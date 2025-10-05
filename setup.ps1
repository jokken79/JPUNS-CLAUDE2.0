# UNS-ClaudeJP - Download and Setup Script
# Run this in PowerShell as Administrator

$projectPath = "D:\UNS-JPClaude"
$downloadUrl = "https://github.com/your-repo/uns-claudejp/archive/refs/heads/main.zip"
$tempZip = "$env:TEMP\uns-claudejp.zip"

Write-Host "=========================================="
Write-Host "UNS-ClaudeJP - Automated Setup"
Write-Host "=========================================="
Write-Host ""

# Check if Docker is installed
Write-Host "Checking Docker..."
try {
    docker --version | Out-Null
    Write-Host "[OK] Docker is installed" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker is not installed!" -ForegroundColor Red
    Write-Host "Please install Docker Desktop from:"
    Write-Host "https://www.docker.com/products/docker-desktop"
    exit 1
}

# Check if Docker is running
Write-Host "Checking Docker status..."
try {
    docker ps | Out-Null
    Write-Host "[OK] Docker is running" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop first."
    exit 1
}

Write-Host ""
Write-Host "Project will be created at: $projectPath"
Write-Host ""

# Create .env from example
if (Test-Path "$projectPath\.env.example") {
    if (-not (Test-Path "$projectPath\.env")) {
        Write-Host "Creating .env file..."
        Copy-Item "$projectPath\.env.example" "$projectPath\.env"
        Write-Host "[OK] .env file created"
        Write-Host ""
        Write-Host "[IMPORTANT] Please edit the .env file and change:"
        Write-Host "  - DB_PASSWORD"
        Write-Host "  - SECRET_KEY"
        Write-Host ""
        $editEnv = Read-Host "Do you want to edit .env now? (Y/N)"
        if ($editEnv -eq "Y" -or $editEnv -eq "y") {
            notepad "$projectPath\.env"
        }
    }
}

# Build and start services
Write-Host ""
Write-Host "Building Docker images (this may take 5-10 minutes)..."
Set-Location $projectPath
docker-compose build

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Build failed" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Build complete" -ForegroundColor Green
Write-Host ""

Write-Host "Starting services..."
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to start services" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Services started" -ForegroundColor Green
Write-Host ""
Write-Host "Waiting for services to be ready..."
Start-Sleep -Seconds 10

# Get local IP
$localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "192.168.*"}).IPAddress

Write-Host ""
Write-Host "=========================================="
Write-Host "Installation Complete!"
Write-Host "=========================================="
Write-Host ""
Write-Host "Access the application:"
Write-Host "  - Frontend: http://localhost:3000"
Write-Host "  - Backend API: http://localhost:8000"
Write-Host "  - API Docs: http://localhost:8000/api/docs"
Write-Host ""
if ($localIP) {
    Write-Host "Network access:"
    Write-Host "  - Frontend: http://${localIP}:3000"
    Write-Host "  - Backend: http://${localIP}:8000"
    Write-Host ""
}
Write-Host "Default credentials:"
Write-Host "  - Username: admin"
Write-Host "  - Password: admin123"
Write-Host "  [IMPORTANT] Change password after first login!"
Write-Host ""
Write-Host "Useful commands:"
Write-Host "  - View logs: docker-compose logs -f"
Write-Host "  - Stop: docker-compose stop"
Write-Host "  - Start: docker-compose start"
Write-Host "  - Restart: docker-compose restart"
Write-Host ""

$openBrowser = Read-Host "Open application in browser? (Y/N)"
if ($openBrowser -eq "Y" -or $openBrowser -eq "y") {
    Start-Process "http://localhost:3000"
    Start-Process "http://localhost:8000/api/docs"
}

Write-Host ""
Write-Host "Setup complete! Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
