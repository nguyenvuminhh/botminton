from datetime import date as dt_date
from mongoengine import DoesNotExist, ValidationError, MultipleObjectsReturned, NotUniqueError
from schemas.periods import Periods
from schemas.period_moneys import PeriodMoneys
from schemas.users import Users
from typing import Optional, List, cast
import logging

logger = logging.getLogger(__name__)

class PeriodService:
    """Service class for period CRUD operations with unique start_date"""

    @staticmethod
    def create_period(start_date: str, end_date: Optional[str] = None, total_money: Optional[int] = None) -> Optional[Periods]:
        try:
            existing_period = PeriodService.get_period_by_start_date(start_date)
            if existing_period:
                logger.warning(f"Period with start_date {start_date} already exists")
                return existing_period

            period_data: dict = {
                'start_date': dt_date.fromisoformat(start_date),
                'total_money': total_money
            }

            if end_date:
                period_data['end_date'] = dt_date.fromisoformat(end_date)

            period = Periods(**period_data)
            period.save()
            logger.info(f"Created period starting {start_date}")
            return period

        except NotUniqueError:
            logger.error(f"Period with start_date {start_date} already exists (race condition)")
        except ValidationError as e:
            logger.error(f"Validation error creating period: {e}")
        except Exception as e:
            logger.error(f"Failed to create period: {e}")
        return None

    @staticmethod
    def get_period_by_start_date(start_date: str) -> Optional[Periods]:
        try:
            return cast(Optional[Periods], Periods.objects.get(start_date=dt_date.fromisoformat(start_date)))
        except DoesNotExist:
            logger.info(f"Period with start_date {start_date} not found")
        except MultipleObjectsReturned:
            logger.error(f"Multiple periods found with start_date {start_date}")
        except Exception as e:
            logger.error(f"Error getting period by start_date {start_date}: {e}")
        return None

    @staticmethod
    def update_period_by_start_date(start_date: str, **kwargs) -> Optional[Periods]:
        try:
            period = cast(Periods, Periods.objects.get(start_date=dt_date.fromisoformat(start_date)))

            if 'end_date' in kwargs:
                value = kwargs['end_date']
                period.end_date = dt_date.fromisoformat(value) if value else None  # type: ignore

            if 'total_money' in kwargs:
                period.total_money = kwargs['total_money']  # type: ignore

            period.save()
            logger.info(f"Updated period starting {start_date}")
            return period

        except DoesNotExist:
            logger.info(f"Period with start_date {start_date} not found for update")
        except MultipleObjectsReturned:
            logger.error(f"Multiple periods found with start_date {start_date}")
        except Exception as e:
            logger.error(f"Error updating period {start_date}: {e}")
        return None

    @staticmethod
    def delete_period_by_start_date(start_date: str) -> bool:
        try:
            period = cast(Periods, Periods.objects.get(start_date=dt_date.fromisoformat(start_date)))
            period.delete()
            logger.info(f"Deleted period starting {start_date}")
            return True
        except DoesNotExist:
            logger.info(f"Period with start_date {start_date} not found for deletion")
        except MultipleObjectsReturned:
            logger.error(f"Multiple periods found with start_date {start_date}")
        except Exception as e:
            logger.error(f"Error deleting period {start_date}: {e}")
        return False

    @staticmethod
    def list_all_periods(limit: int = 100, offset: int = 0) -> List[Periods]:
        try:
            return list(Periods.objects.skip(offset).limit(limit))  # type: ignore
        except Exception as e:
            logger.error(f"Failed to list periods: {e}")
        return []

    @staticmethod
    def get_current_period() -> Optional[Periods]:
        """Return the period whose start_date <= today and end_date is null or >= today."""
        try:
            today = dt_date.today()
            # First try: open period (no end_date)
            period = Periods.objects(start_date__lte=today, end_date=None).order_by('-start_date').first()  # type: ignore
            if period:
                return cast(Periods, period)
            # Fallback: period that hasn't ended yet
            period = Periods.objects(start_date__lte=today, end_date__gte=today).order_by('-start_date').first()  # type: ignore
            return cast(Optional[Periods], period)
        except Exception as e:
            logger.error(f"Error getting current period: {e}")
        return None

    @staticmethod
    def get_period_count() -> int:
        try:
            return int(Periods.objects.count())  # type: ignore
        except Exception as e:
            logger.error(f"Failed to count periods: {e}")
        return 0


# Convenience functions
def create_period(start_date: str, end_date: Optional[str] = None, total_money: Optional[int] = None) -> Optional[Periods]:
    return PeriodService.create_period(start_date, end_date, total_money)

def get_period(start_date: str) -> Optional[Periods]:
    return PeriodService.get_period_by_start_date(start_date)

def update_period(start_date: str, **kwargs) -> Optional[Periods]:
    return PeriodService.update_period_by_start_date(start_date, **kwargs)

def delete_period(start_date: str) -> bool:
    return PeriodService.delete_period_by_start_date(start_date)

def list_all_periods(limit: int = 100, offset: int = 0) -> List[Periods]:
    return PeriodService.list_all_periods(limit, offset)

def get_current_period() -> Optional[Periods]:
    return PeriodService.get_current_period()

def get_period_count() -> int:
    return PeriodService.get_period_count()

# Legacy alias used by some tests
def get_period_by_start_date(start_date: str) -> Optional[Periods]:
    return PeriodService.get_period_by_start_date(start_date)
