@echo off
echo ==========================================
echo UNS-ClaudeJP 2.0 - Quick Start
echo ==========================================
echo.

REM Check if Docker is installed
echo Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed!
    echo Please run install-windows.bat first.
    pause
    exit /b 1
)
echo [OK] Docker is installed
echo.

REM Check if Docker is running
echo Checking Docker status...
docker ps >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo Please start Docker Desktop.
    pause
    exit /b 1
)
echo [OK] Docker is running
echo.

REM Check if .env exists
if not exist ".env" (
    echo [ERROR] .env file not found!
    echo Please run install-windows.bat first.
    pause
    exit /b 1
)
echo [OK] Configuration found
echo.

REM Check if containers exist
echo Checking containers...
docker ps -a --filter "name=uns-claudejp" --format "{{.Names}}" | findstr "uns-claudejp" >nul
if errorlevel 1 (
    echo [INFO] Containers not found. Building first time...
    docker-compose up -d --build
    if errorlevel 1 (
        echo [ERROR] Build failed
        pause
        exit /b 1
    )
    echo [OK] Build complete
) else (
    echo Starting services...
    docker-compose up -d
    if errorlevel 1 (
        echo [ERROR] Failed to start services
        pause
        exit /b 1
    )
    echo [OK] Services started
)
echo.

REM Wait for services to be ready
echo Waiting for services to be ready...
timeout /t 15 /nobreak >nul
echo.

REM Check if services are responding
echo Checking service health...
curl -s http://localhost:8000/ >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Backend not responding yet. Waiting more...
    timeout /t 10 /nobreak >nul
)
echo [OK] Services appear to be running
echo.

echo ==========================================
echo UNS-ClaudeJP 2.0 is Ready!
echo ==========================================
echo.
echo Access the application:
echo   - Frontend: http://localhost:3000
echo   - Backend API: http://localhost:8000
echo   - API Docs: http://localhost:8000/api/docs
echo.
echo Default credentials:
echo   - Username: admin
echo   - Password: admin123
echo.

echo Opening application in browser...
start http://localhost:3000
start http://localhost:8000/api/docs
echo.

echo To stop the application later, run: stop-app.bat
echo.
pause