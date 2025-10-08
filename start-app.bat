@echo off
setlocal

echo ==========================================
echo UNS-ClaudeJP 2.0 - Quick Start
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
    echo Please run install-windows.bat first.
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

echo Checking configuration...
if not exist ".env" (
    echo [ERROR] .env file not found!
    echo Please run install-windows.bat first.
    pause
    exit /b 1
)
echo [OK] Configuration found
echo.

echo Checking containers...
docker ps -a --filter "name=uns-claudejp" --format "{{.Names}}" | findstr /I "uns-claudejp" >nul
if errorlevel 1 (
    echo [INFO] Containers not found. Building with latest images...
    call %DOCKER_COMPOSE_CMD% pull
    if errorlevel 1 (
        echo [WARNING] Could not pull updated images. Continuing with local cache.
    )
    call %DOCKER_COMPOSE_CMD% up -d --build
    if errorlevel 1 (
        echo [ERROR] Build failed
        pause
        exit /b 1
    )
    echo [OK] Build complete
) else (
    set "REBUILD_CHOICE=N"
    echo Containers detected.
    echo Do you want to rebuild the containers to apply recent updates? (Y/N)
    set /p REBUILD_CHOICE=
    if /I "%REBUILD_CHOICE%"=="Y" (
        echo [INFO] Updating container images...
        call %DOCKER_COMPOSE_CMD% pull
        if errorlevel 1 (
            echo [WARNING] Could not pull updated images. Continuing with local cache.
        )
        call %DOCKER_COMPOSE_CMD% up -d --build
        if errorlevel 1 (
            echo [ERROR] Failed to rebuild services
            pause
            exit /b 1
        )
        echo [OK] Services rebuilt with latest changes
    ) else (
        echo Starting services without rebuild...
        call %DOCKER_COMPOSE_CMD% up -d
        if errorlevel 1 (
            echo [ERROR] Failed to start services
            pause
            exit /b 1
        )
        echo [OK] Services started
    )
)
echo.

echo Waiting for services to be ready...
timeout /t 15 /nobreak >nul
echo.

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
endlocal
pause
