"""
Culturo - Cultural Intelligence Platform
Unified main entry point for Railway deployment

This file serves as the main entry point for Railway deployment,
handling both the FastAPI backend and serving the React frontend.
"""

import os
import sys
import subprocess
import threading
import time
import logging
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent / "culturo-backend"
sys.path.insert(0, str(backend_path))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def run_backend():
    """Run the FastAPI backend server"""
    try:
        logger.info("Starting FastAPI backend...")
        os.chdir(backend_path)
        
        # Set environment variables for Railway
        os.environ.setdefault("HOST", "0.0.0.0")
        os.environ.setdefault("PORT", "8000")
        os.environ.setdefault("ENVIRONMENT", "production")
        
        # Import and run the FastAPI app
        from app.main import app
        import uvicorn
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Backend startup failed: {e}")
        sys.exit(1)

def run_frontend():
    """Run the React frontend development server"""
    try:
        logger.info("Starting React frontend...")
        frontend_path = Path(__file__).parent / "culturo-frontend"
        os.chdir(frontend_path)
        
        # Install dependencies if node_modules doesn't exist
        if not (frontend_path / "node_modules").exists():
            logger.info("Installing frontend dependencies...")
            subprocess.run(["npm", "install"], check=True)
        
        # Build the frontend for production
        logger.info("Building frontend for production...")
        subprocess.run(["npm", "run", "build"], check=True)
        
        # Serve the built files
        logger.info("Serving frontend build...")
        subprocess.run(["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "3000"], check=True)
        
    except Exception as e:
        logger.error(f"Frontend startup failed: {e}")
        sys.exit(1)

def check_railway_environment():
    """Check if we're running on Railway and set appropriate environment"""
    railway_env = os.environ.get("RAILWAY_ENVIRONMENT")
    if railway_env:
        logger.info(f"Running on Railway environment: {railway_env}")
        
        # Set Railway-specific environment variables
        os.environ.setdefault("ENVIRONMENT", "production")
        os.environ.setdefault("HOST", "0.0.0.0")
        
        # Set database URL for Railway
        railway_postgres_url = os.environ.get("DATABASE_URL")
        if railway_postgres_url:
            os.environ["DATABASE_URL"] = railway_postgres_url
            logger.info("Using Railway PostgreSQL database")
        
        # Set Redis URL for Railway
        railway_redis_url = os.environ.get("REDIS_URL")
        if railway_redis_url:
            os.environ["REDIS_URL"] = railway_redis_url
            logger.info("Using Railway Redis instance")
        
        return True
    return False

def main():
    """Main entry point for the application"""
    logger.info("🌍 Starting Culturo - Cultural Intelligence Platform")
    
    # Check if we're on Railway
    is_railway = check_railway_environment()
    
    if is_railway:
        # On Railway, we'll run the backend and serve the frontend from it
        logger.info("Railway deployment detected - running unified server")
        run_unified_server()
    else:
        # Local development - run both services
        logger.info("Local development detected - running separate services")
        run_development_servers()

def run_unified_server():
    """Run a unified server that serves both backend API and frontend"""
    try:
        # Try the simple server first (most reliable)
        logger.info("Trying simple server...")
        from simple_server import main as simple_main
        simple_main()
    except Exception as e:
        logger.error(f"Simple server failed: {e}")
        # Fallback: try the simplified unified server
        try:
            logger.info("Trying simplified unified server...")
            from unified_server_simple import main as unified_main
            unified_main()
        except Exception as e2:
            logger.error(f"Simplified unified server failed: {e2}")
            # Last resort: try direct backend import
            try:
                logger.info("Trying direct backend import...")
                import sys
                from pathlib import Path
                
                # Add backend to path
                backend_path = Path(__file__).parent / "culturo-backend"
                sys.path.insert(0, str(backend_path))
                
                # Import and run backend directly
                from app.main import app
                import uvicorn
                
                logger.info("Starting backend directly...")
                uvicorn.run(
                    app,
                    host="0.0.0.0",
                    port=int(os.environ.get("PORT", 8000)),
                    log_level="info"
                )
            except Exception as e3:
                logger.error(f"Direct backend import also failed: {e3}")
                sys.exit(1)

def run_development_servers():
    """Run both backend and frontend in development mode"""
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Wait a moment for backend to start
    time.sleep(2)
    
    # Start frontend
    run_frontend()

if __name__ == "__main__":
    main() 