from telegram import Update
from telegram.ext import ContextTypes

from utils.decorator import check_admin_middleware

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    await update.message.reply_text("Hii")

@check_admin_middleware
async def test_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    await update.message.reply_text("You are an admin")