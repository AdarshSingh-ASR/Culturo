#!/usr/bin/env python3
"""
Test script to verify Prisma setup
"""
import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and return success status"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} successful")
            return True
        else:
            print(f"❌ {description} failed:")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False

def main():
    print("🧪 Testing Prisma Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("prisma/schema.prisma"):
        print("❌ prisma/schema.prisma not found. Make sure you're in the culturo-backend directory.")
        sys.exit(1)
    
    # Test Prisma commands
    commands = [
        ("prisma --version", "Prisma CLI version"),
        ("prisma generate", "Prisma client generation"),
        ("prisma py fetch", "Prisma query engine fetch"),
        ("prisma db push", "Database schema push")
    ]
    
    success_count = 0
    for command, description in commands:
        if run_command(command, description):
            success_count += 1
        print()
    
    print(f"📊 Results: {success_count}/{len(commands)} commands successful")
    
    if success_count == len(commands):
        print("🎉 All Prisma setup tests passed!")
        return True
    else:
        print("💥 Some Prisma setup tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 