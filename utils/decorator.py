from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from services.users import create_user, get_user, update_user
from utils.user import check_admin


def upsert_user(telegram_user) -> None:
    """Create or update a user record from a Telegram User object."""
    telegram_id = str(telegram_user.id)
    username = telegram_user.username or telegram_user.first_name
    if not get_user(telegram_id):
        create_user(telegram_id=telegram_id, telegram_user_name=username)
    else:
        update_user(telegram_id, telegram_user_name=username, is_admin=check_admin(telegram_id))


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

        await context.bot.send_message(
            chat_id=chat.id,
            text="❌ You are not authorized to use this command."
        )

    return wrapper
