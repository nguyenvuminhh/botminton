from schemas.users import Users
from mongoengine import DoesNotExist, MultipleObjectsReturned
from typing import Optional, List, cast
import logging

from utils.user import check_admin

logger = logging.getLogger(__name__)

class UserService:
    """Service class for user CRUD operations"""

    @staticmethod
    def create_user(telegram_id: str, telegram_user_name: Optional[str] = None) -> Optional[Users]:
        try:
            is_admin = check_admin(telegram_id)

            existing_user = UserService.get_user_by_telegram_id(telegram_id)
            if existing_user:
                logger.warning(f"User with telegram_id {telegram_id} already exists")
                return existing_user

            user = Users(
                telegram_id=telegram_id,
                telegram_user_name=telegram_user_name,
                is_admin=is_admin
            )
            user.save()
            logger.info(f"Created user with telegram_id: {telegram_id}")
            return user

        except Exception as e:
            logger.error(f"Failed to create user with telegram_id {telegram_id}: {e}")
            return None

    @staticmethod
    def get_user_by_telegram_id(telegram_id: str) -> Optional[Users]:
        try:
            user = cast(Users, Users.objects.get(telegram_id=telegram_id))
            logger.debug(f"Found user with telegram_id: {telegram_id}")
            return user

        except DoesNotExist:
            logger.info(f"User with telegram_id {telegram_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error getting user with telegram_id {telegram_id}: {e}")
            return None

    @staticmethod
    def update_user_by_telegram_id(telegram_id: str, **kwargs) -> Optional[Users]:
        try:
            user = cast(Users, Users.objects.get(telegram_id=telegram_id))
            is_admin = check_admin(telegram_id)

            if 'telegram_user_name' in kwargs:
                user.telegram_user_name = kwargs['telegram_user_name']

            user.is_admin = is_admin

            user.save()
            logger.info(f"Updated user with telegram_id: {telegram_id}")
            return user

        except DoesNotExist:
            logger.warning(f"Cannot update - user with telegram_id {telegram_id} not found")
            return None
        except Exception as e:
            logger.error(f"Failed to update user with telegram_id {telegram_id}: {e}")
            return None

    @staticmethod
    def delete_user_by_telegram_id(telegram_id: str) -> bool:
        try:
            user = cast(Users, Users.objects.get(telegram_id=telegram_id))
            user.delete()
            logger.info(f"Deleted user with telegram_id: {telegram_id}")
            return True

        except DoesNotExist:
            logger.warning(f"Cannot delete - user with telegram_id {telegram_id} not found")
            return False
        except Exception as e:
            logger.error(f"Failed to delete user with telegram_id {telegram_id}: {e}")
            return False

    @staticmethod
    def list_all_users(limit: int = 100, offset: int = 0) -> List[Users]:
        try:
            users = list(Users.objects.skip(offset).limit(limit))
            logger.debug(f"Listed {len(users)} users")
            return users

        except Exception as e:
            logger.error(f"Failed to list all users: {e}")
            return []

    @staticmethod
    def get_user_by_username(username: str) -> Optional[Users]:
        """Look up a user by telegram_user_name (case-insensitive, strips leading @)."""
        try:
            clean = username.lstrip("@")
            return cast(Users, Users.objects.get(telegram_user_name__iexact=clean))
        except DoesNotExist:
            logger.info(f"User with username '{username}' not found")
            return None
        except MultipleObjectsReturned:
            logger.warning(f"Multiple users found with name '{username}'")
            return None
        except Exception as e:
            logger.error(f"Error getting user by username '{username}': {e}")
            return None

# ------------------------
# ✅ Convenience functions
# ------------------------

def create_user(telegram_id: str, telegram_user_name: Optional[str] = None) -> Optional[Users]:
    return UserService.create_user(telegram_id, telegram_user_name)

def get_user(telegram_id: str) -> Optional[Users]:
    return UserService.get_user_by_telegram_id(telegram_id)

def get_user_by_username(username: str) -> Optional[Users]:
    return UserService.get_user_by_username(username)

def update_user(telegram_id: str, **kwargs) -> Optional[Users]:
    return UserService.update_user_by_telegram_id(telegram_id, **kwargs)

def delete_user(telegram_id: str) -> bool:
    return UserService.delete_user_by_telegram_id(telegram_id)

def list_all_users(limit: int = 100, offset: int = 0) -> List[Users]:
    return UserService.list_all_users(limit, offset)