"""
Main FastAPI application for Culturo Backend
"""
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
import time
from datetime import datetime

from .config import settings
from .database import init_db, check_db_connection, check_redis_connection
from .routers import auth, stories, food, travel, recommendations, analytics, clerk_webhooks
from .shared.errors import AppError, ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="""
    🌍 Culturo Backend - Comprehensive Cultural Intelligence Platform
    
    A unified platform that combines the best features from multiple Qloo-powered applications:
    
    ## Core Features
    - **Cultural Taste Analysis**: Deep insights into user preferences
    - **AI-Powered Recommendations**: Personalized suggestions using multiple LLMs
    
    - **Story Development**: AI-assisted story creation with audience analysis
    - **Food Intelligence**: Computer vision-based food recognition
    - **Travel Planning**: Culturally-aware trip itineraries
    - **Content Generation**: Create personalized narratives
    
    ## APIs & Services
    - **Qloo Taste API**: Cultural affinity data
    - **Google Gemini**: Primary LLM for content generation
    - **OpenAI GPT**: Alternative LLM for specific tasks
    - **Computer Vision**: Food recognition and analysis
    
    ## Authentication
    - JWT-based authentication
    - User preference management
    - Cultural profile tracking
    
    ## Analytics
    - User behavior tracking
    - Recommendation performance
    - Cultural insights generation
    """,
    version=settings.app_version,
    contact={
        "name": "Culturo Support",
        "url": "https://github.com/your-username/culturo-backend",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware for production
# Temporarily disabled to fix host header issues
# if settings.environment == "production":
#     app.add_middleware(
#         TrustedHostMiddleware,
#         allowed_hosts=[
#             "culturo.com", 
#             "api.culturo.com", 
#             "culturo.onrender.com",
#             "localhost",
#             "127.0.0.1",
#             "0.0.0.0"
#         ]
#     )

# Add Prometheus metrics if enabled
if settings.prometheus_enabled:
    Instrumentator().instrument(app).expose(app, include_in_schema=False)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Timeout middleware for long-running requests
@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    import asyncio
    try:
        # Set a 90-second timeout for all requests
        response = await asyncio.wait_for(call_next(request), timeout=90.0)
        return response
    except asyncio.TimeoutError:
        return JSONResponse(
            status_code=408,
            content={"detail": "Request timeout - the operation took too long to complete"}
        )


# Custom error handler for AppError
@app.exception_handler(AppError)
async def app_exception_handler(request: Request, exc: AppError):
    logger.error(f"App error on {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.error_code or "APP_ERROR",
            message=exc.message,
            error_code=exc.error_code,
            details=exc.details,
            timestamp=datetime.now().isoformat(),
            path=str(request.url.path)
        ).dict()
    )


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred. Please try again later.",
            timestamp=datetime.now().isoformat(),
            path=str(request.url.path)
        ).dict()
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for service monitoring"""
    db_status = check_db_connection()
    redis_status = check_redis_connection()
    
    # Consider service healthy if database is connected, Redis is optional
    status = "healthy" if db_status else "unhealthy"
    
    return {
        "status": status,
        "service": settings.app_name,
        "version": settings.app_version,
        "timestamp": datetime.now().isoformat(),
        "environment": settings.environment,
        "services": {
            "database": "connected" if db_status else "disconnected",
            "redis": "connected" if redis_status else "disconnected"
        }
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": f"🌍 Welcome to {settings.app_name}",
        "description": "Comprehensive Cultural Intelligence Platform",
        "version": settings.app_version,
        "status": "active",
        "environment": settings.environment,
        "docs": "/docs",
        "health": "/health",
        "features": [
            "Cultural Taste Analysis",
            "AI-Powered Recommendations", 
            "Trend Forecasting",
            "Story Development",
            "Food Intelligence",
            "Travel Planning",
            "Content Generation"
        ],
        "apis": {
            "qloo": "Cultural affinity data",
            "gemini": "Content generation",
            "openai": "Alternative LLM",
            "computer_vision": "Food recognition"
        }
    }


# Include routers
app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)



app.include_router(
    stories.router,
    prefix="/api/v1/stories",
    tags=["Story Development"]
)

app.include_router(
    food.router,
    prefix="/api/v1/food",
    tags=["Food Intelligence"]
)

app.include_router(
    travel.router,
    prefix="/api/v1/travel",
    tags=["Travel Planning"]
)

app.include_router(
    recommendations.router,
    prefix="/api/v1/recommendations",
    tags=["Recommendations"]
)

app.include_router(
    analytics.router,
    prefix="/api/v1/analytics",
    tags=["Analytics"]
)

app.include_router(
    clerk_webhooks.router,
    prefix="/api/v1/clerk",
    tags=["Clerk Webhooks"]
)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    
    # Check service connections
    db_status = check_db_connection()
    redis_status = check_redis_connection()
    
    if not db_status:
        logger.error("Database connection failed")
    if not redis_status:
        logger.warning("Redis connection failed - Redis features will be disabled")
    else:
        logger.info("Redis connection established")
    
    logger.info("Application startup completed")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Application shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    ) 