#!/bin/bash

# Simple test script to verify build process
echo "🧪 Testing build process..."

# Check if we're in the right directory
echo "📁 Current directory: $(pwd)"
echo "📁 Directory contents:"
ls -la

# Check if build script exists
if [ -f "build.sh" ]; then
    echo "✅ build.sh found"
    echo "📄 build.sh contents:"
    head -10 build.sh
else
    echo "❌ build.sh not found"
    exit 1
fi

# Test Python and pip
echo "🐍 Python version: $(python --version)"
echo "📦 pip version: $(pip --version)"

# Test if prisma is available
echo "🔍 Testing prisma availability..."
if python -c "import prisma; print('✅ Prisma package available')" 2>/dev/null; then
    echo "✅ Prisma package is available"
else
    echo "❌ Prisma package not available"
fi

echo "✅ Build test completed" 