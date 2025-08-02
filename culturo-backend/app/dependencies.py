"""
Dependency injection utilities for FastAPI
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from prisma import Prisma
from jose import JWTError, jwt
from typing import Optional
import redis
import requests
import json
import logging

from .database import get_db, get_redis
from .config import settings

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()


def verify_clerk_token(token: str) -> dict:
    """Verify Clerk JWT token and return payload"""
    try:
        # Decode the JWT token using Clerk's public key
        payload = jwt.decode(
            token,
            settings.clerk_secret_key,
            algorithms=["RS256"],
            audience="https://clerk.culturo.com",
            issuer=settings.clerk_jwt_issuer
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )


def get_clerk_user_info(user_id: str) -> dict:
    """Get user information from Clerk API"""
    headers = {
        "Authorization": f"Bearer {settings.clerk_secret_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"https://api.clerk.com/v1/users/{user_id}",
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user info from Clerk: {str(e)}"
        )


def get_current_user_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Prisma = Depends(get_db)
):
    """Get current authenticated user using JWT"""
    try:
        # Verify JWT token
        payload = jwt.decode(
            credentials.credentials,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        user_email = payload.get("sub")
        
        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Get user from database
        user = db.user.find_first(where={"email": user_email})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}"
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Prisma = Depends(get_db)
):
    """Get current authenticated user using Clerk"""
    try:
        # Verify Clerk token
        payload = verify_clerk_token(credentials.credentials)
        clerk_user_id = payload.get("sub")
        
        if not clerk_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Get or create user in our database
        user = db.user.find_first(where={"clerk_id": clerk_user_id})
        
        if not user:
            # Create new user from Clerk data
            clerk_user_info = get_clerk_user_info(clerk_user_id)
            
            user = db.user.create(
                data={
                    "clerk_id": clerk_user_id,
                    "email": clerk_user_info.get("email_addresses", [{}])[0].get("email_address"),
                    "first_name": clerk_user_info.get("first_name"),
                    "last_name": clerk_user_info.get("last_name"),
                    "username": clerk_user_info.get("username"),
                    "profile_image_url": clerk_user_info.get("image_url"),
                    "is_active": True
                }
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Prisma = Depends(get_db)
):
    """Get current user if authenticated using Clerk, otherwise return None"""
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None


def get_optional_user_no_auth(
    db: Prisma = Depends(get_db)
):
    """Get current user if authenticated using Clerk, otherwise return a default user - no auth required"""
    try:
        # Try to get the first user from the database as a fallback
        user = db.user.find_first()
        if user:
            return user
        
        # If no users exist, return None
        return None
    except Exception as e:
        print(f"Error in get_optional_user_no_auth: {e}")
        return None


def get_current_clerk_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Get current Clerk user information without database lookup"""
    try:
        payload = verify_clerk_token(credentials.credentials)
        clerk_user_id = payload.get("sub")
        
        if not clerk_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        return get_clerk_user_info(clerk_user_id)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )


def get_redis_client() -> Optional[redis.Redis]:
    """Get Redis client dependency"""
    return get_redis()


def rate_limit_check(
    user_id: Optional[str] = None,
    redis_client: Optional[redis.Redis] = Depends(get_redis_client)
) -> bool:
    """Check rate limiting for API endpoints"""
    if not user_id:
        return True
    
    # If Redis is not available, skip rate limiting
    if redis_client is None:
        logger.warning("Redis not available, skipping rate limiting")
        return True
    
    try:
        key = f"rate_limit:{user_id}"
        current_count = redis_client.get(key)
        
        if current_count is None:
            redis_client.setex(key, 60, 1)  # 1 minute TTL
            return True
        
        count = int(current_count)
        if count >= settings.rate_limit_per_minute:
            return False
        
        redis_client.incr(key)
        return True
    except Exception as e:
        logger.error(f"Rate limiting error: {e}")
        # If Redis fails, allow the request
        return True 