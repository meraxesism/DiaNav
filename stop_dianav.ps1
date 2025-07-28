# DiaNav Stop Script
Write-Host "Stopping DiaNav Servers..." -ForegroundColor Red

# Stop backend on port 8000
Write-Host "Stopping Backend..." -ForegroundColor Yellow
netstat -ano | findstr :8000 | ForEach-Object {
    $parts = $_ -split '\s+'
    if ($parts.Length -ge 5) {
        $processId = $parts[4]
        taskkill /PID $processId /F 2>$null
        Write-Host "Stopped process $processId on port 8000" -ForegroundColor Green
    }
}

# Stop frontend on port 3000
Write-Host "Stopping Frontend..." -ForegroundColor Yellow
netstat -ano | findstr :3000 | ForEach-Object {
    $parts = $_ -split '\s+'
    if ($parts.Length -ge 5) {
        $processId = $parts[4]
        taskkill /PID $processId /F 2>$null
        Write-Host "Stopped process $processId on port 3000" -ForegroundColor Green
    }
}

Write-Host "DiaNav servers stopped!" -ForegroundColor Green 