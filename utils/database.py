from mongoengine import connect, disconnect, get_connection
from config import MONGODB_URI, DATABASE_NAME
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    _instance = None
    _connected = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def connect(self):
        """Connect to MongoDB using MongoEngine"""
        if not self._connected:
            try:
                if not MONGODB_URI:
                    raise ValueError("MONGODB_URI not found in environment variables")

                connect(
                    db=DATABASE_NAME,
                    host=MONGODB_URI,
                    alias="default"
                )
                logger.info(f"Successfully connected to MongoDB Atlas with MongoEngine: {DATABASE_NAME}")
                self._connected = True

            except Exception as e:
                logger.error(f"Failed to connect to MongoDB with MongoEngine: {e}")
                raise
        else:
            logger.info("Already connected to MongoDB")

    def disconnect(self):
        """Disconnect from MongoDB"""
        try:
            disconnect(alias="default")
            self._connected = False
            logger.info("Disconnected from MongoDB (MongoEngine)")
        except Exception as e:
            logger.warning(f"Error disconnecting MongoEngine: {e}")

    def is_connected(self) -> bool:
        """Check if connection is live"""
        try:
            get_connection()
            return True
        except Exception:
            return False

# Global instance
db_manager = DatabaseManager()
