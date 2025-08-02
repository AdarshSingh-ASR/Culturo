#!/bin/bash

# Deployment script for Culturo Backend
# This script handles Prisma setup and application startup

set -e

echo "🚀 Starting Culturo Backend deployment..."

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Generate Prisma client
echo "🔧 Generating Prisma client..."
prisma generate

# Fetch Prisma query engine for the current platform
echo "📥 Fetching Prisma query engine..."
prisma py fetch

# Push database schema
echo "🗄️ Pushing database schema..."
prisma db push

# Start the application
echo "🌟 Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT 