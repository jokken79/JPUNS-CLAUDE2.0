@echo off
setlocal

echo ==========================================
echo UNS-ClaudeJP 2.0 - Windows Installation
echo ==========================================
echo.

echo Detecting Docker Compose...
set "DOCKER_COMPOSE_CMD="
docker compose version >nul 2>&1
if %errorlevel% EQU 0 (
    set "DOCKER_COMPOSE_CMD=docker compose"
) else (
    docker-compose version >nul 2>&1
    if %errorlevel% EQU 0 (
        set "DOCKER_COMPOSE_CMD=docker-compose"
    ) else (
        echo [ERROR] Docker Compose is not installed!
        echo Please install Docker Desktop or enable Docker Compose V2.
        pause
        exit /b 1
    )
)

echo Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed!
    echo Please install Docker Desktop from:
    echo https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
echo [OK] Docker is installed
echo.

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

echo Creating directories...
if not exist "uploads" mkdir uploads
if not exist "logs" mkdir logs
if not exist "config\factories" mkdir config\factories
echo [OK] Directories created
echo.

echo Checking .env file...
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env >nul
    echo.
    echo [IMPORTANT] Please edit .env file:
    echo   1. Change DB_PASSWORD
    echo   2. Change SECRET_KEY
    echo   3. Configure email (optional)
    echo.
    echo Do you want to edit .env now? (Y/N)
    set /p EDIT_ENV=
    if /I "%EDIT_ENV%"=="Y" (
        notepad .env
    )
)
echo.

echo Pulling latest container images (this may take a moment)...
call %DOCKER_COMPOSE_CMD% pull
if errorlevel 1 (
    echo [WARNING] Could not pull updated images. Continuing with local cache.
)
echo.

echo Building Docker images...
call %DOCKER_COMPOSE_CMD% up -d --build
if errorlevel 1 (
    echo [ERROR] Build failed
    pause
    exit /b 1
)
echo [OK] Build complete
echo.

echo Waiting for services to initialize...
timeout /t 20 /nobreak >nul
echo.

echo Checking service health...
curl -s http://localhost:8000/ >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Backend not responding yet. This is normal on first startup.
    echo The database might still be initializing. Please wait a few minutes.
)
echo.

for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set LOCAL_IP=%%a
    goto found_ip
)
:found_ip
set LOCAL_IP=%LOCAL_IP:~1%

echo ==========================================
echo Installation Complete!
echo ==========================================
echo.
echo Access the application:
echo   - Frontend: http://localhost:3000
echo   - Backend API: http://localhost:8000
echo   - API Docs: http://localhost:8000/api/docs
echo.
echo Network access:
echo   - Frontend: http://%LOCAL_IP%:3000
echo   - Backend: http://%LOCAL_IP%:8000
echo.
echo Default credentials:
echo   - Username: admin
echo   - Password: admin123
echo   [IMPORTANT] Change password after first login!
echo.
echo Useful commands:
echo   - Quick start: start-app.bat
echo   - Quick stop: stop-app.bat
echo   - View logs: %DOCKER_COMPOSE_CMD% logs -f
echo   - Stop: %DOCKER_COMPOSE_CMD% stop
echo   - Start: %DOCKER_COMPOSE_CMD% start
echo   - Restart: %DOCKER_COMPOSE_CMD% restart
echo   - Remove: %DOCKER_COMPOSE_CMD% down
echo.
echo Open application in browser? (Y/N)
set /p OPEN_BROWSER=
if /I "%OPEN_BROWSER%"=="Y" (
    start http://localhost:3000
    start http://localhost:8000/api/docs
)
echo.
endlocal
pause
