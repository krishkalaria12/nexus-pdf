from pymongo import AsyncMongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging

# custom imports
from ..config import MONGO_URI

logger = logging.getLogger(__name__)

def create_mongo_client() -> AsyncMongoClient:
    """Create and return MongoDB client with error handling"""
    try:
        client = AsyncMongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000
        )
        return client
    except Exception as e:
        logger.error(f"Failed to create MongoDB client: {e}")
        raise

mongo_client: AsyncMongoClient = create_mongo_client()

async def test_connection():
    """Test MongoDB connection"""
    try:
        await mongo_client.admin.command('ping')
        logger.info("MongoDB connection successful")
        return True
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"MongoDB connection failed: {e}")
        return False