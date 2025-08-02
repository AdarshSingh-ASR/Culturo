#!/usr/bin/env python3
"""
Test script to verify Prisma CLI functionality
"""

import subprocess
import sys
import os

def test_prisma_cli():
    """Test if Prisma CLI is working correctly"""
    print("🧪 Testing Prisma CLI functionality...")
    
    # Test 1: Check if prisma module can be imported
    try:
        import prisma
        print("✅ Prisma module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import prisma module: {e}")
        return False
    
    # Test 2: Check if prisma CLI is available
    try:
        result = subprocess.run(
            [sys.executable, "-m", "prisma", "--help"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print("✅ Prisma CLI is available and working")
        else:
            print(f"❌ Prisma CLI failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Prisma CLI command timed out")
        return False
    except Exception as e:
        print(f"❌ Error running Prisma CLI: {e}")
        return False
    
    # Test 3: Check if we can generate the client
    try:
        result = subprocess.run(
            [sys.executable, "-m", "prisma", "generate"],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            print("✅ Prisma client generation successful")
        else:
            print(f"❌ Prisma client generation failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Prisma client generation timed out")
        return False
    except Exception as e:
        print(f"❌ Error generating Prisma client: {e}")
        return False
    
    print("✅ All Prisma CLI tests passed!")
    return True

if __name__ == "__main__":
    success = test_prisma_cli()
    sys.exit(0 if success else 1) 