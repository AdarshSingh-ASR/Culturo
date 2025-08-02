#!/usr/bin/env python3
"""
Test script to verify backend imports work correctly
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent / "culturo-backend"
sys.path.insert(0, str(backend_path))

print(f"Python path: {sys.path}")
print(f"Backend path: {backend_path}")
print(f"Backend path exists: {backend_path.exists()}")

try:
    # Test basic import
    print("Testing basic import...")
    from culturo_backend.app.main import app
    print("✅ Successfully imported app from culturo_backend.app.main")
    
    # Test that app is a FastAPI app
    print(f"App type: {type(app)}")
    print(f"App title: {app.title}")
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
    
    # Try alternative import paths
    try:
        print("Trying alternative import path...")
        sys.path.insert(0, str(Path(__file__).parent))
        from culturo_backend.app.main import app
        print("✅ Successfully imported with alternative path")
    except ImportError as e2:
        print(f"❌ Alternative import also failed: {e2}")
        
        try:
            print("Trying direct import...")
            sys.path.insert(0, str(Path(__file__).parent / "culturo-backend"))
            from app.main import app
            print("✅ Successfully imported with direct path")
        except ImportError as e3:
            print(f"❌ Direct import also failed: {e3}")
            sys.exit(1)

print("🎉 All imports successful!") 