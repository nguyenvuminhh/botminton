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
        logger.warning("_resolve_user: user '%s' not found", username)
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"❌ '{username}' not found or ambiguous. Use their @username or first name exactly as it appears in the group."
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
    user_id = update.effective_user.id if update.effective_user else "unknown"
    logger.info("add_player called by user_id=%s target_username=%s", user_id, username)

    session = get_open_session()
    if not session:
        logger.warning("add_player: no open session")
        await context.bot.send_message(chat_id=chat_id, text="❌ No open session/poll.")
        return

    user = await _resolve_user(context, chat_id, username)
    if not user:
        return

    session_date = session.date.isoformat()  # type: ignore
    result = create_participant(user_telegram_id=str(user.telegram_id), session_date=session_date)  # type: ignore
    if result:
        logger.info("add_player: added username=%s to session=%s", username, session_date)
        await context.bot.send_message(chat_id=chat_id, text=f"✅ Added {username} to session {session_date}.")
    else:
        logger.warning("add_player: failed to add username=%s to session=%s (already in session?)", username, session_date)
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Could not add {username} (already in session?).")


@check_admin_middleware
async def remove_player(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Usage: /remove_player @username"""
    if not update.effective_chat or not context.args:
        await update.message.reply_text("Usage: /remove_player @username")  # type: ignore
        return

    chat_id = update.effective_chat.id
    username = context.args[0]
    user_id = update.effective_user.id if update.effective_user else "unknown"
    logger.info("remove_player called by user_id=%s target_username=%s", user_id, username)

    session = get_open_session()
    if not session:
        logger.warning("remove_player: no open session")
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
        logger.info("remove_player: removed username=%s from session=%s", username, session_date)
        await context.bot.send_message(chat_id=chat_id, text=f"✅ Removed {username} from session {session_date}.")
    else:
        logger.warning("remove_player: username=%s was not in session=%s", username, session_date)
        await context.bot.send_message(chat_id=chat_id, text=f"❌ {username} was not in the session.")


@check_admin_middleware
async def add_plus_one(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Usage: /add_plus_one @username"""
    if not update.effective_chat or not context.args:
        await update.message.reply_text("Usage: /add_plus_one @username")  # type: ignore
        return

    chat_id = update.effective_chat.id
    username = context.args[0]
    user_id = update.effective_user.id if update.effective_user else "unknown"
    logger.info("add_plus_one called by user_id=%s target_username=%s", user_id, username)

    session = get_open_session()
    if not session:
        logger.warning("add_plus_one: no open session")
        await context.bot.send_message(chat_id=chat_id, text="❌ No open session/poll.")
        return

    user = await _resolve_user(context, chat_id, username)
    if not user:
        return

    session_date = session.date.isoformat()  # type: ignore
    tid = str(user.telegram_id)  # type: ignore
    participant = get_participant_by_user_and_session(tid, session_date)
    if not participant:
        logger.warning("add_plus_one: username=%s not in session=%s", username, session_date)
        await context.bot.send_message(chat_id=chat_id, text=f"❌ {username} is not in the session yet.")
        return

    current = participant.additional_participants or 0  # type: ignore
    new_count = current + 1
    update_additional_participants(tid, session_date, new_count)
    logger.info("add_plus_one: username=%s plus_ones=%d->%d session=%s", username, current, new_count, session_date)
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"✅ {username} now has {new_count} plus-one(s) for {session_date}."
    )


@check_admin_middleware
async def remove_plus_one(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Usage: /remove_plus_one @username"""
    if not update.effective_chat or not context.args:
        await update.message.reply_text("Usage: /remove_plus_one @username")  # type: ignore
        return

    chat_id = update.effective_chat.id
    username = context.args[0]
    user_id = update.effective_user.id if update.effective_user else "unknown"
    logger.info("remove_plus_one called by user_id=%s target_username=%s", user_id, username)

    session = get_open_session()
    if not session:
        logger.warning("remove_plus_one: no open session")
        await context.bot.send_message(chat_id=chat_id, text="❌ No open session/poll.")
        return

    user = await _resolve_user(context, chat_id, username)
    if not user:
        return

    session_date = session.date.isoformat()  # type: ignore
    tid = str(user.telegram_id)  # type: ignore
    participant = get_participant_by_user_and_session(tid, session_date)
    if not participant:
        logger.warning("remove_plus_one: username=%s not in session=%s", username, session_date)
        await context.bot.send_message(chat_id=chat_id, text=f"❌ {username} is not in the session.")
        return

    current = participant.additional_participants or 0  # type: ignore
    new_count = max(0, current - 1)
    update_additional_participants(tid, session_date, new_count)
    logger.info("remove_plus_one: username=%s plus_ones=%d->%d session=%s", username, current, new_count, session_date)
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"✅ {username} now has {new_count} plus-one(s) for {session_date}."
    )


@check_admin_middleware
async def set_slots(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Usage: /set_slots <float>  — e.g. /set_slots 6.0"""
    if not update.effective_chat or not context.args:
        await update.message.reply_text("Usage: /set_slots <number>  e.g. /set_slots 6.0 (courts × hours)")  # type: ignore
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id if update.effective_user else "unknown"
    logger.info("set_slots called by user_id=%s args=%s", user_id, context.args)

    try:
        slots = float(context.args[0])
    except ValueError:
        logger.warning("set_slots: invalid slots value '%s' from user_id=%s", context.args[0], user_id)
        await context.bot.send_message(chat_id=chat_id, text="❌ Invalid number for court slots.")
        return

    session = get_open_session()
    if not session:
        logger.warning("set_slots: no open session")
        await context.bot.send_message(chat_id=chat_id, text="❌ No open session/poll.")
        return

    session_date = session.date.isoformat()  # type: ignore
    update_session(session_date, slots=slots)
    logger.info("set_slots: session=%s slots set to %s", session_date, slots)
    await context.bot.send_message(chat_id=chat_id, text=f"✅ Session {session_date}: court slots set to {slots}.")


@check_admin_middleware
async def set_venue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Usage: /set_venue <venue name>"""
    if not update.effective_chat or not context.args:
        await update.message.reply_text("Usage: /set_venue <venue name>")  # type: ignore
        return

    chat_id = update.effective_chat.id
    venue_name = " ".join(context.args)
    user_id = update.effective_user.id if update.effective_user else "unknown"
    logger.info("set_venue called by user_id=%s venue_name=%r", user_id, venue_name)

    venue = get_venue_by_name(venue_name)
    if not venue:
        logger.warning("set_venue: venue '%s' not found", venue_name)
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"❌ Venue '{venue_name}' not found. Use /list_venues or /add_venue."
        )
        return

    session = get_open_session()
    if not session:
        logger.warning("set_venue: no open session")
        await context.bot.send_message(chat_id=chat_id, text="❌ No open session/poll.")
        return

    session_date = session.date.isoformat()  # type: ignore
    update_session(session_date, venue=str(venue.id))  # type: ignore
    update_metadata(default_venue_id=str(venue.id))  # type: ignore
    logger.info("set_venue: session=%s venue set to '%s' (%s €/court slot)", session_date, venue_name, venue.price_per_slot)  # type: ignore
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"✅ Session {session_date}: venue set to '{venue_name}' ({venue.price_per_slot} €/court slot). Saved as default."  # type: ignore
    )
