"""
Venue management commands (admin-only):
  /list_venues, /add_venue, /setschedule
"""

from telegram import Update
from telegram.ext import ContextTypes

from services.metadata import get_metadata, update_metadata
from services.venues import create_venue, list_all_venues
from utils.decorator import check_admin_middleware
import logging

logger = logging.getLogger(__name__)


@check_admin_middleware
async def list_venues(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all registered venues with their price per slot."""
    if not update.effective_chat:
        return

    venues = list_all_venues()
    if not venues:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="No venues registered. Use /add_venue to add one."
        )
        return

    lines = ["Venues:"]
    for v in venues:
        location = f" ({v.location})" if v.location else ""  # type: ignore
        lines.append(f"• {v.name}{location} — {v.price_per_slot} €/slot")  # type: ignore
    await context.bot.send_message(chat_id=update.effective_chat.id, text="\n".join(lines))


@check_admin_middleware
async def add_venue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Usage: /add_venue <price> <location> <name...>
    Example: /add_venue 10.0 Unisport Unisport student
    """
    if not update.effective_chat:
        return

    chat_id = update.effective_chat.id

    if not context.args or len(context.args) < 3:  # type: ignore
        await context.bot.send_message(
            chat_id=chat_id,
            text="Usage: /add_venue <price> <location> <name...>\nExample: /add_venue 10.0 Unisport Unisport student"
        )
        return

    try:
        price = float(context.args[0])  # type: ignore
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="❌ Price must be a number.")
        return

    location = context.args[1]  # type: ignore
    name = " ".join(context.args[2:])  # type: ignore

    venue = create_venue(name=name, location=location, price_per_slot=price)
    if venue:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ Venue '{name}' at {location} ({price} €/slot) added."
        )
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Failed to add venue (name already exists?).")


_DAY_NAMES = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
_DAY_ABBREVS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


@check_admin_middleware
async def set_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Usage: /setschedule <start_time> <end_time> [day]
    Day can be mon/tue/wed/thu/fri/sat/sun, full name, or index (0=Mon, 6=Sun).
    Example: /setschedule 20:30 22:00 fri
    """
    if not update.effective_chat:
        return

    chat_id = update.effective_chat.id

    if not context.args or len(context.args) < 2:  # type: ignore
        metadata = get_metadata()
        if metadata:
            day_name = _DAY_NAMES[metadata.default_day_of_the_week_index].capitalize()  # type: ignore
            current = f"{metadata.default_start_time} – {metadata.default_end_time}, {day_name}"  # type: ignore
        else:
            current = "unknown"
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Current schedule: {current}\nUsage: /setschedule <start> <end> [day]\nExample: /setschedule 20:30 22:00 fri"
        )
        return

    start_time = context.args[0]  # type: ignore
    end_time = context.args[1]  # type: ignore
    day_index = None

    if len(context.args) >= 3:  # type: ignore
        day_arg = context.args[2].lower()  # type: ignore
        if day_arg in _DAY_NAMES:
            day_index = _DAY_NAMES.index(day_arg)
        elif day_arg in _DAY_ABBREVS:
            day_index = _DAY_ABBREVS.index(day_arg)
        else:
            try:
                day_index = int(day_arg)
                if not 0 <= day_index <= 6:
                    raise ValueError
            except ValueError:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="❌ Invalid day. Use mon/tue/wed/thu/fri/sat/sun or 0–6."
                )
                return

    update_metadata(default_start_time=start_time, default_end_time=end_time, default_day_of_the_week_index=day_index)
    day_str = f", {_DAY_NAMES[day_index].capitalize()}" if day_index is not None else ""
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"✅ Schedule updated: {start_time} – {end_time}{day_str}."
    )
