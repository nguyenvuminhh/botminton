import logging
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from config import LOG_GROUP_CHAT_ID
from services.users import create_user, get_user, update_user
from utils.user import check_admin

logger = logging.getLogger(__name__)


def upsert_user(telegram_user) -> None:
    """Create or update a user record from a Telegram User object."""
    telegram_id = str(telegram_user.id)
    username = telegram_user.username or telegram_user.first_name
    full_name = telegram_user.first_name
    if telegram_user.last_name:
        full_name += f" {telegram_user.last_name}"
    if not get_user(telegram_id):
        create_user(telegram_id=telegram_id, telegram_user_name=username, full_name=full_name)
    else:
        update_user(telegram_id, telegram_user_name=username, full_name=full_name, is_admin=check_admin(telegram_id))


def user_insertion_middleware(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if not user:
            return
        upsert_user(user)
        return await func(update, context)
    return wrapper


def check_admin_middleware(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        chat = update.effective_chat
        if not user or not chat:
            return

        db_user = get_user(str(user.id))
        if not db_user:
            await context.bot.send_message(
                chat_id=chat.id,
                text="User not found."
            )
            return

        if db_user.is_admin:
            return await func(update, context)

        cmd = update.message.text if update.message else "unknown"
        sender = f"@{user.username}" if user.username else user.first_name
        logger.warning("Unauthorized command attempt: %s from %s (id=%s)", cmd, sender, user.id)
        if LOG_GROUP_CHAT_ID:
            await context.bot.send_message(
                chat_id=LOG_GROUP_CHAT_ID,
                text=f"⚠️ Unauthorized command: {cmd}\nFrom: {sender} (id: {user.id})",
            )

    return wrapper
