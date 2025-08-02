"""
User model for authentication and preferences
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from passlib.context import CryptContext

from ..database import Base

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    """User model for authentication and cultural preferences"""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_id = Column(String(255), unique=True, index=True, nullable=True)  # Clerk user ID
    email = Column(String(255), unique=True, index=True, nullable=True)  # Made nullable for Clerk
    username = Column(String(100), unique=True, index=True, nullable=True)  # Made nullable for Clerk
    hashed_password = Column(String(255), nullable=True)  # Made nullable for Clerk
    first_name = Column(String(100))  # Added for Clerk
    last_name = Column(String(100))  # Added for Clerk
    full_name = Column(String(255))
    profile_image_url = Column(String(500))  # Added for Clerk
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Cultural preferences
    music_preferences = Column(JSON, default=list)
    food_preferences = Column(JSON, default=list)
    fashion_preferences = Column(JSON, default=list)
    book_preferences = Column(JSON, default=list)
    movie_preferences = Column(JSON, default=list)
    travel_preferences = Column(JSON, default=list)
    
    # Profile information
    bio = Column(Text)
    location = Column(String(255))
    birth_year = Column(String(4))
    gender = Column(String(50))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def update_preferences(self, preference_type: str, preferences: list):
        """Update user preferences"""
        if hasattr(self, preference_type):
            setattr(self, preference_type, preferences)
    
    def get_preferences(self, preference_type: str) -> list:
        """Get user preferences by type"""
        return getattr(self, preference_type, [])
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            "id": str(self.id),
            "clerk_id": self.clerk_id,
            "email": self.email,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "profile_image_url": self.profile_image_url,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "music_preferences": self.music_preferences,
            "food_preferences": self.food_preferences,
            "fashion_preferences": self.fashion_preferences,
            "book_preferences": self.book_preferences,
            "movie_preferences": self.movie_preferences,
            "travel_preferences": self.travel_preferences,
            "bio": self.bio,
            "location": self.location,
            "birth_year": self.birth_year,
            "gender": self.gender,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        } 