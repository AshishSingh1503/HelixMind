Write-Host "🔍 Verifying GenomeGuard Minimal Deployment..." -ForegroundColor Green

# Check if Docker is running
try {
    docker --version | Out-Null
    Write-Host "✅ Docker is available" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not available or not running" -ForegroundColor Red
    exit 1
}

# Check if containers are running
$containers = docker ps --format "table {{.Names}}\t{{.Status}}" | Select-String "genomeguard"
if ($containers) {
    Write-Host "✅ GenomeGuard containers are running:" -ForegroundColor Green
    $containers | ForEach-Object { Write-Host "   $_" -ForegroundColor Cyan }
} else {
    Write-Host "❌ No GenomeGuard containers found running" -ForegroundColor Red
    Write-Host "Run deploy-minimal.ps1 first" -ForegroundColor Yellow
    exit 1
}

# Test API health
Write-Host "🔍 Testing API health..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ API is healthy and responding" -ForegroundColor Green
        $healthData = $response.Content | ConvertFrom-Json
        Write-Host "   Status: $($healthData.status)" -ForegroundColor Cyan
    } else {
        Write-Host "❌ API health check failed with status: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ API is not responding: $($_.Exception.Message)" -ForegroundColor Red
}

# Test frontend
Write-Host "🔍 Testing frontend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Frontend is accessible" -ForegroundColor Green
    } else {
        Write-Host "❌ Frontend check failed with status: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Frontend is not responding: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎯 Deployment Summary:" -ForegroundColor Green
Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔗 API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan