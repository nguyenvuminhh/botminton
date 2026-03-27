"""
Poll management commands: /open_poll, /close_poll
"""

from datetime import datetime, timedelta, timezone
from telegram import Update
from telegram.ext import ContextTypes

from config import COMMON_GROUP_CHAT_ID
from constants import ALL_POLL_OPTIONS, PollOptions, POLL_OPTIONS_TO_NUMBER_MAPPING
from services.metadata import get_metadata
from services.periods import get_current_period
from services.sessions import create_session, get_open_session, update_session
from services.session_participants import create_participant, delete_participant_by_user_and_session
from utils.decorator import check_admin_middleware, upsert_user
from utils.date import get_next_day, format_to_dd_mm
from utils.messages import get_poll_title
import logging

logger = logging.getLogger(__name__)

YES_OPTION_INDEX = ALL_POLL_OPTIONS.index(PollOptions.YES)


def _get_next_friday_midnight() -> datetime:
    """Return the next Friday 00:00 UTC (= Thursday midnight)."""
    now = datetime.now(tz=timezone.utc)
    # Friday = weekday 4
    days_until_friday = (4 - now.weekday() + 7) % 7
    if days_until_friday == 0:
        days_until_friday = 7
    next_friday = now + timedelta(days=days_until_friday)
    return next_friday.replace(hour=0, minute=0, second=0, microsecond=0)


@check_admin_middleware
async def open_poll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Create a session for the next play day, send a YES/NO poll to the group, schedule auto-close."""
    if not update.effective_chat:
        return

    period = get_current_period()
    if not period:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ No active period. Create one with /new_period first."
        )
        return

    # Check no poll is already open
    open_session = get_open_session()
    if open_session:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ A poll is already open for {open_session.date}."  # type: ignore
        )
        return

    metadata = get_metadata()
    if not metadata:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Metadata not initialized."
        )
        return

    from datetime import date as dt_date
    next_play_day = get_next_day(dt_date.today(), metadata.default_day_of_the_week_index)  # type: ignore
    session_date_str = next_play_day.isoformat()

    period_start_str = period.start_date.isoformat()  # type: ignore

    session = create_session(
        date=session_date_str,
        period_id=period_start_str,
        venue_id=metadata.default_venue_id or None,  # type: ignore
    )
    if not session:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Could not create session for {session_date_str} (already exists?)."
        )
        return

    poll_title = get_poll_title(
        metadata.default_start_time,  # type: ignore
        metadata.default_end_time,  # type: ignore
        metadata.default_location,  # type: ignore
        metadata.default_day_of_the_week_index,  # type: ignore
    )

    poll_message = await context.bot.send_poll(
        chat_id=COMMON_GROUP_CHAT_ID,
        question=poll_title,
        options=[opt.value for opt in ALL_POLL_OPTIONS],
        is_anonymous=False,
    )

    update_session(
        session_date_str,
        is_poll_open=True,
        telegram_poll_message_id=str(poll_message.message_id),
    )

    # Schedule auto-close at next Friday 00:00 UTC
    close_time = _get_next_friday_midnight()
    context.job_queue.run_once(  # type: ignore
        _auto_close_poll_job,
        when=close_time,
        name=f"close_poll_{session_date_str}",
        data=session_date_str,
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"✅ Poll opened for {format_to_dd_mm(next_play_day)}. Auto-closes {close_time.strftime('%d/%m %H:%M')} UTC."
    )
    logger.info(f"Poll opened for session {session_date_str}")


@check_admin_middleware
async def close_poll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manually close the current open poll."""
    if not update.effective_chat:
        return

    session = get_open_session()
    if not session:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ No open poll found."
        )
        return

    await _do_close_poll(context, str(session.date.isoformat()))  # type: ignore
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"✅ Poll for {session.date} closed."  # type: ignore
    )


async def _auto_close_poll_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Job callback to auto-close the poll."""
    session_date_str: str = context.job.data  # type: ignore
    await _do_close_poll(context, session_date_str)
    logger.info(f"Auto-closed poll for session {session_date_str}")


async def _do_close_poll(context: ContextTypes.DEFAULT_TYPE, session_date_str: str) -> None:
    """Stop the Telegram poll and mark session as closed."""
    from services.sessions import get_session
    session = get_session(session_date_str)
    if not session or not session.is_poll_open:  # type: ignore
        return

    if session.telegram_poll_message_id:  # type: ignore
        try:
            await context.bot.stop_poll(
                chat_id=COMMON_GROUP_CHAT_ID,
                message_id=int(session.telegram_poll_message_id),  # type: ignore
            )
        except Exception as e:
            logger.error(f"Failed to stop Telegram poll: {e}")

    update_session(session_date_str, is_poll_open=False)


async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Called on every PollAnswer update.
    Adds or removes the voter from session participants based on their vote.
    """
    if not update.poll_answer:
        return

    poll_answer = update.poll_answer
    voter = poll_answer.user
    telegram_id = str(voter.id)

    upsert_user(voter)

    session = get_open_session()
    if not session:
        return

    session_date_str = session.date.isoformat()  # type: ignore
    voted_yes = YES_OPTION_INDEX in poll_answer.option_ids

    if voted_yes:
        create_participant(user_telegram_id=telegram_id, session_date=session_date_str)
    else:
        # Voted NO or retracted vote
        delete_participant_by_user_and_session(
            user_telegram_id=telegram_id,
            session_date=session_date_str,
        )
