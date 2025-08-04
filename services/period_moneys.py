from mongoengine import DoesNotExist, ValidationError
from orms.period_moneys import PeriodMoneys
from orms.users import Users
from services.periods import PeriodService
from typing import Optional, List, cast
import logging

logger = logging.getLogger(__name__)

class PeriodMoneyService:
    """Service class for period money CRUD operations"""

    @staticmethod
    def create_period_money(period_start_date: str, user_telegram_id: str, amount: float) -> Optional[PeriodMoneys]:
        """
        Create a new period money record
        
        Args:
            period_start_date (str): Period start date in ISO format
            user_telegram_id (str): User telegram ID
            amount (float): Money amount
            
        Returns:
            PeriodMoneys: Created period money object or None if failed
        """
        try:
            # Check if period money already exists
            existing_pm = PeriodMoneyService.get_period_money_by_date(period_start_date, user_telegram_id)
            if existing_pm:
                logger.warning(f"Period money already exists for user {user_telegram_id} in period {period_start_date}")
                return None
            
            # Get period and user
            period = PeriodService.get_period_by_start_date(period_start_date)
            if not period:
                logger.error(f"Period with start_date {period_start_date} not found")
                return None
            
            user = cast(Users, Users.objects.get(telegram_id=user_telegram_id))  # type: ignore
            if not user:
                logger.error(f"User with telegram_id {user_telegram_id} not found")
                return None
            
            # Create period money
            period_money = PeriodMoneys(
                period=period,
                user=user,
                amount=amount
            )
            period_money.save()
            
            logger.info(f"Created period money: {amount} for user {user_telegram_id} in period {period_start_date}")
            return period_money
            
        except DoesNotExist as e:
            logger.error(f"Referenced object not found: {e}")
            return None
        except ValidationError as e:
            logger.error(f"Validation error while creating period money: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to create period money: {e}")
            return None

    @staticmethod
    def get_period_money_by_date(period_start_date: str, user_telegram_id: str) -> Optional[PeriodMoneys]:
        """
        Get period money by period start date and user
        
        Args:
            period_start_date (str): Period start date in ISO format
            user_telegram_id (str): User telegram ID
            
        Returns:
            PeriodMoneys: Period money object or None if not found
        """
        try:
            # Get period and user
            period = PeriodService.get_period_by_start_date(period_start_date)
            if not period:
                logger.error(f"Period with start_date {period_start_date} not found")
                return None
            
            user = cast(Users, Users.objects.get(telegram_id=user_telegram_id))  # type: ignore
            if not user:
                logger.error(f"User with telegram_id {user_telegram_id} not found")
                return None
            
            # Handle multiple records gracefully - get the first one
            period_moneys = list(PeriodMoneys.objects.filter(period=period, user=user))  # type: ignore
            if not period_moneys:
                logger.debug(f"Period money for user {user_telegram_id} in period {period_start_date} not found")
                return None
            
            if len(period_moneys) > 1:
                logger.warning(f"Multiple period money records found for user {user_telegram_id} in period {period_start_date}, returning the first one")
                # Optionally clean up duplicates by keeping the first and deleting the rest
                first_pm = period_moneys[0]
                for duplicate_pm in period_moneys[1:]:
                    logger.info(f"Removing duplicate period money record: {duplicate_pm.id}")
                    duplicate_pm.delete()  # type: ignore
                return first_pm
            
            period_money = period_moneys[0]
            logger.debug(f"Found period money for user {user_telegram_id} in period {period_start_date}")
            return period_money
            
        except DoesNotExist:
            logger.debug(f"Period money for user {user_telegram_id} in period {period_start_date} not found")
            return None
        except Exception as e:
            logger.error(f"Error getting period money for user {user_telegram_id} in period {period_start_date}: {e}")
            return None

    @staticmethod
    def get_period_money_by_id(period_money_id: str) -> Optional[PeriodMoneys]:
        """
        Get period money by ID
        
        Args:
            period_money_id (str): Period money ID
            
        Returns:
            PeriodMoneys: Period money object or None if not found
        """
        try:
            period_money = cast(PeriodMoneys, PeriodMoneys.objects.get(id=period_money_id))  # type: ignore
            logger.debug(f"Found period money with ID: {period_money_id}")
            return period_money
            
        except DoesNotExist:
            logger.debug(f"Period money with ID {period_money_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error getting period money with ID {period_money_id}: {e}")
            return None

    @staticmethod
    def update_period_money_by_date(period_start_date: str, user_telegram_id: str, **kwargs) -> Optional[PeriodMoneys]:
        """
        Update period money by period start date and user
        
        Args:
            period_start_date (str): Period start date in ISO format
            user_telegram_id (str): User telegram ID
            **kwargs: Fields to update (amount)
            
        Returns:
            PeriodMoneys: Updated period money object or None if failed
        """
        try:
            # Get the period money record first
            period_money = PeriodMoneyService.get_period_money_by_date(period_start_date, user_telegram_id)
            if not period_money:
                logger.warning(f"Cannot update - period money for user {user_telegram_id} in period {period_start_date} not found")
                return None
            
            # Update fields
            if 'amount' in kwargs:
                period_money.amount = kwargs['amount']
            
            period_money.save()
            
            logger.info(f"Updated period money for user {user_telegram_id} in period {period_start_date}")
            return period_money
            
        except ValidationError as e:
            logger.error(f"Validation error while updating period money: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to update period money for user {user_telegram_id} in period {period_start_date}: {e}")
            return None

    @staticmethod
    def update_period_money_by_id(period_money_id: str, **kwargs) -> Optional[PeriodMoneys]:
        """
        Update period money by ID
        
        Args:
            period_money_id (str): Period money ID
            **kwargs: Fields to update (amount)
            
        Returns:
            PeriodMoneys: Updated period money object or None if failed
        """
        try:
            period_money = cast(PeriodMoneys, PeriodMoneys.objects.get(id=period_money_id))  # type: ignore
            
            # Update fields
            if 'amount' in kwargs:
                period_money.amount = kwargs['amount']
            
            period_money.save()
            
            logger.info(f"Updated period money with ID: {period_money_id}")
            return period_money
            
        except DoesNotExist:
            logger.warning(f"Cannot update - period money with ID {period_money_id} not found")
            return None
        except ValidationError as e:
            logger.error(f"Validation error while updating period money: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to update period money with ID {period_money_id}: {e}")
            return None

    @staticmethod
    def delete_period_money_by_date(period_start_date: str, user_telegram_id: str) -> bool:
        """
        Delete period money by period start date and user
        
        Args:
            period_start_date (str): Period start date in ISO format
            user_telegram_id (str): User telegram ID
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            # Get the period money record first
            period_money = PeriodMoneyService.get_period_money_by_date(period_start_date, user_telegram_id)
            if not period_money:
                logger.warning(f"Cannot delete - period money for user {user_telegram_id} in period {period_start_date} not found")
                return False
            
            period_money.delete()
            
            logger.info(f"Deleted period money for user {user_telegram_id} in period {period_start_date}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete period money for user {user_telegram_id} in period {period_start_date}: {e}")
            return False

    @staticmethod
    def delete_period_money_by_id(period_money_id: str) -> bool:
        """
        Delete period money by ID
        
        Args:
            period_money_id (str): Period money ID
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            period_money = cast(PeriodMoneys, PeriodMoneys.objects.get(id=period_money_id))  # type: ignore
            period_money.delete()
            
            logger.info(f"Deleted period money with ID: {period_money_id}")
            return True
            
        except DoesNotExist:
            logger.warning(f"Cannot delete - period money with ID {period_money_id} not found")
            return False
        except Exception as e:
            logger.error(f"Failed to delete period money with ID {period_money_id}: {e}")
            return False

    @staticmethod
    def list_period_moneys_by_period(period_start_date: str) -> List[PeriodMoneys]:
        """
        List all period moneys for a specific period
        
        Args:
            period_start_date (str): Period start date in ISO format
            
        Returns:
            List[PeriodMoneys]: List of period money objects
        """
        try:
            period = PeriodService.get_period_by_start_date(period_start_date)
            if not period:
                logger.warning(f"Period with start_date {period_start_date} not found")
                return []
            
            period_moneys = list(PeriodMoneys.objects.filter(period=period))  # type: ignore
            
            logger.debug(f"Found {len(period_moneys)} period moneys for period {period_start_date}")
            return period_moneys
            
        except Exception as e:
            logger.error(f"Failed to list period moneys for period {period_start_date}: {e}")
            return []

    @staticmethod
    def list_period_moneys_by_user(user_telegram_id: str) -> List[PeriodMoneys]:
        """
        List all period moneys for a specific user
        
        Args:
            user_telegram_id (str): User telegram ID
            
        Returns:
            List[PeriodMoneys]: List of period money objects
        """
        try:
            user = cast(Users, Users.objects.get(telegram_id=user_telegram_id))  # type: ignore
            period_moneys = list(PeriodMoneys.objects.filter(user=user))  # type: ignore
            
            logger.debug(f"Found {len(period_moneys)} period moneys for user {user_telegram_id}")
            return period_moneys
            
        except DoesNotExist:
            logger.warning(f"User with telegram_id {user_telegram_id} not found")
            return []
        except Exception as e:
            logger.error(f"Failed to list period moneys for user {user_telegram_id}: {e}")
            return []

    @staticmethod
    def get_total_money_for_period(period_start_date: str) -> float:
        """
        Calculate total money for a specific period
        
        Args:
            period_start_date (str): Period start date in ISO format
            
        Returns:
            float: Total money amount
        """
        try:
            period_moneys = PeriodMoneyService.list_period_moneys_by_period(period_start_date)
            total = 0.0
            for pm in period_moneys:
                total += pm.amount  # type: ignore
            
            logger.debug(f"Total money for period {period_start_date}: {total}")
            return total
            
        except Exception as e:
            logger.error(f"Failed to calculate total money for period {period_start_date}: {e}")
            return 0.0
        
    @staticmethod
    def mark_as_paid_by_telegram_id(period_start_date: str, user_telegram_id: str) -> Optional[PeriodMoneys]:
        """
        Mark period money as paid by period start date and user telegram ID
        
        Args:
            period_start_date (str): Period start date in ISO format
            user_telegram_id (str): User telegram ID
            
        Returns:
            PeriodMoneys: Updated period money object or None if failed
        """
        try:
            period_money = PeriodMoneyService.get_period_money_by_date(period_start_date, user_telegram_id)
            if not period_money:
                logger.warning(f"Cannot mark as paid - period money for user {user_telegram_id} in period {period_start_date} not found")
                return None
            
            period_money.has_paid = True
            period_money.save()
            
            logger.info(f"Marked period money as paid for user {user_telegram_id} in period {period_start_date}")
            return period_money
            
        except Exception as e:
            logger.error(f"Failed to mark period money as paid for user {user_telegram_id} in period {period_start_date}: {e}")
            return None

    @staticmethod
    def mark_as_unpaid_by_telegram_id(period_start_date: str, user_telegram_id: str) -> Optional[PeriodMoneys]:
        """
        Mark period money as unpaid by period start date and user telegram ID
        
        Args:
            period_start_date (str): Period start date in ISO format
            user_telegram_id (str): User telegram ID
            
        Returns:
            PeriodMoneys: Updated period money object or None if failed
        """
        try:
            period_money = PeriodMoneyService.get_period_money_by_date(period_start_date, user_telegram_id)
            if not period_money:
                logger.warning(f"Cannot mark as unpaid - period money for user {user_telegram_id} in period {period_start_date} not found")
                return None
            
            period_money.has_paid = False
            period_money.save()
            
            logger.info(f"Marked period money as unpaid for user {user_telegram_id} in period {period_start_date}")
            return period_money
            
        except Exception as e:
            logger.error(f"Failed to mark period money as unpaid for user {user_telegram_id} in period {period_start_date}: {e}")
            return None

    @staticmethod
    def list_paid_by_period_start_date(period_start_date: str) -> List[PeriodMoneys]:
        """
        List all paid period moneys for a specific period
        
        Args:
            period_start_date (str): Period start date in ISO format
            
        Returns:
            List[PeriodMoneys]: List of paid period money objects
        """
        try:
            period = PeriodService.get_period_by_start_date(period_start_date)
            if not period:
                logger.warning(f"Period with start_date {period_start_date} not found")
                return []
            
            paid_period_moneys = list(PeriodMoneys.objects.filter(period=period, has_paid=True))  # type: ignore
            
            logger.debug(f"Found {len(paid_period_moneys)} paid period moneys for period {period_start_date}")
            return paid_period_moneys
            
        except Exception as e:
            logger.error(f"Failed to list paid period moneys for period {period_start_date}: {e}")
            return []

    @staticmethod
    def list_unpaid_by_period_start_date(period_start_date: str) -> List[PeriodMoneys]:
        """
        List all unpaid period moneys for a specific period
        
        Args:
            period_start_date (str): Period start date in ISO format
            
        Returns:
            List[PeriodMoneys]: List of unpaid period money objects
        """
        try:
            period = PeriodService.get_period_by_start_date(period_start_date)
            if not period:
                logger.warning(f"Period with start_date {period_start_date} not found")
                return []
            
            unpaid_period_moneys = list(PeriodMoneys.objects.filter(period=period, has_paid=False))  # type: ignore
            
            logger.debug(f"Found {len(unpaid_period_moneys)} unpaid period moneys for period {period_start_date}")
            return unpaid_period_moneys
            
        except Exception as e:
            logger.error(f"Failed to list unpaid period moneys for period {period_start_date}: {e}")
            return []


