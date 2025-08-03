from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from config import MONGODB_URI, DATABASE_NAME
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    _instance = None
    _client: MongoClient = None
    _database: Database = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def connect(self):
        """Connect to MongoDB Atlas"""
        try:
            if not MONGODB_URI:
                raise ValueError("MONGODB_URI not found in environment variables")
            
            self._client = MongoClient(MONGODB_URI)
            self._database = self._client[DATABASE_NAME]
            
            # Test the connection
            self._client.admin.command('ping')
            logger.info(f"Successfully connected to MongoDB Atlas database: {DATABASE_NAME}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from MongoDB"""
        if self._client:
            self._client.close()
            logger.info("Disconnected from MongoDB")
    
    def get_database(self) -> Database:
        """Get the database instance"""
        if self._database is None:
            self.connect()
        return self._database
    
    def get_collection(self, collection_name: str) -> Collection:
        """Get a collection from the database"""
        return self.get_database()[collection_name]
    
    def is_connected(self) -> bool:
        """Check if connected to MongoDB"""
        try:
            if self._client:
                self._client.admin.command('ping')
                return True
        except Exception:
            pass
        return False

# Global database manager instance
db_manager = DatabaseManager()

def get_db() -> Database:
    """Get database instance"""
    return db_manager.get_database()

def get_collection(collection_name: str) -> Collection:
    """Get collection instance"""
    return db_manager.get_collection(collection_name)
