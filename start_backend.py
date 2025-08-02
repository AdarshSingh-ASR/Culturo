#!/usr/bin/env python3
"""
Explicit Backend Startup Script for Railway
This is the main entry point for the Culturo backend on Railway
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the backend server"""
    logger.info("🚀 Starting Culturo Backend Server")
    
    try:
        # Set Railway environment variables
        os.environ.setdefault("HOST", "0.0.0.0")
        os.environ.setdefault("PORT", "8000")
        os.environ.setdefault("ENVIRONMENT", "production")
        
        # Add the backend directory to Python path
        backend_path = Path(__file__).parent / "culturo-backend"
        sys.path.insert(0, str(backend_path))
        
        # Import the FastAPI app directly
        logger.info("Importing FastAPI app...")
        from app.main import app
        
        # Get port from environment
        port = int(os.environ.get("PORT", 8000))
        
        logger.info(f"Starting server on port {port}")
        
        # Import uvicorn and run
        import uvicorn
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 