# Convenience functions for PeriodMoneys
def create_period_money(period_start_date: str, user_telegram_id: str, amount: float) -> Optional[PeriodMoneys]:
    """Create period money - convenience function"""
    return PeriodMoneyService.create_period_money(period_start_date, user_telegram_id, amount)

def get_period_money(period_start_date: str, user_telegram_id: str) -> Optional[PeriodMoneys]:
    """Get period money by period start date and user - convenience function"""
    return PeriodMoneyService.get_period_money_by_date(period_start_date, user_telegram_id)

def get_period_money_by_id(period_money_id: str) -> Optional[PeriodMoneys]:
    """Get period money by ID - convenience function"""
    return PeriodMoneyService.get_period_money_by_id(period_money_id)

def update_period_money(period_start_date: str, user_telegram_id: str, **kwargs) -> Optional[PeriodMoneys]:
    """Update period money by period start date and user - convenience function"""
    return PeriodMoneyService.update_period_money_by_date(period_start_date, user_telegram_id, **kwargs)

def update_period_money_by_id(period_money_id: str, **kwargs) -> Optional[PeriodMoneys]:
    """Update period money by ID - convenience function"""
    return PeriodMoneyService.update_period_money_by_id(period_money_id, **kwargs)

def delete_period_money(period_start_date: str, user_telegram_id: str) -> bool:
    """Delete period money by period start date and user - convenience function"""
    return PeriodMoneyService.delete_period_money_by_date(period_start_date, user_telegram_id)

