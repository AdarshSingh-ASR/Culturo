#!/bin/bash

# Deploy script for Culturo Backend
# This script handles Prisma setup and application startup

set -e

echo "🚀 Starting Culturo Backend deployment..."

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Generate Prisma client
echo "🔧 Generating Prisma client..."
python -m prisma generate

# Fetch Prisma query engine for the current platform
echo "📥 Fetching Prisma query engine..."
python -m prisma py fetch

# Push database schema
echo "🗄️ Pushing database schema..."
python -m prisma db push

echo "✅ Deployment completed successfully!" 