#!/bin/bash

# Culturo Backend Startup Script

echo "🌍 Starting Culturo Backend..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp env.example .env
    echo "📝 Please edit .env file with your API keys and database credentials"
    echo "🔑 Required API keys: QLOO_API_KEY, GEMINI_API_KEY, SECRET_KEY"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check if PostgreSQL is running
echo "🗄️  Checking database connection..."
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "⚠️  PostgreSQL is not running. Please start PostgreSQL first."
    echo "💡 You can use Docker: docker run --name postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:15"
    exit 1
fi

# Check if Redis is running
echo "🔴 Checking Redis connection..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "⚠️  Redis is not running. Please start Redis first."
    echo "💡 You can use Docker: docker run --name redis -p 6379:6379 -d redis:7"
    exit 1
fi

# Run database migrations (if using Alembic)
if [ -f "alembic.ini" ]; then
    echo "🔄 Running database migrations..."
    alembic upgrade head
fi

# Start the application
echo "🚀 Starting Culturo Backend server..."
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🏥 Health Check: http://localhost:8000/health"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 