"""
Database configuration and session management with Prisma
"""
from prisma import Prisma
import redis
from typing import Generator, Optional
from .config import settings
import logging
import os
import subprocess

logger = logging.getLogger(__name__)

# Create Prisma client
prisma = Prisma()

# Redis client - make it optional
redis_client: Optional[redis.Redis] = None

try:
    redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    # Test connection
    redis_client.ping()
    logger.info("Redis connection established successfully")
except Exception as e:
    logger.warning(f"Redis connection failed: {e}. Redis features will be disabled.")
    redis_client = None


def ensure_prisma_query_engine():
    """Ensure Prisma query engine is available"""
    try:
        # Try to fetch the query engine if it's not found
        result = subprocess.run(
            ["prisma", "py", "fetch"], 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        if result.returncode == 0:
            logger.info("Prisma query engine fetched successfully")
            return True
        else:
            logger.warning(f"Prisma py fetch failed: {result.stderr}")
            return False
    except Exception as e:
        logger.warning(f"Failed to fetch Prisma query engine: {e}")
        return False


def get_db() -> Generator[Prisma, None, None]:
    """Dependency to get Prisma client"""
    try:
        prisma.connect()
        yield prisma
    finally:
        prisma.disconnect()


def get_redis() -> Optional[redis.Redis]:
    """Dependency to get Redis client"""
    return redis_client


def init_db():
    """Initialize database with Prisma"""
    try:
        # Ensure query engine is available
        ensure_prisma_query_engine()
        
        prisma.connect()
        # Prisma will handle table creation automatically
        logger.info("Database initialized successfully with Prisma")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Try to fetch query engine and retry
        if "Expected" in str(e) and "prisma-query-engine" in str(e):
            logger.info("Attempting to fetch Prisma query engine...")
            if ensure_prisma_query_engine():
                try:
                    prisma.connect()
                    logger.info("Database initialized successfully after fetching query engine")
                except Exception as retry_e:
                    logger.error(f"Database initialization still failed after fetching query engine: {retry_e}")
            else:
                logger.error("Failed to fetch Prisma query engine")
    finally:
        try:
            prisma.disconnect()
        except:
            pass


def check_db_connection():
    """Check database connection"""
    try:
        prisma.connect()
        # Test connection with a simple query
        prisma.user.find_first()
        prisma.disconnect()
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        # Try to fetch query engine and retry
        if "Expected" in str(e) and "prisma-query-engine" in str(e):
            logger.info("Attempting to fetch Prisma query engine for connection test...")
            if ensure_prisma_query_engine():
                try:
                    prisma.connect()
                    prisma.user.find_first()
                    prisma.disconnect()
                    return True
                except Exception as retry_e:
                    logger.error(f"Database connection still failed after fetching query engine: {retry_e}")
        return False


def check_redis_connection():
    """Check Redis connection"""
    if redis_client is None:
        return False
    try:
        redis_client.ping()
        return True
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        return False 