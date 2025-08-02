"""
Custom error classes and exception handlers for the Culturo API
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from pydantic import BaseModel


class AppError(Exception):
    """Base application error class"""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(AppError):
    """Validation error for invalid input data"""
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details={"field": field, **details} if details else {"field": field}
        )


class AuthenticationError(AppError):
    """Authentication error"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_ERROR"
        )


class AuthorizationError(AppError):
    """Authorization error"""
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTHORIZATION_ERROR"
        )


class NotFoundError(AppError):
    """Resource not found error"""
    def __init__(self, resource: str, resource_id: Optional[str] = None):
        message = f"{resource} not found"
        if resource_id:
            message += f" with id: {resource_id}"
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND_ERROR",
            details={"resource": resource, "resource_id": resource_id}
        )


class ExternalServiceError(AppError):
    """External service error (Qloo, LLM, etc.)"""
    def __init__(self, service: str, message: str, original_error: Optional[str] = None):
        super().__init__(
            message=f"{service} service error: {message}",
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service, "original_error": original_error}
        )


class RateLimitError(AppError):
    """Rate limiting error"""
    def __init__(self, service: str, retry_after: Optional[int] = None):
        super().__init__(
            message=f"Rate limit exceeded for {service}",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_ERROR",
            details={"service": service, "retry_after": retry_after}
        )


class DatabaseError(AppError):
    """Database operation error"""
    def __init__(self, operation: str, message: str, original_error: Optional[str] = None):
        super().__init__(
            message=f"Database {operation} failed: {message}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            details={"operation": operation, "original_error": original_error}
        )


class LLMServiceError(AppError):
    """LLM service error"""
    def __init__(self, provider: str, message: str, original_error: Optional[str] = None):
        super().__init__(
            message=f"{provider} LLM service error: {message}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="LLM_SERVICE_ERROR",
            details={"provider": provider, "original_error": original_error}
        )


class QlooServiceError(AppError):
    """Qloo API service error"""
    def __init__(self, endpoint: str, message: str, status_code: Optional[int] = None):
        super().__init__(
            message=f"Qloo {endpoint} error: {message}",
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_code="QLOO_SERVICE_ERROR",
            details={"endpoint": endpoint, "qloo_status_code": status_code}
        )


# Error response models
class ErrorResponse(BaseModel):
    """Standard error response format"""
    error: str
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: str
    path: str


class ValidationErrorResponse(BaseModel):
    """Validation error response format"""
    error: str = "Validation Error"
    message: str
    details: Dict[str, Any]
    timestamp: str
    path: str 