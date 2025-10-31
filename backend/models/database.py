from pymongo import MongoClient
from config.settings import settings
from loguru import logger

class Database:
    client: MongoClient = None
    database = None

db = Database()

def connect_to_mongo():
    """Create database connection"""
    try:
        db.client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=2000)
        # Test the connection
        db.client.admin.command('ping')
        db.database = db.client[settings.DATABASE_NAME]
        logger.info(f"Connected to MongoDB: {settings.DATABASE_NAME}")
    except Exception as e:
        logger.warning(f"MongoDB not available: {e}. Running without database.")
        # Don't raise - allow the app to run without MongoDB

def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("Disconnected from MongoDB")

def get_database():
    """Get database instance"""
    return db.database