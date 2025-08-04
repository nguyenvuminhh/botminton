from datetime import date as dt_date
from mongoengine import DoesNotExist, ValidationError, MultipleObjectsReturned
from orms.sessions import Sessions
from orms.periods import Periods
from typing import Optional, List, cast
import logging

logger = logging.getLogger(__name__)

class SessionService:
    """Service class for session CRUD operations"""

    @staticmethod
    def create_session(date: str, period_id: str, courts_price: float, telegram_poll_message_id: str) -> Optional[Sessions]:
        try:
            # Try to get period by start_date first, then by ID
            try:
                period = Periods.objects.get(start_date=dt_date.fromisoformat(period_id))  # type: ignore
            except:
                period = Periods.objects.get(id=period_id)  # type: ignore
            
            session = Sessions(
                date=dt_date.fromisoformat(date),
                period=period,
                courts_price=courts_price,
                telegram_poll_message_id=telegram_poll_message_id
            )
            session.save()
            logger.info(f"Created session on {date} with period {period_id}")
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
                    # Try to get period by start_date first, then by ID
                    try:
                        session.period = Periods.objects.get(start_date=dt_date.fromisoformat(kwargs['period']))  # type: ignore
                    except:
                        session.period = Periods.objects.get(id=kwargs['period'])  # type: ignore
                except DoesNotExist:
                    logger.error(f"Period with id/start_date {kwargs['period']} does not exist")
                    return None

            if 'courts_price' in kwargs:
                session.courts_price = kwargs['courts_price']

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
            # Try to get period by start_date first, then by ID
            try:
                period = Periods.objects.get(start_date=dt_date.fromisoformat(period_id))  # type: ignore
            except:
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
                logger.debug(f"Found current session on {today}")
                return session
            else:
                logger.info(f"No current session found for {today}")
        except Exception as e:
            logger.error(f"Error getting current session: {e}")
        return None

# Convenience functions for direct use
def create_session(date: str, period_id: str, courts_price: float, telegram_poll_message_id: str) -> Optional[Sessions]:
    """Create session - convenience function"""
    return SessionService.create_session(date, period_id, courts_price, telegram_poll_message_id)

def get_session(date: str) -> Optional[Sessions]:
    """Get session by date - convenience function"""
    return SessionService.get_session_by_date(date)

def update_session(date: str, **kwargs) -> Optional[Sessions]:
    """Update session by date - convenience function"""
    return SessionService.update_session_by_date(date, **kwargs)

def delete_session(date: str) -> bool:
    """Delete session by date - convenience function"""
    return SessionService.delete_session_by_date(date)

def list_sessions_by_period(period_id: str) -> List[Sessions]:
    """List sessions by period ID - convenience function"""
    return SessionService.list_sessions_by_period_id(period_id)

def get_current_session() -> Optional[Sessions]:
    """Get current session (today) - convenience function"""
    return SessionService.get_current_session()

