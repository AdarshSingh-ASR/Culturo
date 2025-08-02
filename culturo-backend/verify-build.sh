#!/bin/bash

# Verification script for build process
# This script tests if the build script works correctly

set -e

echo "🧪 Testing build script..."

# Test if build script exists and is executable
if [ -f "build.sh" ]; then
    echo "✅ build.sh exists"
    if [ -x "build.sh" ]; then
        echo "✅ build.sh is executable"
    else
        echo "❌ build.sh is not executable"
        chmod +x build.sh
        echo "🔧 Made build.sh executable"
    fi
else
    echo "❌ build.sh not found"
    exit 1
fi

# Test if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt exists"
else
    echo "❌ requirements.txt not found"
    exit 1
fi

# Test if prisma schema exists
if [ -f "prisma/schema.prisma" ]; then
    echo "✅ prisma/schema.prisma exists"
else
    echo "❌ prisma/schema.prisma not found"
    exit 1
fi

echo "✅ All build prerequisites are met"
echo "🚀 Ready to run build script" 