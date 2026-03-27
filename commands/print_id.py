from telegram import Update
from telegram.ext import ContextTypes

from utils.user import check_admin

async def print_group_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_chat = update.effective_chat
    if not group_chat or not group_chat.id:
        if not update.message:
            return
        await update.message.reply_text("This command can only be used in a group chat.")
        return
    await context.bot.send_message(chat_id=group_chat.id, text=f"Group Chat ID: {group_chat.id}")

async def print_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_chat = update.effective_chat
    if not group_chat or not group_chat.id:
        if not update.message:
            return
        await update.message.reply_text("This command can only be used in a group chat.")
        return

    user = update.effective_user
    if not user or not user.id:
        if not update.message:
            return
        await update.message.reply_text("This command can only be used in a private chat.")
        return

    is_admin = check_admin(user.id)
    await context.bot.send_message(chat_id=group_chat.id, text=f"Your User ID: {user.id}. You are {'an admin' if is_admin else 'not an admin'}.")
