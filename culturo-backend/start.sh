#!/bin/bash

# Exit on any error
set -e

echo "Starting Culturo Backend..."

# Generate Prisma client
echo "Generating Prisma client..."
prisma generate

# Fetch Prisma query engine
echo "Fetching Prisma query engine..."
prisma py fetch

# Push database schema
echo "Pushing database schema..."
prisma db push

# Start the application
echo "Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT 