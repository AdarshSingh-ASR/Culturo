from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from typing import Optional, Any
import jwt
import httpx
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from ..database import get_db
from ..schemas.auth import (
    UserCreate, UserLogin, UserResponse, Token, UserPreferencesUpdate,
    ClerkUser, ClerkWebhookEvent, ClerkAuthResponse, PasswordResetRequest,
    PasswordResetConfirm, ProfileUpdate
)
from ..config import settings
from ..dependencies import get_current_user, get_current_user_jwt, get_optional_user, get_current_clerk_user

router = APIRouter()
security = HTTPBearer()

# Clerk configuration
CLERK_API_URL = "https://api.clerk.dev/v1"
CLERK_WEBHOOK_SECRET = settings.clerk_webhook_secret

class AuthService:
    def __init__(self, db):
        self.db = db

    def create_user(self, user_data: UserCreate) -> Any:
        """Create a new user with JWT authentication"""
        # Check if user already exists
        existing_user = self.db.user.find_first(
            where={
                "OR": [
                    {"email": user_data.email},
                    {"username": user_data.username}
                ]
            }
        )
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or username already exists"
            )

        # Create new user
        user = self.db.user.create(
            data={
                "email": user_data.email,
                "username": user_data.username,
                "full_name": user_data.full_name
            }
        )
        
        # Create user preferences if provided
        if any([
            user_data.music_preferences,
            user_data.food_preferences,
            user_data.fashion_preferences,
            user_data.book_preferences,
            user_data.movie_preferences,
            user_data.travel_preferences
        ]):
            cultural_tastes = {
                "music": user_data.music_preferences or [],
                "food": user_data.food_preferences or [],
                "fashion": user_data.fashion_preferences or [],
                "books": user_data.book_preferences or [],
                "movies": user_data.movie_preferences or []
            }
            
            self.db.userpreference.create(
                data={
                    "user_id": user.id,
                    "cultural_tastes": cultural_tastes,
                    "travel_preferences": user_data.travel_preferences or {}
                }
            )
        
        return user

    def authenticate_user(self, email: str, password: str) -> Any:
        """Authenticate user with email and password"""
        user = self.db.user.find_first(where={"email": email})
        if not user:
            return None
        # Note: Password verification is handled by Clerk authentication
        # This method is kept for compatibility but not used in the current Clerk-based auth flow
        return user

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            return payload
        except jwt.PyJWTError:
            return None

    async def verify_clerk_token(self, token: str) -> Optional[ClerkUser]:
        """Verify Clerk JWT token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{CLERK_API_URL}/sessions/{token}/verify",
                    headers={"Authorization": f"Bearer {settings.clerk_secret_key}"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return ClerkUser(**data)
                return None
        except Exception:
            return None

    async def get_clerk_user(self, user_id: str) -> Optional[ClerkUser]:
        """Get Clerk user by ID"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{CLERK_API_URL}/users/{user_id}",
                    headers={"Authorization": f"Bearer {settings.clerk_secret_key}"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return ClerkUser(**data)
                return None
        except Exception:
            return None

    def get_or_create_user_from_clerk(self, clerk_user: ClerkUser) -> Any:
        """Get existing user or create new user from Clerk data"""
        # Try to find user by Clerk ID first
        user = self.db.user.find_first(where={"clerk_id": clerk_user.id})
        
        if not user:
            # Try to find by email
            email = clerk_user.email_addresses[0]["email_address"] if clerk_user.email_addresses else None
            if email:
                user = self.db.user.find_first(where={"email": email})
            
            if not user:
                # Create new user
                user = self.db.user.create(
                    data={
                        "clerk_id": clerk_user.id,
                        "email": email,
                        "username": clerk_user.username or f"user_{clerk_user.id[:8]}",
                        "full_name": f"{clerk_user.first_name or ''} {clerk_user.last_name or ''}".strip(),
                        "is_active": True
                    }
                )
        
        return user

    def update_user_preferences(self, user_id: str, preferences: UserPreferencesUpdate) -> Any:
        """Update user preferences"""
        user = self.db.user.find_first(where={"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if user preferences exist
        user_preferences = self.db.userpreference.find_first(where={"user_id": user_id})
        
        # Prepare cultural tastes data
        cultural_tastes = {}
        if preferences.music_preferences is not None:
            cultural_tastes["music"] = preferences.music_preferences
        if preferences.food_preferences is not None:
            cultural_tastes["food"] = preferences.food_preferences
        if preferences.fashion_preferences is not None:
            cultural_tastes["fashion"] = preferences.fashion_preferences
        if preferences.book_preferences is not None:
            cultural_tastes["books"] = preferences.book_preferences
        if preferences.movie_preferences is not None:
            cultural_tastes["movies"] = preferences.movie_preferences
        
        # Prepare travel preferences
        travel_preferences = {}
        if preferences.travel_preferences is not None:
            travel_preferences = preferences.travel_preferences
        
        if user_preferences:
            # Update existing preferences
            update_data = {}
            if cultural_tastes:
                update_data["cultural_tastes"] = cultural_tastes
            if travel_preferences:
                update_data["travel_preferences"] = travel_preferences
            
            if update_data:
                self.db.userpreference.update(
                    where={"user_id": user_id},
                    data=update_data
                )
        else:
            # Create new preferences
            self.db.userpreference.create(
                data={
                    "user_id": user_id,
                    "cultural_tastes": cultural_tastes,
                    "travel_preferences": travel_preferences
                }
            )
        
        return user

# JWT Authentication Endpoints
@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db = Depends(get_db)):
    """Register a new user with JWT authentication"""
    auth_service = AuthService(db)
    user = auth_service.create_user(user_data)
    return user

@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db = Depends(get_db)):
    """Login with email and password"""
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(user_credentials.email, user_credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60
    }

@router.get("/profile", response_model=UserResponse)
def get_profile(current_user = Depends(get_current_user_jwt)):
    """Get current user profile"""
    return current_user

@router.put("/preferences", response_model=UserResponse)
def update_preferences(
    preferences: UserPreferencesUpdate,
    current_user = Depends(get_current_user_jwt),
    db = Depends(get_db)
):
    """Update user preferences"""
    auth_service = AuthService(db)
    return auth_service.update_user_preferences(current_user.id, preferences)

# Clerk Authentication Endpoints
@router.post("/clerk/verify")
async def verify_clerk_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_db)
):
    """Verify Clerk token and return user data"""
    auth_service = AuthService(db)
    clerk_user = await auth_service.verify_clerk_token(credentials.credentials)
    
    if not clerk_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Clerk token"
        )
    
    user = auth_service.get_or_create_user_from_clerk(clerk_user)
    return {"user": user, "clerk_user": clerk_user}

