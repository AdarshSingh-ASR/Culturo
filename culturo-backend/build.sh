#!/bin/bash

# Build script for Culturo Backend
# This script handles the build phase with proper Prisma setup

set -e  # Exit on any error
set -x  # Print commands as they are executed

echo "🚀 Starting Culturo Backend build..."
echo "📁 Current directory: $(pwd)"
echo "🐍 Python version: $(python --version)"
echo "📦 pip version: $(pip --version)"

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Verify Prisma is installed
echo "🔍 Verifying Prisma installation..."
python -c "import prisma; print('✅ Prisma package found')"

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
python -m prisma db push

echo "✅ Build completed successfully!" 