def delete_period_money_by_id(period_money_id: str) -> bool:
    """Delete period money by ID - convenience function"""
    return PeriodMoneyService.delete_period_money_by_id(period_money_id)

def list_period_moneys_by_period(period_start_date: str) -> List[PeriodMoneys]:
    """List period moneys by period - convenience function"""
    return PeriodMoneyService.list_period_moneys_by_period(period_start_date)

def list_period_moneys_by_user(user_telegram_id: str) -> List[PeriodMoneys]:
    """List period moneys by user - convenience function"""
    return PeriodMoneyService.list_period_moneys_by_user(user_telegram_id)

def get_total_money_for_period(period_start_date: str) -> float:
    """Get total money for period - convenience function"""
    return PeriodMoneyService.get_total_money_for_period(period_start_date)

def mark_as_paid_by_telegram_id(period_start_date: str, user_telegram_id: str) -> Optional[PeriodMoneys]:
    """Mark period money as paid by telegram ID - convenience function"""
    return PeriodMoneyService.mark_as_paid_by_telegram_id(period_start_date, user_telegram_id)

def mark_as_unpaid_by_telegram_id(period_start_date: str, user_telegram_id: str) -> Optional[PeriodMoneys]:
    """Mark period money as unpaid by telegram ID - convenience function"""
    return PeriodMoneyService.mark_as_unpaid_by_telegram_id(period_start_date, user_telegram_id)

def list_paid_by_period_start_date(period_start_date: str) -> List[PeriodMoneys]:
    """List paid period moneys for a period - convenience function"""
    return PeriodMoneyService.list_paid_by_period_start_date(period_start_date)

def list_unpaid_by_period_start_date(period_start_date: str) -> List[PeriodMoneys]:
    """List unpaid period moneys for a period - convenience function"""
    return PeriodMoneyService.list_unpaid_by_period_start_date(period_start_date)
