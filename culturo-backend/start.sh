#!/bin/bash

# Start script for Culturo Backend
# This script handles Prisma setup and application startup

set -e

# Generate Prisma client
echo "Generating Prisma client..."
python -m prisma generate

# Fetch Prisma query engine
echo "Fetching Prisma query engine..."
python -m prisma py fetch

# Push database schema (or use migrations)
echo "Pushing database schema..."
python -m prisma db push

# Start the application
echo "Starting application..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
