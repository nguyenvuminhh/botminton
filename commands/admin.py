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

    user_id = update.effective_user.id if update.effective_user else "unknown"
    logger.info("list_venues called by user_id=%s", user_id)

    venues = list_all_venues()
    if not venues:
        logger.info("list_venues: no venues found")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="No venues registered. Use /add_venue to add one."
        )
        return

    logger.info("list_venues: returning %d venue(s)", len(venues))
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
    user_id = update.effective_user.id if update.effective_user else "unknown"
    logger.info("add_venue called by user_id=%s args=%s", user_id, context.args)

    if not context.args or len(context.args) < 3:  # type: ignore
        logger.warning("add_venue: insufficient args from user_id=%s", user_id)
        await context.bot.send_message(
            chat_id=chat_id,
            text="Usage: /add_venue <price> <location> <name...>\nExample: /add_venue 10.0 Unisport Unisport student"
        )
        return

    try:
        price = float(context.args[0])  # type: ignore
    except ValueError:
        logger.warning("add_venue: invalid price '%s' from user_id=%s", context.args[0], user_id)  # type: ignore
        await context.bot.send_message(chat_id=chat_id, text="❌ Price must be a number.")
        return

    location = context.args[1]  # type: ignore
    name = " ".join(context.args[2:])  # type: ignore

    logger.debug("add_venue: creating venue name=%r location=%r price=%s", name, location, price)
    venue = create_venue(name=name, location=location, price_per_slot=price)
    if venue:
        logger.info("add_venue: created venue name=%r price=%s", name, price)
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ Venue '{name}' at {location} ({price} €/slot) added."
        )
    else:
        logger.error("add_venue: failed to create venue name=%r (already exists?)", name)
        await context.bot.send_message(chat_id=chat_id, text="❌ Failed to add venue (name already exists?).")


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
    user_id = update.effective_user.id if update.effective_user else "unknown"
    logger.info("set_schedule called by user_id=%s args=%s", user_id, context.args)

    if not context.args or len(context.args) < 2:  # type: ignore
        metadata = get_metadata()
        if metadata:
            day_name = _DAY_NAMES[metadata.default_day_of_the_week_index].capitalize()  # type: ignore
            current = f"{metadata.default_start_time} – {metadata.default_end_time}, {day_name}"  # type: ignore
        else:
            current = "unknown"
        logger.info("set_schedule: no args, showing current schedule: %s", current)
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
                logger.warning("set_schedule: invalid day arg '%s' from user_id=%s", day_arg, user_id)
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="❌ Invalid day. Use mon/tue/wed/thu/fri/sat/sun or 0–6."
                )
                return

    logger.debug("set_schedule: updating start=%s end=%s day_index=%s", start_time, end_time, day_index)
    update_metadata(default_start_time=start_time, default_end_time=end_time, default_day_of_the_week_index=day_index)
    day_str = f", {_DAY_NAMES[day_index].capitalize()}" if day_index is not None else ""
    logger.info("set_schedule: updated schedule to %s – %s%s", start_time, end_time, day_str)
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"✅ Schedule updated: {start_time} – {end_time}{day_str}."
    )
