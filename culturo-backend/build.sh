#!/bin/bash

# Build script for Culturo Backend
# This script handles the build phase with proper Prisma setup

set -e  # Exit on any error
set -x  # Print commands as they are executed

echo "🚀 Starting Culturo Backend build..."
echo "📁 Current directory: $(pwd)"
echo "🐍 Python version: $(python --version)"
echo "📦 pip version: $(pip --version)"
echo "🔍 Python executable: $(which python)"
echo "🔍 pip executable: $(which pip)"
echo "🔍 Python path: $PYTHONPATH"

# Install dependencies
echo "📦 Installing Python dependencies..."
if [ -f "requirements-render.txt" ]; then
    echo "📦 Using Render-optimized requirements..."
    pip install -r requirements-render.txt
else
    echo "📦 Using standard requirements..."
    pip install -r requirements.txt
fi

# Verify Prisma is installed
echo "🔍 Verifying Prisma installation..."
python -c "import prisma; print('✅ Prisma package found')"

# Check Prisma CLI availability
echo "🔍 Checking Prisma CLI availability..."
if python -m prisma --help > /dev/null 2>&1; then
    echo "✅ Prisma CLI is available"
else
    echo "❌ Prisma CLI is not available"
    exit 1
fi

# Run comprehensive Prisma test
echo "🧪 Running Prisma CLI test..."
if python test-prisma-cli.py; then
    echo "✅ Prisma CLI test passed"
else
    echo "❌ Prisma CLI test failed"
    exit 1
fi

# Generate Prisma client
echo "🔧 Generating Prisma client..."
python -m prisma generate

# Fetch Prisma query engine with retry logic
echo "📥 Fetching Prisma query engine..."
max_retries=3
retry_count=0

while [ $retry_count -lt $max_retries ]; do
    if python -m prisma py fetch; then
        echo "✅ Prisma query engine fetched successfully"
        break
    else
        retry_count=$((retry_count + 1))
        echo "❌ Failed to fetch Prisma query engine (attempt $retry_count/$max_retries)"
        if [ $retry_count -lt $max_retries ]; then
            echo "🔄 Retrying in 5 seconds..."
            sleep 5
        else
            echo "💥 Failed to fetch Prisma query engine after $max_retries attempts"
            exit 1
        fi
    fi
done

# Push database schema
echo "🗄️ Pushing database schema..."
max_retries=3
retry_count=0

while [ $retry_count -lt $max_retries ]; do
    if python -m prisma db push; then
        echo "✅ Database schema pushed successfully"
        break
    else
        retry_count=$((retry_count + 1))
        echo "❌ Failed to push database schema (attempt $retry_count/$max_retries)"
        if [ $retry_count -lt $max_retries ]; then
            echo "🔄 Retrying in 5 seconds..."
            sleep 5
        else
            echo "💥 Failed to push database schema after $max_retries attempts"
            exit 1
        fi
    fi
done

# Final verification
echo "🔍 Final verification..."
echo "📁 Current directory: $(pwd)"
echo "🐍 Python version: $(python --version)"
echo "📦 Installed packages:"
pip list | grep -E "(prisma|fastapi|uvicorn)"

echo "✅ Build completed successfully!" 