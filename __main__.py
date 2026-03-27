from commands.admin import add_venue, list_venues
from commands.payments import confirm_paid, mark_paid, payment_status
from commands.period_mgmt import add_shuttlecock, end_current_and_start_new_period, period_summary
from commands.poll import close_poll, handle_poll_answer, open_poll
from commands.print_id import print_group_chat_id, print_user_id
from commands.session_mgmt import (
    add_player, add_plus_one, remove_player, remove_plus_one, set_slots, set_venue
)
from commands.start import test_admin
from config import BOT_TOKEN
from constants import Commands
from schemas.metadata import Metadata
from utils.database import db_manager
from utils.decorator import upsert_user
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, PollAnswerHandler, Application, filters, ContextTypes
import logging

from utils.decorator import user_insertion_middleware

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

GROUP   = filters.ChatType.GROUPS
PRIVATE = filters.ChatType.PRIVATE


def register_command(app: Application, command: str, handler_func, chat_filter):
    wrapped = user_insertion_middleware(handler_func)
    app.add_handler(CommandHandler(command, wrapped, filters=chat_filter))


async def upsert_on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user:
        upsert_user(update.effective_user)


def run():
    try:
        db_manager.connect()
        Metadata.create()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Private only (debug/utility + payment tracking)
    register_command(app, Commands.PRINT_GROUP_CHAT_ID, print_group_chat_id, PRIVATE)
    register_command(app, Commands.PRINT_USER_ID,       print_user_id,       PRIVATE)
    register_command(app, Commands.TEST_ADMIN,          test_admin,          PRIVATE)
    register_command(app, Commands.PAYMENT_STATUS,      payment_status,      PRIVATE)
    register_command(app, Commands.MARK_PAID,           mark_paid,           PRIVATE)
    register_command(app, Commands.CONFIRM_PAID,        confirm_paid,        PRIVATE)

    # Group only — all functional commands
    register_command(app, Commands.OPEN_POLL,       open_poll,       GROUP)
    register_command(app, Commands.CLOSE_POLL,      close_poll,      GROUP)
    register_command(app, Commands.ADD_PLAYER,      add_player,      GROUP)
    register_command(app, Commands.REMOVE_PLAYER,   remove_player,   GROUP)
    register_command(app, Commands.ADD_PLUS_ONE,    add_plus_one,    GROUP)
    register_command(app, Commands.REMOVE_PLUS_ONE, remove_plus_one, GROUP)
    register_command(app, Commands.SET_SLOTS,       set_slots,       GROUP)
    register_command(app, Commands.SET_VENUE,       set_venue,       GROUP)
    register_command(app, Commands.NEW_PERIOD,      end_current_and_start_new_period, GROUP)
    register_command(app, Commands.PERIOD_SUMMARY,  period_summary,  GROUP)
    register_command(app, Commands.ADD_SHUTTLECOCK, add_shuttlecock, GROUP)
    register_command(app, Commands.LIST_VENUES,     list_venues,     GROUP)
    register_command(app, Commands.ADD_VENUE,       add_venue,       GROUP)

    # Poll answer handler (tracks individual votes for non-anonymous polls)
    app.add_handler(PollAnswerHandler(handle_poll_answer))

    # Catch-all: upsert any group member who sends a message
    app.add_handler(MessageHandler(GROUP & filters.ALL, upsert_on_message))

    try:
        app.run_polling()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        db_manager.disconnect()


if __name__ == "__main__":
    run()
