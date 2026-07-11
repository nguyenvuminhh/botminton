import config
from mongoengine import DoesNotExist

from schemas.users import Users


def normalize_telegram_id(telegram_id: str | int) -> str:
    return str(telegram_id)


def check_super_admin(telegram_id: str | int) -> bool:
    return normalize_telegram_id(telegram_id) == str(config.ADMIN_USER_ID)


def check_admin(telegram_id: str | int) -> bool:
    telegram_id = normalize_telegram_id(telegram_id)
    if check_super_admin(telegram_id):
        return True

    try:
        user = Users.objects.get(telegram_id=telegram_id)
    except DoesNotExist:
        return False
    except Exception:
        return False

    return bool(user.is_admin)
