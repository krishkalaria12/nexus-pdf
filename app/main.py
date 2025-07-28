import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn

from .server import app
from .db.client import test_connection as test_mongo_connection
from .queue.queue import test_redis_connection
from .db.collections.files import create_file_indexes
from .config import HOST, PORT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Nexus PDF Processor...")
    
    # Test database connections
    mongo_ok = await test_mongo_connection()
    redis_ok = await test_redis_connection()
    
    if not mongo_ok:
        logger.error("MongoDB connection failed. Application may not work properly.")
    
    if not redis_ok:
        logger.error("Redis connection failed. Queue processing may not work properly.")
    
    # Create database indexes
    try:
        await create_file_indexes()
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Failed to create database indexes: {e}")
    
    logger.info("Nexus PDF Processor started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Nexus PDF Processor...")

# Update app with lifespan
app.router.lifespan_context = lifespan

def main():
    """Main application entry point"""
    try:
        uvicorn.run(
            app, 
            host=HOST, 
            port=PORT,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        raise

if __name__ == "__main__":
    main()
