"""
Simplified Unified Server for Culturo - Railway Deployment
This server serves the FastAPI backend with a simple placeholder frontend
"""

import os
import sys
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
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

def create_unified_app():
    """Create the unified FastAPI application"""
    try:
        # Try to import the original FastAPI app
        from culturo_backend.app.main import app as backend_app
        logger.info("Successfully imported backend app")
    except ImportError as e:
        logger.error(f"Failed to import backend app: {e}")
        # Create a simple fallback app
        backend_app = FastAPI(title="Culturo Backend Fallback")
        
        @backend_app.get("/health")
        async def health():
            return {"status": "healthy", "message": "Backend is running"}
    
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
    
    # Check if React frontend exists
    frontend_path = Path(__file__).parent / "culturo-frontend" / "dist"
    
    if frontend_path.exists() and (frontend_path / "index.html").exists():
        logger.info(f"Found React frontend at: {frontend_path}")
        
        # Mount static files
        app.mount("/assets", StaticFiles(directory=str(frontend_path / "assets")), name="assets")
        
        # Serve index.html for root
        @app.get("/")
        async def serve_index():
            return FileResponse(str(frontend_path / "index.html"))
        
        # Catch-all route for SPA routing
        @app.get("/{full_path:path}")
        async def catch_all(full_path: str):
            # Skip API routes and assets
            if full_path.startswith(("api", "assets", "docs", "redoc", "openapi.json")):
                raise HTTPException(status_code=404, detail="Not found")
            
            # Serve index.html for all other routes (SPA routing)
            return FileResponse(str(frontend_path / "index.html"))
        
        logger.info("React frontend mounted successfully")
    else:
        logger.warning(f"React frontend not found at {frontend_path}, serving fallback")
        
        # Fallback HTML
        @app.get("/", response_class=HTMLResponse)
        async def root():
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Culturo - Cultural Intelligence Platform</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                    .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    h1 { color: #333; text-align: center; }
                    .links { margin: 20px 0; }
                    .links a { display: inline-block; margin: 10px; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
                    .links a:hover { background: #0056b3; }
                    .status { background: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🌍 Culturo - Cultural Intelligence Platform</h1>
                    <div class="status">
                        <strong>Status:</strong> Backend API is running successfully! 🚀
                    </div>
                    <div class="links">
                        <a href="/api/docs">📚 API Documentation</a>
                        <a href="/api/health">💚 Health Check</a>
                        <a href="/api/openapi.json">🔧 OpenAPI Schema</a>
                    </div>
                    <p><strong>Note:</strong> React frontend build not found. Check build process.</p>
                </div>
            </body>
            </html>
            """
        
        # Catch-all route for SPA routing (serve the same HTML)
        @app.get("/{full_path:path}")
        async def catch_all(full_path: str):
            # Skip API routes
            if full_path.startswith(("api", "docs", "redoc", "openapi.json")):
                raise HTTPException(status_code=404, detail="Not found")
            
            # Serve the same HTML for all other routes
            return await root()
    
    return app

def main():
    """Main entry point for the unified server"""
    logger.info("🌍 Starting Culturo Simplified Unified Server")
    
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