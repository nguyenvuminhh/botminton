import logging

from telegram import Update
from telegram.ext import ContextTypes

from utils.decorator import check_admin_middleware

logger = logging.getLogger(__name__)


@check_admin_middleware
async def test_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id if update.effective_user else "unknown"
    logger.info("test_admin called by user_id=%s", user_id)
    if not update.message:
        return
    await update.message.reply_text("You are an admin")
