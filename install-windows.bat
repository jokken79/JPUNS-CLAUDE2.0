@echo off
echo ==========================================
echo UNS-ClaudeJP 1.0 - Windows Installation
echo ==========================================
echo.

REM Check if Docker is installed
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

REM Create necessary directories
echo Creating directories...
if not exist "uploads" mkdir uploads
if not exist "logs" mkdir logs
if not exist "config\factories" mkdir config\factories
echo [OK] Directories created
echo.

REM Check .env file
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo.
    echo [IMPORTANT] Please edit .env file:
    echo   1. Change DB_PASSWORD
    echo   2. Change SECRET_KEY
    echo   3. Configure email (optional)
    echo.
    echo Do you want to edit .env now? (Y/N)
    set /p EDIT_ENV=
    if /i "%EDIT_ENV%"=="Y" (
        notepad .env
    )
)
echo.

REM Build Docker images
echo Building Docker images...
docker-compose build
if errorlevel 1 (
    echo [ERROR] Build failed
    pause
    exit /b 1
)
echo [OK] Build complete
echo.

REM Start services
echo Starting services...
docker-compose up -d
if errorlevel 1 (
    echo [ERROR] Failed to start services
    pause
    exit /b 1
)
echo [OK] Services started
echo.

REM Wait for services to be ready
echo Waiting for services...
timeout /t 10 /nobreak >nul
echo.

REM Get local IP
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set LOCAL_IP=%%a
    goto :found_ip
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
echo   - View logs: docker-compose logs -f
echo   - Stop: docker-compose stop
echo   - Start: docker-compose start
echo   - Restart: docker-compose restart
echo   - Remove: docker-compose down
echo.
echo Open application in browser? (Y/N)
set /p OPEN_BROWSER=
if /i "%OPEN_BROWSER%"=="Y" (
    start http://localhost:3000
    start http://localhost:8000/api/docs
)
echo.
pause
