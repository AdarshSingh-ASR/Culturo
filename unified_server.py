"""
Unified Server for Culturo - Railway Deployment
This server combines FastAPI backend with React frontend serving
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Add the backend directory to Python path
backend_path = Path(__file__).parent / "culturo-backend"
sys.path.insert(0, str(backend_path))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def build_frontend():
    """Build the React frontend for production"""
    try:
        logger.info("Building React frontend...")
        frontend_path = Path(__file__).parent / "culturo-frontend"
        
        # Install dependencies if needed
        if not (frontend_path / "node_modules").exists():
            logger.info("Installing frontend dependencies...")
            subprocess.run(["npm", "install"], cwd=frontend_path, check=True)
        
        # Build the frontend
        logger.info("Building frontend for production...")
        subprocess.run(["npm", "run", "build"], cwd=frontend_path, check=True)
        
        return frontend_path / "dist"
    except Exception as e:
        logger.error(f"Frontend build failed: {e}")
        return None

def create_unified_app():
    """Create the unified FastAPI application"""
    # Import the original FastAPI app
    from culturo_backend.app.main import app as backend_app
    
    # Create a new FastAPI app for the unified server
    app = FastAPI(
        title="Culturo - Cultural Intelligence Platform",
        description="Unified server for Culturo backend API and frontend",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include all backend routes with /api prefix
    app.mount("/api", backend_app)
    
    # Build and serve frontend
    frontend_build_path = build_frontend()
    
    if frontend_build_path and frontend_build_path.exists():
        # Mount static files
        app.mount("/assets", StaticFiles(directory=str(frontend_build_path / "assets")), name="assets")
        
        # Serve index.html for root and other frontend routes
        @app.get("/")
        async def serve_index():
            return FileResponse(str(frontend_build_path / "index.html"))
        
        # Catch-all route for SPA routing
        @app.get("/{full_path:path}")
        async def catch_all(full_path: str):
            # Skip API routes and assets
            if full_path.startswith(("api", "assets", "docs", "redoc", "openapi.json")):
                raise HTTPException(status_code=404, detail="Not found")
            
            # Serve index.html for all other routes (SPA routing)
            return FileResponse(str(frontend_build_path / "index.html"))
        
        logger.info(f"Frontend mounted successfully from: {frontend_build_path}")
    else:
        logger.warning("Frontend build not found, serving API only")
        
        @app.get("/")
        async def root():
            return {
                "message": "Culturo API Server",
                "docs": "/api/docs",
                "health": "/api/health"
            }
    
    return app

def main():
    """Main entry point for the unified server"""
    logger.info("🌍 Starting Culturo Unified Server")
    
    # Set Railway environment variables
    os.environ.setdefault("HOST", "0.0.0.0")
    os.environ.setdefault("PORT", "8000")
    os.environ.setdefault("ENVIRONMENT", "production")
    
    # Create the unified app
    app = create_unified_app()
    
    # Get port from environment
    port = int(os.environ.get("PORT", 8000))
    
    logger.info(f"Starting unified server on port {port}")
    
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main() 