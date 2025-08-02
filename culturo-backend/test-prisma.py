#!/usr/bin/env python3
"""
Test script to verify Prisma setup
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and return success status"""
    try:
        print(f"🔍 Testing: {description}")
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ {description} - SUCCESS")
        if result.stdout.strip():
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"   Error: {e.stderr.strip()}")
        return False
    except FileNotFoundError:
        print(f"❌ {description} - COMMAND NOT FOUND")
        return False

def main():
    print("🧪 Testing Prisma Setup")
    
    # Check if we're in the right directory
    if not Path("prisma/schema.prisma").exists():
        print("❌ prisma/schema.prisma not found. Make sure you're in the culturo-backend directory.")
        sys.exit(1)
    
    print("✅ Found prisma/schema.prisma")
    
    # Test Prisma commands
    tests = [
        ("python -m prisma --version", "Prisma CLI version"),
        ("python -m prisma generate", "Prisma client generation"),
        ("python -m prisma py fetch", "Prisma query engine fetch"),
        ("python -m prisma db push", "Database schema push")
    ]
    
    passed = 0
    total = len(tests)
    
    for command, description in tests:
        if run_command(command, description):
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Prisma setup tests passed!")
        sys.exit(0)
    else:
        print("💥 Some Prisma setup tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 