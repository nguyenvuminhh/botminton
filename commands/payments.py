"""
Payment tracking commands (admin-only, private chat):
  /payment_status, /mark_paid, /confirm_paid
"""

from telegram import Update
from telegram.ext import ContextTypes

from services.period_moneys import list_period_moneys_by_period, mark_as_paid_by_telegram_id
from services.periods import get_last_closed_period
from utils.date import format_to_dd_mm
from utils.decorator import check_admin_middleware
import logging

logger = logging.getLogger(__name__)

_PENDING_KEY = "mark_paid_pending"


def _sorted_records(period_start_date: str):
    """Return period money records sorted by amount descending (deterministic order)."""
    records = list_period_moneys_by_period(period_start_date)
    return sorted(records, key=lambda r: r.amount, reverse=True)  # type: ignore


@check_admin_middleware
async def payment_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show numbered paid/unpaid list for the most recently closed period."""
    if not update.effective_chat:
        return

    chat_id = update.effective_chat.id
    period = get_last_closed_period()
    if not period:
        await context.bot.send_message(chat_id=chat_id, text="❌ No closed period found.")
        return

    records = _sorted_records(period.start_date.isoformat())  # type: ignore
    if not records:
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ No payment records found. Run /period_summary first."
        )
        return

    start_str = format_to_dd_mm(period.start_date)  # type: ignore
    end_str = format_to_dd_mm(period.end_date) if period.end_date else "?"  # type: ignore
    lines = [f"Period {start_str} → {end_str}"]
    for i, rec in enumerate(records, start=1):
        username = rec.user.telegram_user_name if rec.user else "?"  # type: ignore
        paid_icon = "✅" if rec.has_paid else "❌"  # type: ignore
        lines.append(f"{i}. {username} — {rec.amount:.2f} {paid_icon}")  # type: ignore

    await context.bot.send_message(chat_id=chat_id, text="\n".join(lines))


@check_admin_middleware
async def mark_paid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Preview players to mark as paid by index, then ask for /confirm_paid."""
    if not update.effective_chat:
        return

    chat_id = update.effective_chat.id

    if not context.args:  # type: ignore
        await context.bot.send_message(
            chat_id=chat_id,
            text="Usage: /mark_paid 1 3 5\nRun /payment_status first to see the index."
        )
        return

    period = get_last_closed_period()
    if not period:
        await context.bot.send_message(chat_id=chat_id, text="❌ No closed period found.")
        return

    records = _sorted_records(period.start_date.isoformat())  # type: ignore
    if not records:
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ No payment records found. Run /period_summary first."
        )
        return

    try:
        indices = [int(a) for a in context.args]  # type: ignore
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="❌ Indices must be integers.")
        return

    selected = []
    invalid = []
    for idx in indices:
        if 1 <= idx <= len(records):
            selected.append((idx, records[idx - 1]))
        else:
            invalid.append(idx)

    if invalid:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"❌ Invalid indices: {', '.join(str(i) for i in invalid)} (valid: 1–{len(records)})"
        )
        return

    lines = ["Mark these as paid?"]
    for _, rec in selected:
        username = rec.user.telegram_user_name if rec.user else "?"  # type: ignore
        lines.append(f"• {username} ({rec.amount:.2f})")  # type: ignore
    lines.append("\nReply /confirm_paid to confirm.")

    # Store pending state: period + list of telegram_ids
    context.user_data[_PENDING_KEY] = {  # type: ignore
        "period_start_date": period.start_date.isoformat(),  # type: ignore
        "telegram_ids": [rec.user.telegram_id for _, rec in selected],  # type: ignore
    }

    await context.bot.send_message(chat_id=chat_id, text="\n".join(lines))


@check_admin_middleware
async def confirm_paid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Confirm the pending /mark_paid action."""
    if not update.effective_chat:
        return

    chat_id = update.effective_chat.id
    pending = context.user_data.get(_PENDING_KEY)  # type: ignore
    if not pending:
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ No pending /mark_paid. Run /mark_paid <indices> first."
        )
        return

    period_start_date = pending["period_start_date"]
    telegram_ids = pending["telegram_ids"]
    del context.user_data[_PENDING_KEY]  # type: ignore

    succeeded = []
    failed = []
    for tid in telegram_ids:
        result = mark_as_paid_by_telegram_id(period_start_date, tid)
        if result:
            username = result.user.telegram_user_name if result.user else tid  # type: ignore
            succeeded.append(username)
        else:
            failed.append(tid)

    lines = []
    if succeeded:
        lines.append("✅ Marked as paid: " + ", ".join(succeeded))
    if failed:
        lines.append("❌ Failed: " + ", ".join(failed))

    await context.bot.send_message(chat_id=chat_id, text="\n".join(lines))