@router.post("/clerk/webhook")
async def clerk_webhook(request: Request, db = Depends(get_db)):
    """Handle Clerk webhook events"""
    try:
        # Verify webhook signature
        signature = request.headers.get("svix-signature")
        timestamp = request.headers.get("svix-timestamp")
        webhook_id = request.headers.get("svix-id")
        
        if not all([signature, timestamp, webhook_id]):
            raise HTTPException(status_code=400, detail="Missing webhook headers")
        
        # Verify webhook signature (implement proper verification)
        # This is a simplified version - implement proper signature verification
        
        body = await request.body()
        event_data = json.loads(body)
        
        auth_service = AuthService(db)
        event_type = event_data.get("type")
        
        if event_type == "user.created":
            # Handle user creation
            user_data = event_data.get("data", {})
            clerk_user = ClerkUser(**user_data)
            user = auth_service.get_or_create_user_from_clerk(clerk_user)
            
        elif event_type == "user.updated":
            # Handle user updates
            user_data = event_data.get("data", {})
            clerk_user = ClerkUser(**user_data)
            user = auth_service.get_or_create_user_from_clerk(clerk_user)
            
        elif event_type == "user.deleted":
            # Handle user deletion
            user_id = event_data.get("data", {}).get("id")
            if user_id:
                user = db.user.find_first(where={"clerk_id": user_id})
                if user:
                    db.user.update(
                        where={"clerk_id": user_id},
                        data={"is_active": False}
                    )
        
        return {"status": "success"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook processing failed: {str(e)}")

@router.get("/clerk/profile")
async def get_clerk_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_db)
):
    """Get user profile from Clerk token"""
    auth_service = AuthService(db)
    clerk_user = await auth_service.verify_clerk_token(credentials.credentials)
    
    if not clerk_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Clerk token"
        )
    
    user = auth_service.get_or_create_user_from_clerk(clerk_user)
    return user


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user = Depends(get_current_user)
):
    """Get current user profile using Clerk authentication"""
    return current_user


@router.get("/clerk/me")
async def get_clerk_user_info(
    clerk_user: dict = Depends(get_current_clerk_user)
):
    """Get current Clerk user information"""
    return clerk_user

# Password Reset Endpoints
@router.post("/password-reset-request")
def request_password_reset(request: PasswordResetRequest, db = Depends(get_db)):
    """Request password reset"""
    user = db.user.find_first(where={"email": request.email})
    if user:
        # Generate reset token and send email
        # This is a placeholder - implement actual email sending
        pass
    
    # Always return success to prevent email enumeration
    return {"message": "If the email exists, a password reset link has been sent"}

@router.post("/password-reset-confirm")
def confirm_password_reset(confirm: PasswordResetConfirm, db = Depends(get_db)):
    """Confirm password reset with token"""
    # Verify reset token and update password
    # This is a placeholder - implement actual token verification
    pass

# Profile Management
@router.put("/profile", response_model=UserResponse)
def update_profile(
    profile_data: ProfileUpdate,
    current_user = Depends(get_current_user_jwt),
    db = Depends(get_db)
):
    """Update user profile"""
    if profile_data.username:
        # Check if username is already taken
        existing_user = db.user.find_first(
            where={
                "username": profile_data.username,
                "NOT": {"id": current_user.id}
            }
        )
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")
    
    # Prepare update data
    update_data = {}
    if profile_data.username:
        update_data["username"] = profile_data.username
    if profile_data.full_name is not None:
        update_data["full_name"] = profile_data.full_name
    
    # Update user
    user = db.user.update(
        where={"id": current_user.id},
        data=update_data
    )
    return user

# Health Check
@router.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()} 