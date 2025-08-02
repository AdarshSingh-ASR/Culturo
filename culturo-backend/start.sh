#!/bin/bash

# Exit on any error
set -e

echo "Starting Culturo Backend..."

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements-render.txt
fi

# Generate Prisma client
echo "Generating Prisma client..."
prisma generate

# Push database schema
echo "Pushing database schema..."
prisma db push

# Start the application
echo "Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT 