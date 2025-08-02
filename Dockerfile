# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js and npm
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Copy package files first for better caching
COPY culturo-frontend/package*.json ./culturo-frontend/
COPY culturo-backend/requirements.txt ./culturo-backend/

# Install Python dependencies
RUN pip install --no-cache-dir -r culturo-backend/requirements.txt

# Install Node.js dependencies
RUN cd culturo-frontend && npm install

# Copy the rest of the application
COPY . .

# Build the frontend
RUN cd culturo-frontend && npm run build

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app/culturo-backend
ENV HOST=0.0.0.0
ENV PORT=8000
ENV ENVIRONMENT=production

# Start the application
CMD ["python", "main.py"] 