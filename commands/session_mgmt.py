"""
Session management commands (admin-only):
  /add_player, /remove_player, /add_plus_one, /remove_plus_one, /set_slots, /set_venue
"""

from telegram import Update
from telegram.ext import ContextTypes

from services.session_participants import (
    create_participant,
    delete_participant_by_user_and_session,
    get_participant_by_user_and_session,
    update_additional_participants,
)
from services.metadata import update_metadata
from services.sessions import get_open_session, update_session
from services.users import get_user_by_username
from services.venues import get_venue_by_name
from utils.decorator import check_admin_middleware
import logging

logger = logging.getLogger(__name__)


def _get_open_session_or_reply(context, chat_id):
    """Helper: return open session or None (and send error message)."""
    session = get_open_session()
    return session


async def _resolve_user(context, chat_id: int, username: str):
    """Look up a DB user by @username, sending an error if not found."""
    user = get_user_by_username(username)
    if not user:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"❌ User '{username}' not found in database. They need to send /start first."
        )
    return user


@check_admin_middleware
async def add_player(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Usage: /add_player @username"""
    if not update.effective_chat or not context.args:
        await update.message.reply_text("Usage: /add_player @username")  # type: ignore
        return

    chat_id = update.effective_chat.id
    username = context.args[0]

    session = get_open_session()
    if not session:
        await context.bot.send_message(chat_id=chat_id, text="❌ No open session/poll.")
        return

    user = await _resolve_user(context, chat_id, username)
    if not user:
        return

    session_date = session.date.isoformat()  # type: ignore
    result = create_participant(user_telegram_id=str(user.telegram_id), session_date=session_date)  # type: ignore
    if result:
        await context.bot.send_message(chat_id=chat_id, text=f"✅ Added {username} to session {session_date}.")
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Could not add {username} (already in session?).")


@check_admin_middleware
async def remove_player(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Usage: /remove_player @username"""
    if not update.effective_chat or not context.args:
        await update.message.reply_text("Usage: /remove_player @username")  # type: ignore
        return

    chat_id = update.effective_chat.id
    username = context.args[0]

    session = get_open_session()
    if not session:
        await context.bot.send_message(chat_id=chat_id, text="❌ No open session/poll.")
        return

    user = await _resolve_user(context, chat_id, username)
    if not user:
        return

    session_date = session.date.isoformat()  # type: ignore
    ok = delete_participant_by_user_and_session(
        user_telegram_id=str(user.telegram_id), session_date=session_date  # type: ignore
    )
    if ok:
        await context.bot.send_message(chat_id=chat_id, text=f"✅ Removed {username} from session {session_date}.")
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ {username} was not in the session.")


@check_admin_middleware
async def add_plus_one(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Usage: /add_plus_one @username"""
    if not update.effective_chat or not context.args:
        await update.message.reply_text("Usage: /add_plus_one @username")  # type: ignore
        return

    chat_id = update.effective_chat.id
    username = context.args[0]

    session = get_open_session()
    if not session:
        await context.bot.send_message(chat_id=chat_id, text="❌ No open session/poll.")
        return

    user = await _resolve_user(context, chat_id, username)
    if not user:
        return

    session_date = session.date.isoformat()  # type: ignore
    tid = str(user.telegram_id)  # type: ignore
    participant = get_participant_by_user_and_session(tid, session_date)
    if not participant:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ {username} is not in the session yet.")
        return

    current = participant.additional_participants or 0  # type: ignore
    update_additional_participants(tid, session_date, current + 1)
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"✅ {username} now has {current + 1} plus-one(s) for {session_date}."
    )


@check_admin_middleware
async def remove_plus_one(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Usage: /remove_plus_one @username"""
    if not update.effective_chat or not context.args:
        await update.message.reply_text("Usage: /remove_plus_one @username")  # type: ignore
        return

    chat_id = update.effective_chat.id
    username = context.args[0]

    session = get_open_session()
    if not session:
        await context.bot.send_message(chat_id=chat_id, text="❌ No open session/poll.")
        return

    user = await _resolve_user(context, chat_id, username)
    if not user:
        return

    session_date = session.date.isoformat()  # type: ignore
    tid = str(user.telegram_id)  # type: ignore
    participant = get_participant_by_user_and_session(tid, session_date)
    if not participant:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ {username} is not in the session.")
        return

    current = participant.additional_participants or 0  # type: ignore
    new_count = max(0, current - 1)
    update_additional_participants(tid, session_date, new_count)
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"✅ {username} now has {new_count} plus-one(s) for {session_date}."
    )


@check_admin_middleware
async def set_slots(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Usage: /set_slots <float>  — e.g. /set_slots 6.0"""
    if not update.effective_chat or not context.args:
        await update.message.reply_text("Usage: /set_slots <number>  e.g. /set_slots 6.0")  # type: ignore
        return

    chat_id = update.effective_chat.id

    try:
        slots = float(context.args[0])
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="❌ Invalid number for slots.")
        return

    session = get_open_session()
    if not session:
        await context.bot.send_message(chat_id=chat_id, text="❌ No open session/poll.")
        return

    session_date = session.date.isoformat()  # type: ignore
    update_session(session_date, slots=slots)
    await context.bot.send_message(chat_id=chat_id, text=f"✅ Session {session_date}: slots set to {slots}.")


@check_admin_middleware
async def set_venue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Usage: /set_venue <venue name>"""
    if not update.effective_chat or not context.args:
        await update.message.reply_text("Usage: /set_venue <venue name>")  # type: ignore
        return

    chat_id = update.effective_chat.id
    venue_name = " ".join(context.args)

    venue = get_venue_by_name(venue_name)
    if not venue:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"❌ Venue '{venue_name}' not found. Use /list_venues or /add_venue."
        )
        return

    session = get_open_session()
    if not session:
        await context.bot.send_message(chat_id=chat_id, text="❌ No open session/poll.")
        return

    session_date = session.date.isoformat()  # type: ignore
    update_session(session_date, venue=str(venue.id))  # type: ignore
    update_metadata(default_venue_id=str(venue.id))  # type: ignore
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"✅ Session {session_date}: venue set to '{venue_name}' ({venue.price_per_slot} €/slot). Saved as default."  # type: ignore
    )
