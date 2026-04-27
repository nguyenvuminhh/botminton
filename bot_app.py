"""Bot Application factory — shared between webhook mode (FastAPI) and polling mode (__main__)."""
import logging

from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PollAnswerHandler,
    filters,
)

from commands.admin import add_venue, list_venues, set_schedule
from commands.payments import confirm_paid, mark_paid, payment_status
from commands.period_mgmt import add_shuttlecock, end_current_and_start_new_period, period_summary
from commands.poll import close_poll, handle_poll_answer, open_poll
from commands.print_id import print_group_chat_id, print_user_id
from commands.session_mgmt import (
    add_player,
    add_plus_one,
    remove_player,
    remove_plus_one,
    set_slots,
    set_venue,
)
from commands.start import test_admin
from config import ADMIN_USER_ID, BOT_TOKEN, LOG_GROUP_CHAT_ID
from constants import Commands
from utils.decorator import upsert_user, user_insertion_middleware
from utils.operation_log import operation_log_middleware
from utils.telegram_log_handler import TelegramLogHandler

logger = logging.getLogger(__name__)

GROUP   = filters.ChatType.GROUPS
PRIVATE = filters.ChatType.PRIVATE


def _register(app: Application, command: str, handler_func, chat_filter) -> None:
    app.add_handler(CommandHandler(command, operation_log_middleware(user_insertion_middleware(handler_func)), filters=chat_filter))


async def _upsert_on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user:
        upsert_user(update.effective_user)


async def _error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    import traceback
    tb = "".join(traceback.format_exception(type(context.error), context.error, context.error.__traceback__))
    msg = f"⚠️ Error: {context.error}\n\n<pre>{tb[-3000:]}</pre>"
    try:
        await context.bot.send_message(chat_id=ADMIN_USER_ID, text=msg, parse_mode="HTML")
    except Exception:
        logger.error("Failed to send error to admin: %s", context.error)
    logger.error("Exception while handling update: %s", context.error, exc_info=context.error)


async def _unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    cmd = update.message.text or ""
    user = update.effective_user
    chat = update.effective_chat
    sender = f"@{user.username}" if user and user.username else (user.first_name if user else "unknown")
    chat_info = f"chat {chat.id}" if chat else "unknown chat"
    await context.bot.send_message(
        chat_id=ADMIN_USER_ID,
        text=f"⚠️ Unknown command: {cmd}\nFrom: {sender} in {chat_info}",
    )


def build_application() -> Application:
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    if LOG_GROUP_CHAT_ID:
        handler = TelegramLogHandler(BOT_TOKEN, LOG_GROUP_CHAT_ID, level=logging.DEBUG)
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
        logging.getLogger().addHandler(handler)
        logger.info("Telegram log handler active → chat_id=%s", LOG_GROUP_CHAT_ID)

    _register(app, Commands.SET_SCHEDULE,        set_schedule,                     PRIVATE)
    _register(app, Commands.PRINT_GROUP_CHAT_ID, print_group_chat_id,              filters.ALL)
    _register(app, Commands.PRINT_USER_ID,       print_user_id,                    PRIVATE)
    _register(app, Commands.TEST_ADMIN,          test_admin,                       PRIVATE)
    _register(app, Commands.PAYMENT_STATUS,      payment_status,                   PRIVATE)
    _register(app, Commands.MARK_PAID,           mark_paid,                        PRIVATE)
    _register(app, Commands.CONFIRM_PAID,        confirm_paid,                     PRIVATE)
    _register(app, Commands.OPEN_POLL,           open_poll,                        GROUP)
    _register(app, Commands.CLOSE_POLL,          close_poll,                       GROUP)
    _register(app, Commands.ADD_PLAYER,          add_player,                       GROUP)
    _register(app, Commands.REMOVE_PLAYER,       remove_player,                    GROUP)
    _register(app, Commands.ADD_PLUS_ONE,        add_plus_one,                     GROUP)
    _register(app, Commands.REMOVE_PLUS_ONE,     remove_plus_one,                  GROUP)
    _register(app, Commands.SET_SLOTS,           set_slots,                        GROUP)
    _register(app, Commands.SET_VENUE,           set_venue,                        GROUP)
    _register(app, Commands.NEW_PERIOD,          end_current_and_start_new_period, GROUP)
    _register(app, Commands.PERIOD_SUMMARY,      period_summary,                   GROUP)
    _register(app, Commands.ADD_SHUTTLECOCK,     add_shuttlecock,                  GROUP)
    _register(app, Commands.LIST_VENUES,         list_venues,                      GROUP)
    _register(app, Commands.ADD_VENUE,           add_venue,                        GROUP)

    app.add_error_handler(_error_handler)
    app.add_handler(PollAnswerHandler(handle_poll_answer))
    app.add_handler(MessageHandler(GROUP & filters.ALL, _upsert_on_message))
    app.add_handler(MessageHandler(filters.COMMAND, _unknown_command))

    return app
