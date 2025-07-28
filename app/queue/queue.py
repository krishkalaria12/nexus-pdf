from redis import Redis
from rq import Queue
import logging

# custom imports
from ..config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_USERNAME

logger = logging.getLogger(__name__)

def create_redis_client() -> Redis:
    """Create Redis client with error handling"""
    try:
        redis_client = Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True,
            username=REDIS_USERNAME,
            password=REDIS_PASSWORD,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        return redis_client
    except Exception as e:
        logger.error(f"Failed to create Redis client: {e}")
        raise

def create_queue() -> Queue:
    """Create RQ queue with Redis connection"""
    try:
        redis_client = create_redis_client()
        queue = Queue(connection=redis_client)
        return queue
    except Exception as e:
        logger.error(f"Failed to create queue: {e}")
        raise

redis_client = create_redis_client()
queue = create_queue()

async def test_redis_connection() -> bool:
    """Test Redis connection"""
    try:
        redis_client.ping()
        logger.info("Redis connection successful")
        return True
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        return False