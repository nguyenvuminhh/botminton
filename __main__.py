from commands.start import start
from config import BOT_TOKEN
from constants import Commands
from orms.metadata import Metadata
from utils.database import db_manager
from telegram.ext import ApplicationBuilder, CommandHandler
import logging

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def run():
    # Initialize database connection
    try:
        db_manager.connect()
        Metadata.create()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler(Commands.START, start))

    try:
        app.run_polling()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        # Clean up database connection
        db_manager.disconnect()

if __name__ == "__main__":
    run()

