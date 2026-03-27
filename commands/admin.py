"""
Venue management commands (admin-only):
  /list_venues, /add_venue
"""

from telegram import Update
from telegram.ext import ContextTypes

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
