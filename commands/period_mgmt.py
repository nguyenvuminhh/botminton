"""
Period management commands (admin-only):
  /new_period, /period_summary, /add_shuttlecock
"""

from datetime import date as dt_date
from telegram import Update
from telegram.ext import ContextTypes

from config import COMMON_GROUP_CHAT_ID
from services.calculations import calculate_period_report
from services.periods import create_period, get_current_period, update_period
from services.shuttlecock_batches import create_batch
from utils.decorator import check_admin_middleware
from utils.messages import get_money_message, get_react_after_sending_money_message
import logging

logger = logging.getLogger(__name__)


@check_admin_middleware
async def new_period(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Usage: /new_period [YYYY-MM-DD]
    Closes the current period (if any) and starts a new one. Defaults to today.
    """
    if not update.effective_chat:
        return

    chat_id = update.effective_chat.id
    start_date_str = context.args[0] if context.args else dt_date.today().isoformat()  # type: ignore

    try:
        dt_date.fromisoformat(start_date_str)
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="❌ Invalid date format. Use YYYY-MM-DD.")
        return

    reply_lines = []

    current = get_current_period()
    if current:
        today = dt_date.today().isoformat()
        update_period(current.start_date.isoformat(), end_date=today)  # type: ignore
        reply_lines.append(f"✅ Closed period {current.start_date} (end: {today}).")  # type: ignore

    period = create_period(start_date=start_date_str)
    if period:
        reply_lines.append(f"✅ New period started on {start_date_str}.")
    else:
        reply_lines.append(f"❌ Could not create period (already exists for {start_date_str}?).")

    await context.bot.send_message(chat_id=chat_id, text="\n".join(reply_lines))


@check_admin_middleware
async def period_summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Calculate and post the money summary for the current period to the group."""
    if not update.effective_chat:
        return

    chat_id = update.effective_chat.id
    period = get_current_period()
    if not period:
        await context.bot.send_message(chat_id=chat_id, text="❌ No active period found.")
        return

    report = calculate_period_report(period.start_date.isoformat())  # type: ignore
    if not report:
        await context.bot.send_message(chat_id=chat_id, text="❌ Could not generate report.")
        return

    message = get_money_message(report)
    await context.bot.send_message(chat_id=COMMON_GROUP_CHAT_ID, text=message)
    await context.bot.send_message(
        chat_id=COMMON_GROUP_CHAT_ID,
        text=get_react_after_sending_money_message()
    )
    await context.bot.send_message(chat_id=chat_id, text="✅ Summary posted to group.")


@check_admin_middleware
async def add_shuttlecock(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Usage: /add_shuttlecock <YYYY-MM-DD> <price> [tube_count]
    Example: /add_shuttlecock 2026-02-23 11.4 12
    """
    if not update.effective_chat:
        return

    chat_id = update.effective_chat.id

    if not context.args or len(context.args) < 2:  # type: ignore
        await context.bot.send_message(
            chat_id=chat_id,
            text="Usage: /add_shuttlecock <YYYY-MM-DD> <price> [tube_count]"
        )
        return

    purchase_date_str = context.args[0]  # type: ignore
    try:
        dt_date.fromisoformat(purchase_date_str)
        total_price = float(context.args[1])  # type: ignore
    except (ValueError, IndexError):
        await context.bot.send_message(chat_id=chat_id, text="❌ Invalid arguments. Date: YYYY-MM-DD, price: number.")
        return

    tube_count = None
    if len(context.args) >= 3:  # type: ignore
        try:
            tube_count = int(context.args[2])  # type: ignore
        except ValueError:
            await context.bot.send_message(chat_id=chat_id, text="❌ tube_count must be an integer.")
            return

    period = get_current_period()
    if not period:
        await context.bot.send_message(chat_id=chat_id, text="❌ No active period.")
        return

    batch = create_batch(
        period_start_date=period.start_date.isoformat(),  # type: ignore
        purchase_date=purchase_date_str,
        total_price=total_price,
        tube_count=tube_count,
    )
    if batch:
        tubes_info = f", {tube_count} tubes" if tube_count else ""
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ Shuttlecock batch {purchase_date_str}: {total_price} €{tubes_info} added to current period."
        )
    else:
        await context.bot.send_message(chat_id=chat_id, text="❌ Failed to add shuttlecock batch.")
