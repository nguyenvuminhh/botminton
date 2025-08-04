from datetime import date as dt_date
from mongoengine import DoesNotExist, ValidationError, MultipleObjectsReturned, NotUniqueError
from orms.periods import Periods
from orms.period_moneys import PeriodMoneys
from orms.users import Users
from typing import Optional, List, cast
import logging

logger = logging.getLogger(__name__)

class PeriodService:
    """Service class for period CRUD operations with unique start_date"""

    @staticmethod
    def create_period(start_date: str, end_date: Optional[str] = None, total_money: Optional[int] = None) -> Optional[Periods]:
        """
        Create a new period with unique start_date
        
        Args:
            start_date (str): Start date in ISO format (YYYY-MM-DD)
            end_date (str): End date in ISO format (YYYY-MM-DD), optional
            total_money (int): Total money for the period, optional
            
        Returns:
            Periods: Created period object or None if failed
        """
        try:
            # Check if period with this start_date already exists
            existing_period = PeriodService.get_period_by_start_date(start_date)
            if existing_period:
                logger.warning(f"Period with start_date {start_date} already exists")
                return existing_period

            # Create new period
            period_data = {
                'start_date': dt_date.fromisoformat(start_date),
                'total_money': total_money
            }
            
            if end_date:
                period_data['end_date'] = dt_date.fromisoformat(end_date)

            period = Periods(**period_data)
            period.save()
            
            logger.info(f"Created period with start_date: {start_date}")
            return period
            
        except NotUniqueError:
            logger.error(f"Period with start_date {start_date} already exists (unique constraint)")
            return None
        except ValidationError as e:
            logger.error(f"Validation error while creating period: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to create period with start_date {start_date}: {e}")
            return None

    @staticmethod
    def get_period_by_start_date(start_date: str) -> Optional[Periods]:
        """
        Get period by start_date
        
        Args:
            start_date (str): Start date in ISO format (YYYY-MM-DD)
            
        Returns:
            Periods: Period object or None if not found
        """
        try:
            period = cast(Periods, Periods.objects.get(start_date=dt_date.fromisoformat(start_date))) 
            logger.debug(f"Found period with start_date: {start_date}")
            return period
            
        except DoesNotExist:
            logger.debug(f"Period with start_date {start_date} not found")
            return None
        except Exception as e:
            logger.error(f"Error getting period with start_date {start_date}: {e}")
            return None

    @staticmethod
    def update_period_by_start_date(start_date: str, **kwargs) -> Optional[Periods]:
        """
        Update period by start_date
        
        Args:
            start_date (str): Start date in ISO format (YYYY-MM-DD)
            **kwargs: Fields to update (end_date, total_money)
            
        Returns:
            Periods: Updated period object or None if failed
        """
        try:
            period = cast(Periods, Periods.objects.get(start_date=dt_date.fromisoformat(start_date))) 
            
            # Update fields
            if 'end_date' in kwargs:
                if kwargs['end_date']:
                    period.end_date = dt_date.fromisoformat(kwargs['end_date'])
                else:
                    period.end_date = None
            
            if 'total_money' in kwargs:
                period.total_money = kwargs['total_money']
            
            period.save()
            
            logger.info(f"Updated period with start_date: {start_date}")
            return period
            
        except DoesNotExist:
            logger.warning(f"Cannot update - period with start_date {start_date} not found")
            return None
        except ValidationError as e:
            logger.error(f"Validation error while updating period: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to update period with start_date {start_date}: {e}")
            return None

    @staticmethod
    def delete_period_by_start_date(start_date: str) -> bool:
        """
        Delete period by start_date
        
        Args:
            start_date (str): Start date in ISO format (YYYY-MM-DD)
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            period = cast(Periods, Periods.objects.get(start_date=dt_date.fromisoformat(start_date)))
            period.delete()
            
            logger.info(f"Deleted period with start_date: {start_date}")
            return True
            
        except DoesNotExist:
            logger.warning(f"Cannot delete - period with start_date {start_date} not found")
            return False
        except Exception as e:
            logger.error(f"Failed to delete period with start_date {start_date}: {e}")
            return False

    @staticmethod
    def list_all_periods(limit: int = 100, offset: int = 0) -> List[Periods]:
        """
        List all periods with pagination
        
        Args:
            limit (int): Maximum number of periods to return
            offset (int): Number of periods to skip
            
        Returns:
            List[Periods]: List of period objects
        """
        try:
            periods = Periods.objects.skip(offset).limit(limit).order_by('-start_date') 
            periods_list = list(periods)
            
            logger.debug(f"Listed {len(periods_list)} periods")
            return periods_list
            
        except Exception as e:
            logger.error(f"Failed to list periods: {e}")
            return []

    @staticmethod
    def get_current_period() -> Optional[Periods]:
        """
        Get current period (period where today falls between start_date and end_date)
        If no end_date is set, consider it as ongoing period
        
        Returns:
            Periods: Current period object or None if not found
        """
        try:
            today = dt_date.today()
            
            # Find period where today is between start_date and end_date
            # Or where start_date <= today and end_date is None (ongoing period)
            current_period = cast(
                Periods,
                Periods.objects(  # type: ignore
                    start_date__lte=today
                ).filter(
                    __raw__={
                        '$or': [
                            {'end_date': {'$gte': today}},
                            {'end_date': None}
                        ]
                    }
                ).order_by('-start_date').first()
            )
            
            if current_period:
                logger.debug(f"Found current period: {current_period.start_date}")
                return current_period
            else:
                logger.info("No current period found")
                return None
                
        except Exception as e:
            logger.error(f"Error getting current period: {e}")
            return None

    @staticmethod
    def get_period_count() -> int:
        """
        Get total number of periods
        
        Returns:
            int: Number of periods
        """
        try:
            count = Periods.objects.count() 
            logger.debug(f"Period count: {count}")
            return count
            
        except Exception as e:
            logger.error(f"Failed to get period count: {e}")
            return 0


# Convenience functions for Periods
def create_period(start_date: str, end_date: Optional[str] = None, total_money: Optional[int] = None) -> Optional[Periods]:
    """Create period - convenience function"""
    return PeriodService.create_period(start_date, end_date, total_money)

def get_period(start_date: str) -> Optional[Periods]:
    """Get period by start_date - convenience function"""
    return PeriodService.get_period_by_start_date(start_date)

def update_period(start_date: str, **kwargs) -> Optional[Periods]:
    """Update period by start_date - convenience function"""
    return PeriodService.update_period_by_start_date(start_date, **kwargs)

def delete_period(start_date: str) -> bool:
    """Delete period by start_date - convenience function"""
    return PeriodService.delete_period_by_start_date(start_date)

def list_all_periods(limit: int = 100, offset: int = 0) -> List[Periods]:
    """List all periods - convenience function"""
    return PeriodService.list_all_periods(limit, offset)

def get_current_period() -> Optional[Periods]:
    """Get current period - convenience function"""
    return PeriodService.get_current_period()
