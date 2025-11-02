Write-Host "🚀 Deploying GenomeGuard Minimal Version..." -ForegroundColor Green

# Stop existing containers
Write-Host "Stopping existing containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.minimal.yml down

# Build and start minimal version
Write-Host "Building and starting minimal containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.minimal.yml up --build -d

# Wait for services to start
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check service health
Write-Host "Checking service health..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
    Write-Host "✅ API is healthy" -ForegroundColor Green
} catch {
    Write-Host "❌ API health check failed" -ForegroundColor Red
}

Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔗 API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan