"""
Validation utilities for input validation and data sanitization
"""
import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from ..shared.errors import ValidationError


class InputValidator:
    """Utility class for input validation"""
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email format"""
        if not email:
            raise ValidationError("Email is required", "email")
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError("Invalid email format", "email")
        
        return email.lower().strip()
    
    @staticmethod
    def validate_password(password: str) -> str:
        """Validate password strength"""
        if not password:
            raise ValidationError("Password is required", "password")
        
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long", "password")
        
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain at least one uppercase letter", "password")
        
        if not re.search(r'[a-z]', password):
            raise ValidationError("Password must contain at least one lowercase letter", "password")
        
        if not re.search(r'\d', password):
            raise ValidationError("Password must contain at least one number", "password")
        
        return password
    
    @staticmethod
    def validate_username(username: str) -> str:
        """Validate username format"""
        if not username:
            raise ValidationError("Username is required", "username")
        
        if len(username) < 3:
            raise ValidationError("Username must be at least 3 characters long", "username")
        
        if len(username) > 30:
            raise ValidationError("Username must be less than 30 characters", "username")
        
        username_pattern = r'^[a-zA-Z0-9_-]+$'
        if not re.match(username_pattern, username):
            raise ValidationError("Username can only contain letters, numbers, underscores, and hyphens", "username")
        
        return username.lower().strip()
    
    @staticmethod
    def validate_destination(destination: str) -> str:
        """Validate destination name"""
        if not destination:
            raise ValidationError("Destination is required", "destination")
        
        if len(destination) < 2:
            raise ValidationError("Destination must be at least 2 characters long", "destination")
        
        if len(destination) > 100:
            raise ValidationError("Destination must be less than 100 characters", "destination")
        
        return destination.strip()
    
    @staticmethod
    def validate_travel_style(style: str) -> str:
        """Validate travel style"""
        valid_styles = [
            "cultural", "adventure", "relaxing", "luxury", "budget",
            "family", "romantic", "business", "educational", "wellness"
        ]
        
        if style and style.lower() not in valid_styles:
            raise ValidationError(
                f"Invalid travel style. Must be one of: {', '.join(valid_styles)}", 
                "travel_style"
            )
        
        return style.lower() if style else "cultural"
    
    @staticmethod
    def validate_duration(duration: str) -> str:
        """Validate travel duration"""
        if not duration:
            return "1 week"
        
        duration_pattern = r'^\d+\s*(day|days|week|weeks|month|months)$'
        if not re.match(duration_pattern, duration.lower()):
            raise ValidationError(
                "Invalid duration format. Use format like '5 days', '2 weeks', '1 month'", 
                "duration"
            )
        
        return duration.strip()
    
    @staticmethod
    def validate_cultural_interests(interests: List[str]) -> List[str]:
        """Validate cultural interests list"""
        if not isinstance(interests, list):
            raise ValidationError("Cultural interests must be a list", "cultural_interests")
        
        validated_interests = []
        for interest in interests:
            if isinstance(interest, str) and interest.strip():
                validated_interests.append(interest.strip())
        
        return validated_interests
    
    @staticmethod
    def validate_topic(topic: str) -> str:
        """Validate trend analysis topic"""
        if not topic:
            raise ValidationError("Topic is required", "topic")
        
        if len(topic) < 2:
            raise ValidationError("Topic must be at least 2 characters long", "topic")
        
        if len(topic) > 200:
            raise ValidationError("Topic must be less than 200 characters", "topic")
        
        return topic.strip()
    
    @staticmethod
    def validate_timeframe(timeframe: str) -> str:
        """Validate trend analysis timeframe"""
        valid_timeframes = ["short_term", "medium_term", "long_term"]
        
        if timeframe not in valid_timeframes:
            raise ValidationError(
                f"Invalid timeframe. Must be one of: {', '.join(valid_timeframes)}", 
                "timeframe"
            )
        
        return timeframe
    
    @staticmethod
    def validate_story_prompt(prompt: str) -> str:
        """Validate story generation prompt"""
        if not prompt:
            raise ValidationError("Story prompt is required", "story_prompt")
        
        if len(prompt) < 10:
            raise ValidationError("Story prompt must be at least 10 characters long", "story_prompt")
        
        if len(prompt) > 1000:
            raise ValidationError("Story prompt must be less than 1000 characters", "story_prompt")
        
        return prompt.strip()
    
    @staticmethod
    def validate_genre(genre: str) -> str:
        """Validate story genre"""
        valid_genres = [
            "fantasy", "mystery", "romance", "sci-fi", "thriller", "historical",
            "adventure", "comedy", "drama", "horror", "western", "literary"
        ]
        
        if genre and genre.lower() not in valid_genres:
            raise ValidationError(
                f"Invalid genre. Must be one of: {', '.join(valid_genres)}", 
                "genre"
            )
        
        return genre.lower() if genre else "adventure"
    
    @staticmethod
    def validate_file_size(file_size: int, max_size_mb: int = 10) -> None:
        """Validate file size"""
        max_size_bytes = max_size_mb * 1024 * 1024
        
        if file_size > max_size_bytes:
            raise ValidationError(
                f"File size must be less than {max_size_mb}MB", 
                "file_size"
            )
    
    @staticmethod
    def validate_file_type(filename: str, allowed_extensions: List[str]) -> None:
        """Validate file type"""
        if not filename:
            raise ValidationError("Filename is required", "filename")
        
        file_extension = filename.lower().split('.')[-1] if '.' in filename else ''
        
        if file_extension not in allowed_extensions:
            raise ValidationError(
                f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}", 
                "file_type"
            )
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = 1000) -> str:
        """Sanitize text input"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        sanitized = re.sub(r'\s+', ' ', text.strip())
        
        # Truncate if too long
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length] + "..."
        
        return sanitized
    
    @staticmethod
    def validate_date_range(start_date: Optional[date], end_date: Optional[date]) -> None:
        """Validate date range"""
        if start_date and end_date and start_date > end_date:
            raise ValidationError("Start date must be before end date", "date_range")
        
        if start_date and start_date < date.today():
            raise ValidationError("Start date cannot be in the past", "start_date")
    
    @staticmethod
    def validate_pagination_params(page: int, page_size: int) -> None:
        """Validate pagination parameters"""
        if page < 1:
            raise ValidationError("Page number must be greater than 0", "page")
        
        if page_size < 1 or page_size > 100:
            raise ValidationError("Page size must be between 1 and 100", "page_size")


# Convenience functions for common validations
def validate_user_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate user registration/update input"""
    validated = {}
    
    if "email" in data:
        validated["email"] = InputValidator.validate_email(data["email"])
    
    if "password" in data:
        validated["password"] = InputValidator.validate_password(data["password"])
    
    if "username" in data:
        validated["username"] = InputValidator.validate_username(data["username"])
    
    if "full_name" in data:
        validated["full_name"] = InputValidator.sanitize_text(data["full_name"], 100)
    
    return validated


def validate_travel_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate travel planning input"""
    validated = {}
    
    if "destination" in data:
        validated["destination"] = InputValidator.validate_destination(data["destination"])
    
    if "travel_style" in data:
        validated["travel_style"] = InputValidator.validate_travel_style(data["travel_style"])
    
    if "duration" in data:
        validated["duration"] = InputValidator.validate_duration(data["duration"])
    
    if "cultural_interests" in data:
        validated["cultural_interests"] = InputValidator.validate_cultural_interests(data["cultural_interests"])
    
    return validated


def validate_trend_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate trend analysis input"""
    validated = {}
    
    if "topic" in data:
        validated["topic"] = InputValidator.validate_topic(data["topic"])
    
    if "timeframe" in data:
        validated["timeframe"] = InputValidator.validate_timeframe(data["timeframe"])
    
    if "industry" in data:
        validated["industry"] = InputValidator.sanitize_text(data["industry"], 100)
    
    return validated


def validate_story_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate story generation input"""
    validated = {}
    
    if "story_prompt" in data:
        validated["story_prompt"] = InputValidator.validate_story_prompt(data["story_prompt"])
    
    if "genre" in data:
        validated["genre"] = InputValidator.validate_genre(data["genre"])
    
    if "target_audience" in data:
        validated["target_audience"] = InputValidator.sanitize_text(data["target_audience"], 200)
    
    return validated 