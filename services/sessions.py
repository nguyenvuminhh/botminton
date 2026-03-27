from datetime import date as dt_date
from mongoengine import DoesNotExist, ValidationError, MultipleObjectsReturned
from schemas.sessions import Sessions
from schemas.periods import Periods
from schemas.venues import Venues
from typing import Optional, List, cast
import logging

logger = logging.getLogger(__name__)


class SessionService:
    """Service class for session CRUD operations"""

    @staticmethod
    def create_session(
        date: str,
        period_id: str,
        venue_id: Optional[str] = None,
        slots: float = 0.0,
        telegram_poll_message_id: Optional[str] = None,
    ) -> Optional[Sessions]:
        try:
            try:
                period = Periods.objects.get(start_date=dt_date.fromisoformat(period_id))  # type: ignore
            except Exception:
                period = Periods.objects.get(id=period_id)  # type: ignore

            venue = None
            if venue_id:
                try:
                    venue = Venues.objects.get(name=venue_id)  # type: ignore
                except DoesNotExist:
                    try:
                        venue = Venues.objects.get(id=venue_id)  # type: ignore
                    except DoesNotExist:
                        logger.warning(f"Venue '{venue_id}' not found; session created without venue")

            session = Sessions(
                date=dt_date.fromisoformat(date),
                period=period,
                venue=venue,
                slots=slots,
                telegram_poll_message_id=telegram_poll_message_id,
            )
            session.save()
            logger.info(f"Created session on {date}")
            return session
        except DoesNotExist:
            logger.error(f"Period with id/start_date {period_id} does not exist")
        except ValidationError as e:
            logger.error(f"Validation error while creating session on {date}: {e}")
        except Exception as e:
            logger.error(f"Failed to create session on {date}: {e}")
        return None

    @staticmethod
    def get_session_by_date(date: str) -> Optional[Sessions]:
        try:
            return cast(Optional[Sessions], Sessions.objects.get(date=dt_date.fromisoformat(date)))
        except DoesNotExist:
            logger.info(f"Session on {date} not found")
        except MultipleObjectsReturned:
            logger.error(f"Multiple sessions found on {date} — database integrity issue")
        except Exception as e:
            logger.error(f"Error getting session on {date}: {e}")
        return None

    @staticmethod
    def update_session_by_date(date: str, **kwargs) -> Optional[Sessions]:
        try:
            session = cast(Sessions, Sessions.objects.get(date=dt_date.fromisoformat(date)))

            if 'period' in kwargs:
                try:
                    try:
                        session.period = Periods.objects.get(start_date=dt_date.fromisoformat(kwargs['period']))  # type: ignore
                    except Exception:
                        session.period = Periods.objects.get(id=kwargs['period'])  # type: ignore
                except DoesNotExist:
                    logger.error(f"Period {kwargs['period']} does not exist")
                    return None

            if 'venue' in kwargs:
                venue_id = kwargs['venue']
                if venue_id is None:
                    session.venue = None  # type: ignore
                else:
                    try:
                        session.venue = Venues.objects.get(name=venue_id)  # type: ignore
                    except DoesNotExist:
                        try:
                            session.venue = Venues.objects.get(id=venue_id)  # type: ignore
                        except DoesNotExist:
                            logger.error(f"Venue '{venue_id}' not found")
                            return None

            for field in ('slots', 'is_poll_open', 'telegram_poll_message_id'):
                if field in kwargs:
                    setattr(session, field, kwargs[field])

            session.save()
            logger.info(f"Updated session on {date}")
            return session

        except DoesNotExist:
            logger.info(f"Session on {date} not found for update")
        except MultipleObjectsReturned:
            logger.error(f"Multiple sessions found on {date} — cannot update uniquely")
        except Exception as e:
            logger.error(f"Error updating session on {date}: {e}")
        return None

    @staticmethod
    def delete_session_by_date(date: str) -> bool:
        try:
            session = cast(Sessions, Sessions.objects.get(date=dt_date.fromisoformat(date)))
            session.delete()
            logger.info(f"Deleted session on {date}")
            return True
        except DoesNotExist:
            logger.info(f"Session on {date} not found for deletion")
        except MultipleObjectsReturned:
            logger.error(f"Multiple sessions found on {date} — cannot delete uniquely")
        except Exception as e:
            logger.error(f"Error deleting session on {date}: {e}")
        return False

    @staticmethod
    def list_sessions_by_period_id(period_id: str) -> List[Sessions]:
        try:
            try:
                period = Periods.objects.get(start_date=dt_date.fromisoformat(period_id))  # type: ignore
            except Exception:
                period = Periods.objects.get(id=period_id)  # type: ignore
            return list(Sessions.objects(period=period))  # type: ignore
        except DoesNotExist:
            logger.info(f"No period found with id/start_date {period_id}")
        except Exception as e:
            logger.error(f"Error listing sessions by period {period_id}: {e}")
        return []

    @staticmethod
    def get_current_session() -> Optional[Sessions]:
        try:
            today = dt_date.today()
            session = cast(Sessions, Sessions.objects(date=today).first())
            if session:
                return session
            logger.info(f"No current session found for {today}")
        except Exception as e:
            logger.error(f"Error getting current session: {e}")
        return None

    @staticmethod
    def get_open_session() -> Optional[Sessions]:
        """Return the session with an open poll, if any."""
        try:
            return cast(Optional[Sessions], Sessions.objects(is_poll_open=True).first())  # type: ignore
        except Exception as e:
            logger.error(f"Error getting open session: {e}")
        return None


# Convenience functions
def create_session(
    date: str,
    period_id: str,
    venue_id: Optional[str] = None,
    slots: float = 0.0,
    telegram_poll_message_id: Optional[str] = None,
) -> Optional[Sessions]:
    return SessionService.create_session(date, period_id, venue_id, slots, telegram_poll_message_id)

def get_session(date: str) -> Optional[Sessions]:
    return SessionService.get_session_by_date(date)

def update_session(date: str, **kwargs) -> Optional[Sessions]:
    return SessionService.update_session_by_date(date, **kwargs)

def delete_session(date: str) -> bool:
    return SessionService.delete_session_by_date(date)

def list_sessions_by_period(period_id: str) -> List[Sessions]:
    return SessionService.list_sessions_by_period_id(period_id)

def get_current_session() -> Optional[Sessions]:
    return SessionService.get_current_session()

def get_open_session() -> Optional[Sessions]:
    return SessionService.get_open_session()
