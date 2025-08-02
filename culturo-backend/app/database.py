"""
Database configuration and session management with Prisma
"""
from prisma import Prisma
import redis
from typing import Generator, Optional
from .config import settings
import logging

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
        prisma.connect()
        # Prisma will handle table creation automatically
        logger.info("Database initialized successfully with Prisma")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    finally:
        prisma.disconnect()


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