"""
Database configuration and session management with Prisma
"""
from prisma import Prisma
import redis
from typing import Generator
from .config import settings

# Create Prisma client
prisma = Prisma()

# Redis client
redis_client = redis.from_url(settings.redis_url, decode_responses=True)


def get_db() -> Generator[Prisma, None, None]:
    """Dependency to get Prisma client"""
    try:
        prisma.connect()
        yield prisma
    finally:
        prisma.disconnect()


def get_redis() -> redis.Redis:
    """Dependency to get Redis client"""
    return redis_client


def init_db():
    """Initialize database with Prisma"""
    try:
        prisma.connect()
        # Prisma will handle table creation automatically
        print("Database initialized successfully with Prisma")
    except Exception as e:
        print(f"Database initialization failed: {e}")
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
        print(f"Database connection failed: {e}")
        return False


def check_redis_connection():
    """Check Redis connection"""
    try:
        redis_client.ping()
        return True
    except Exception as e:
        print(f"Redis connection failed: {e}")
        return False 