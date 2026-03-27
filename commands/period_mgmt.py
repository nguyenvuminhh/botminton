"""
Period management commands (admin-only):
  /end_current_and_start_new_period, /period_summary, /add_shuttlecock
"""

from datetime import date as dt_date
from telegram import Update
from telegram.ext import ContextTypes

from config import COMMON_GROUP_CHAT_ID
from services.calculations import calculate_period_report
from services.period_moneys import upsert_period_money
from services.periods import create_period, get_current_period, update_period
from services.shuttlecock_batches import create_batch
from utils.decorator import check_admin_middleware
from utils.messages import get_money_message, get_react_after_sending_money_message
import logging

logger = logging.getLogger(__name__)


@check_admin_middleware
async def end_current_and_start_new_period(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Usage: /end_current_and_start_new_period [YYYY-MM-DD]
    Posts the period summary to the group, closes the current period, then starts a new one. Defaults to today.
    """
    if not update.effective_chat:
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id if update.effective_user else "unknown"
    start_date_str = context.args[0] if context.args else dt_date.today().isoformat()  # type: ignore
    logger.info("end_current_and_start_new_period called by user_id=%s start_date=%s", user_id, start_date_str)

    try:
        dt_date.fromisoformat(start_date_str)
    except ValueError:
        logger.warning("end_current_and_start_new_period: invalid date '%s' from user_id=%s", start_date_str, user_id)
        await context.bot.send_message(chat_id=chat_id, text="❌ Invalid date format. Use YYYY-MM-DD.")
        return

    reply_lines = []

    current = get_current_period()
    if current:
        logger.info("end_current_and_start_new_period: found current period=%s, generating summary", current.start_date)  # type: ignore
        # Post summary before closing
        report = calculate_period_report(current.start_date.isoformat())  # type: ignore
        if report:
            logger.info("end_current_and_start_new_period: report generated with %d entries", len(report.personal_period_money))
            for entry in report.personal_period_money:
                upsert_period_money(current.start_date.isoformat(), entry.person_id, entry.period_money)  # type: ignore
            message = get_money_message(report)
            await context.bot.send_message(chat_id=COMMON_GROUP_CHAT_ID, text=message)
            await context.bot.send_message(
                chat_id=COMMON_GROUP_CHAT_ID,
                text=get_react_after_sending_money_message()
            )
            logger.info("end_current_and_start_new_period: summary posted to group")
            reply_lines.append("✅ Summary posted to group.")
        else:
            logger.warning("end_current_and_start_new_period: could not generate report for period=%s", current.start_date)  # type: ignore
            reply_lines.append("⚠️ Could not generate summary (no data?).")

        today = dt_date.today().isoformat()
        update_period(current.start_date.isoformat(), end_date=today)  # type: ignore
        logger.info("end_current_and_start_new_period: closed period=%s end_date=%s", current.start_date, today)  # type: ignore
        reply_lines.append(f"✅ Closed period {current.start_date} (end: {today}).")  # type: ignore
    else:
        logger.info("end_current_and_start_new_period: no current period to close")

    period = create_period(start_date=start_date_str)
    if period:
        logger.info("end_current_and_start_new_period: new period created start_date=%s", start_date_str)
        reply_lines.append(f"✅ New period started on {start_date_str}.")
    else:
        logger.error("end_current_and_start_new_period: failed to create period start_date=%s (already exists?)", start_date_str)
        reply_lines.append(f"❌ Could not create period (already exists for {start_date_str}?).")

    await context.bot.send_message(chat_id=chat_id, text="\n".join(reply_lines))


@check_admin_middleware
async def period_summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Calculate and post the money summary for the current period to the group."""
    if not update.effective_chat:
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id if update.effective_user else "unknown"
    logger.info("period_summary called by user_id=%s", user_id)

    period = get_current_period()
    if not period:
        logger.warning("period_summary: no active period found")
        await context.bot.send_message(chat_id=chat_id, text="❌ No active period found.")
        return

    logger.info("period_summary: generating report for period=%s", period.start_date)  # type: ignore
    report = calculate_period_report(period.start_date.isoformat())  # type: ignore
    if not report:
        logger.error("period_summary: failed to generate report for period=%s", period.start_date)  # type: ignore
        await context.bot.send_message(chat_id=chat_id, text="❌ Could not generate report.")
        return

    logger.info("period_summary: report generated with %d entries, upserting period moneys", len(report.personal_period_money))
    for entry in report.personal_period_money:
        upsert_period_money(period.start_date.isoformat(), entry.person_id, entry.period_money)  # type: ignore

    message = get_money_message(report)
    await context.bot.send_message(chat_id=COMMON_GROUP_CHAT_ID, text=message)
    await context.bot.send_message(
        chat_id=COMMON_GROUP_CHAT_ID,
        text=get_react_after_sending_money_message()
    )
    logger.info("period_summary: summary posted to group for period=%s", period.start_date)  # type: ignore
    await context.bot.send_message(chat_id=chat_id, text="✅ Summary posted to group.")


@check_admin_middleware
async def add_shuttlecock(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Usage: /add_shuttlecock <price1> [price2] [price3] ...
    Example: /add_shuttlecock 11.4 11.4 12.0
    Each argument is the price of one tube. Total and tube count are derived automatically.
    """
    if not update.effective_chat:
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id if update.effective_user else "unknown"
    logger.info("add_shuttlecock called by user_id=%s args=%s", user_id, context.args)

    if not context.args:  # type: ignore
        logger.warning("add_shuttlecock: no args from user_id=%s", user_id)
        await context.bot.send_message(
            chat_id=chat_id,
            text="Usage: /add_shuttlecock <price1> [price2] ...\nExample: /add_shuttlecock 11.4 11.4 12.0"
        )
        return

    try:
        tube_prices = [float(a) for a in context.args]  # type: ignore
    except ValueError:
        logger.warning("add_shuttlecock: invalid price args=%s from user_id=%s", context.args, user_id)
        await context.bot.send_message(chat_id=chat_id, text="❌ All arguments must be numbers (one price per tube).")
        return

    total_price = sum(tube_prices)
    tube_count = len(tube_prices)
    purchase_date_str = dt_date.today().isoformat()
    logger.debug("add_shuttlecock: tube_count=%d total_price=%.2f purchase_date=%s", tube_count, total_price, purchase_date_str)

    period = get_current_period()
    if not period:
        logger.warning("add_shuttlecock: no active period")
        await context.bot.send_message(chat_id=chat_id, text="❌ No active period.")
        return

    batch = create_batch(
        period_start_date=period.start_date.isoformat(),  # type: ignore
        purchase_date=purchase_date_str,
        total_price=total_price,
        tube_count=tube_count,
    )
    if batch:
        logger.info("add_shuttlecock: batch created tube_count=%d total=%.2f period=%s", tube_count, total_price, period.start_date)  # type: ignore
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ {tube_count} tube(s) added: {total_price:.2f} € total."
        )
    else:
        logger.error("add_shuttlecock: failed to create batch for period=%s", period.start_date)  # type: ignore
        await context.bot.send_message(chat_id=chat_id, text="❌ Failed to add shuttlecock batch.")
