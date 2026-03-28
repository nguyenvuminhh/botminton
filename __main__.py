from commands.admin import add_venue, list_venues, set_schedule
from commands.print_id import print_group_chat_id, print_user_id
from commands.start import test_admin
from commands.payments import confirm_paid, mark_paid, payment_status
from commands.period_mgmt import add_shuttlecock, end_current_and_start_new_period, period_summary
from commands.poll import close_poll, handle_poll_answer, open_poll
from commands.session_mgmt import (
    add_player, add_plus_one, remove_player, remove_plus_one, set_slots, set_venue
)
from config import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_SECRET, WEBHOOK_PORT, ADMIN_USER_ID, LOG_GROUP_CHAT_ID
from utils.telegram_log_handler import TelegramLogHandler
from constants import Commands
from schemas.metadata import Metadata
from utils.database import db_manager
from utils.decorator import upsert_user, user_insertion_middleware
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, PollAnswerHandler, Application, filters, ContextTypes
import logging

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


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    import traceback
    tb = "".join(traceback.format_exception(type(context.error), context.error, context.error.__traceback__))
    msg = f"⚠️ Error: {context.error}\n\n<pre>{tb[-3000:]}</pre>"
    try:
        await context.bot.send_message(chat_id=ADMIN_USER_ID, text=msg, parse_mode="HTML")
    except Exception:
        logger.error(f"Failed to send error to admin: {context.error}")
    logger.error(f"Exception while handling update: {context.error}", exc_info=context.error)


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    cmd = update.message.text or ""
    user = update.effective_user
    chat = update.effective_chat
    sender = f"@{user.username}" if user and user.username else (user.first_name if user else "unknown")
    chat_info = f"chat {chat.id}" if chat else "unknown chat"
    await context.bot.send_message(
        chat_id=ADMIN_USER_ID,
        text=f"⚠️ Unknown command: {cmd}\nFrom: {sender} in {chat_info}"
    )


def run():
    try:
        db_manager.connect()
        Metadata.create()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    if LOG_GROUP_CHAT_ID:
        tg_handler = TelegramLogHandler(BOT_TOKEN, LOG_GROUP_CHAT_ID, level=logging.WARNING)
        tg_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s'))
        logging.getLogger().addHandler(tg_handler)
        logger.info("Telegram log handler active → chat_id=%s", LOG_GROUP_CHAT_ID)

    # Private only — debug + admin config + payment tracking
    register_command(app, Commands.SET_SCHEDULE,    set_schedule,    PRIVATE)
    register_command(app, Commands.PRINT_GROUP_CHAT_ID, print_group_chat_id, filters.ALL)
    register_command(app, Commands.PRINT_USER_ID,       print_user_id,       PRIVATE)
    register_command(app, Commands.TEST_ADMIN,          test_admin,          PRIVATE)
    # Private only — payment tracking
    register_command(app, Commands.PAYMENT_STATUS, payment_status, PRIVATE)
    register_command(app, Commands.MARK_PAID,      mark_paid,      PRIVATE)
    register_command(app, Commands.CONFIRM_PAID,   confirm_paid,   PRIVATE)

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

    app.add_error_handler(error_handler)
    app.add_handler(PollAnswerHandler(handle_poll_answer))
    app.add_handler(MessageHandler(GROUP & filters.ALL, upsert_on_message))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    try:
        if WEBHOOK_URL:
            logger.info(f"Starting in webhook mode on port {WEBHOOK_PORT}")
            app.run_webhook(
                listen="0.0.0.0",
                port=WEBHOOK_PORT,
                url_path=BOT_TOKEN,
                webhook_url=f"{WEBHOOK_URL.rstrip('/')}/{BOT_TOKEN}",
                secret_token=WEBHOOK_SECRET,
            )
        else:
            logger.info("No WEBHOOK_URL set — starting in polling mode")
            app.run_polling()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        db_manager.disconnect()


run()
