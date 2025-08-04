from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from services.users import create_user, get_user, update_user
from utils.user import check_admin

# ✅ Decorator: Insert user if not exists
def user_insertion_middleware(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if not user:
            return

        user_telegram_id = str(user.id)
        existing_user = get_user(user_telegram_id)

        if not existing_user:
            create_user(
                telegram_id=user_telegram_id,
                telegram_user_name=user.username or user.first_name,
            )
        else:
            update_user(
                user_telegram_id,
                telegram_user_name=user.username or user.first_name,
                is_admin=check_admin(user_telegram_id)
            )


        return await func(update, context)

    return wrapper

# ✅ Decorator: Allow only admins
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
