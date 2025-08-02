#!/usr/bin/env python3
"""
Simple Server for Culturo - Direct Backend Import
This server directly imports and runs the FastAPI backend
"""

import os
import sys
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

def main():
    """Main entry point for the simple server"""
    logger.info("🌍 Starting Culturo Simple Server")
    
    try:
        # Set Railway environment variables
        os.environ.setdefault("HOST", "0.0.0.0")
        os.environ.setdefault("PORT", "8000")
        os.environ.setdefault("ENVIRONMENT", "production")
        
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
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error(f"Python path: {sys.path}")
        logger.error(f"Backend path: {backend_path}")
        logger.error(f"Backend path exists: {backend_path.exists()}")
        
        # Try alternative import
        try:
            logger.info("Trying alternative import path...")
            sys.path.insert(0, str(Path(__file__).parent))
            from culturo_backend.app.main import app
            import uvicorn
            
            port = int(os.environ.get("PORT", 8000))
            uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
            
        except ImportError as e2:
            logger.error(f"Alternative import also failed: {e2}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 