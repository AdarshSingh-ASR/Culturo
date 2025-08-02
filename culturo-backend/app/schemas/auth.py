from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime

# JWT Authentication Schemas
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    music_preferences: Optional[list[str]] = []
    food_preferences: Optional[list[str]] = []
    fashion_preferences: Optional[list[str]] = []
    book_preferences: Optional[list[str]] = []
    movie_preferences: Optional[list[str]] = []
    travel_preferences: Optional[list[str]] = []

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    music_preferences: list[str] = []
    food_preferences: list[str] = []
    fashion_preferences: list[str] = []
    book_preferences: list[str] = []
    movie_preferences: list[str] = []
    travel_preferences: list[str] = []

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    email: Optional[str] = None

class UserPreferencesUpdate(BaseModel):
    music_preferences: Optional[list[str]] = None
    food_preferences: Optional[list[str]] = None
    fashion_preferences: Optional[list[str]] = None
    book_preferences: Optional[list[str]] = None
    movie_preferences: Optional[list[str]] = None
    travel_preferences: Optional[list[str]] = None

# Clerk Authentication Schemas
class ClerkUser(BaseModel):
    id: str
    email_addresses: list[Dict[str, Any]]
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    image_url: Optional[str] = None
    created_at: int
    updated_at: int

class ClerkWebhookEvent(BaseModel):
    type: str
    data: Dict[str, Any]
    object: str
    created_at: int

class ClerkSession(BaseModel):
    id: str
    user_id: str
    status: str
    expire_at: int
    last_active_at: int
    created_at: int
    updated_at: int

class ClerkAuthResponse(BaseModel):
    user: ClerkUser
    session: Optional[ClerkSession] = None
    token: Optional[str] = None

# Password Reset Schemas
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

# Profile Update Schemas
class ProfileUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None

# OAuth Schemas (for future social login integration)
class OAuthProvider(BaseModel):
    provider: str  # google, github, etc.
    provider_user_id: str
    email: EmailStr
    name: Optional[str] = None
    picture: Optional[str] = None

class OAuthLogin(BaseModel):
    provider: str
    code: str
    redirect_uri: str 