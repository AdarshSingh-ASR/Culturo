"""
Configuration settings for Culturo Backend
"""
import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    app_name: str = "Culturo Backend"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Database
    database_url: str = Field(env="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # API Keys
    qloo_api_key: Optional[str] = Field(default=None, env="QLOO_API_KEY")
    qloo_api_url: str = Field(default="https://api.qloo.com/v1", env="QLOO_API_URL")
    gemini_api_key: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openrouter_api_key: Optional[str] = Field(default=None, env="OPENROUTER_API_KEY")
    
    # Authentication
    secret_key: Optional[str] = Field(default="your_super_secret_key_here_make_it_long_and_random", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Clerk Authentication
    clerk_secret_key: str = Field(env="CLERK_SECRET_KEY")
    clerk_publishable_key: Optional[str] = Field(default=None, env="CLERK_PUBLISHABLE_KEY")
    clerk_jwt_issuer: str = Field(env="CLERK_JWT_ISSUER")
    clerk_webhook_secret: Optional[str] = Field(default=None, env="CLERK_WEBHOOK_SECRET")
    
    # External APIs
    google_places_api_key: Optional[str] = Field(default=None, env="GOOGLE_PLACES_API_KEY")
    google_vision_api_key: Optional[str] = Field(default=None, env="GOOGLE_VISION_API_KEY")
    openweather_api_key: Optional[str] = Field(default=None, env="OPENWEATHER_API_KEY")
    
    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000"],
        env="CORS_ORIGINS"
    )
    
    # Monitoring
    prometheus_enabled: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    
    # ML Models
    food_model_path: str = Field(default="./app/ml/models/food101", env="FOOD_MODEL_PATH")
    
    # Cache
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")  # 1 hour
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    
    # File Upload
    max_file_size: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    allowed_image_types: List[str] = Field(
        default=["image/jpeg", "image/png", "image/webp"],
        env="ALLOWED_IMAGE_TYPES"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env file


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings 