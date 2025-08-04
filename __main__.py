from commands.print_id import print_group_chat_id, print_user_id
from commands.start import start, test_admin
from config import BOT_TOKEN
from constants import Commands
from orms.metadata import Metadata
from utils.database import db_manager
from telegram.ext import ApplicationBuilder, CommandHandler, Application
import logging

from utils.decorator import user_insertion_middleware

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Register command handlers with middleware
def register_command(app: Application, command: str, handler_func):
    wrapped = user_insertion_middleware(handler_func)
    app.add_handler(CommandHandler(command, wrapped))

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

    
    register_command(app, Commands.START, start)
    register_command(app, Commands.PRINT_GROUP_CHAT_ID, print_group_chat_id)
    register_command(app, Commands.PRINT_USER_ID, print_user_id)
    register_command(app, Commands.TEST_ADMIN, test_admin)

    try:
        app.run_polling()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        # Clean up database connection
        db_manager.disconnect()

if __name__ == "__main__":
    run()

