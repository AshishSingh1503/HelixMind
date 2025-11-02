#!/bin/bash

echo "🚀 Deploying GenomeGuard Minimal Version..."

# Stop existing containers
echo "Stopping existing containers..."
docker-compose -f docker-compose.minimal.yml down

# Build and start minimal version
echo "Building and starting minimal containers..."
docker-compose -f docker-compose.minimal.yml up --build -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 10

# Check service health
echo "Checking service health..."
curl -f http://localhost:8000/health || echo "API health check failed"

echo "✅ Deployment complete!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔗 API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"