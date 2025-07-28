# DiaNav Startup Script
# This script starts both the backend and frontend servers

Write-Host "Starting DiaNav - AI-Powered Automotive Diagnostic Assistant" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green

# Function to check if a port is in use
function Test-Port {
    param($Port)
    try {
        $connection = Test-NetConnection -ComputerName localhost -Port $Port -WarningAction SilentlyContinue
        return $connection.TcpTestSucceeded
    }
    catch {
        return $false
    }
}

# Function to kill process on a specific port
function Stop-ProcessOnPort {
    param($Port)
    try {
        $process = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($process) {
            $processId = $process.OwningProcess
            Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
            Write-Host "Killed existing process on port $Port" -ForegroundColor Yellow
            Start-Sleep -Seconds 2
        }
    }
    catch {
        # Ignore errors
    }
}

# Check and kill existing processes on ports 8000 and 3000
Write-Host "Checking for existing processes..." -ForegroundColor Cyan

if (Test-Port -Port 8000) {
    Write-Host "Port 8000 is in use. Stopping existing backend..." -ForegroundColor Yellow
    Stop-ProcessOnPort -Port 8000
}

if (Test-Port -Port 3000) {
    Write-Host "Port 3000 is in use. Stopping existing frontend..." -ForegroundColor Yellow
    Stop-ProcessOnPort -Port 3000
}

# Start Backend
Write-Host "Starting Backend Server (FastAPI)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; python dianav_backend.py" -WindowStyle Normal

# Wait for backend to start
Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
$backendReady = $false
$attempts = 0
while (-not $backendReady -and $attempts -lt 30) {
    Start-Sleep -Seconds 2
    $attempts++
    if (Test-Port -Port 8000) {
        $backendReady = $true
        Write-Host "Backend server is ready on http://localhost:8000" -ForegroundColor Green
    }
}

if (-not $backendReady) {
    Write-Host "Backend failed to start within 60 seconds" -ForegroundColor Red
    exit 1
}

# Start Frontend
Write-Host "Starting Frontend Server (React)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\dianav-frontend'; npm start" -WindowStyle Normal

# Wait for frontend to start
Write-Host "Waiting for frontend to start..." -ForegroundColor Yellow
$frontendReady = $false
$attempts = 0
while (-not $frontendReady -and $attempts -lt 45) {
    Start-Sleep -Seconds 2
    $attempts++
    if (Test-Port -Port 3000) {
        $frontendReady = $true
        Write-Host "Frontend server is ready on http://localhost:3000" -ForegroundColor Green
    }
}

if (-not $frontendReady) {
    Write-Host "Frontend failed to start within 90 seconds" -ForegroundColor Red
    Write-Host "You can manually start the frontend by running: cd dianav-frontend && npm start" -ForegroundColor Yellow
}

# Final status
Write-Host ""
Write-Host "DiaNav is starting up!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host "Backend API:  http://localhost:8000" -ForegroundColor White
Write-Host "Frontend App: http://localhost:3000" -ForegroundColor White
Write-Host "API Health:   http://localhost:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "Tips:" -ForegroundColor Cyan
Write-Host "   The frontend will automatically open in your browser" -ForegroundColor White
Write-Host "   Try asking: 'What is DTC B1087?' to test the system" -ForegroundColor White
Write-Host "   Press Ctrl+C in the server windows to stop them" -ForegroundColor White
Write-Host ""
Write-Host "Security: All diagnostic images are processed in memory only" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Green

# Keep the script running to show status
Write-Host "Monitoring servers... (Press Ctrl+C to exit this script)" -ForegroundColor Cyan
try {
    while ($true) {
        $backendStatus = if (Test-Port -Port 8000) { "OK" } else { "DOWN" }
        $frontendStatus = if (Test-Port -Port 3000) { "OK" } else { "DOWN" }
        
        Write-Host "Backend: $backendStatus | Frontend: $frontendStatus" -ForegroundColor White
        Start-Sleep -Seconds 5
    }
}
catch {
    Write-Host ""
    Write-Host "DiaNav startup script stopped" -ForegroundColor Yellow
} 