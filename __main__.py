"""Entry point for local polling mode. In production (webhook mode), the bot runs inside FastAPI via backend_main.py."""
import logging

from bot_app import build_application
from config import WEBHOOK_URL
from schemas.metadata import Metadata
from utils.database import db_manager

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def run():
    if WEBHOOK_URL:
        logger.error(
            "WEBHOOK_URL is set — run backend_main.py instead. "
            "__main__.py is for local polling only."
        )
        return

    try:
        db_manager.connect()
        Metadata.create()
        logger.info("Database connection established")
    except Exception as e:
        logger.error("Failed to connect to database: %s", e)
        return

    app = build_application()

    try:
        logger.info("Starting in polling mode")
        app.run_polling()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        db_manager.disconnect()


run()
