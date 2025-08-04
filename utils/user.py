import config


def check_admin(telegram_id: str | int) -> bool:
    if isinstance(telegram_id, int):
        telegram_id = str(telegram_id)
    return telegram_id in config.ADMIN_USER_IDS