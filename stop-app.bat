@echo off
setlocal

echo ==========================================
echo UNS-ClaudeJP 2.0 - Stop Application
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
        pause
        exit /b 1
    )
)

echo Stopping services...
call %DOCKER_COMPOSE_CMD% stop
if errorlevel 1 (
    echo [ERROR] Failed to stop services
    pause
    exit /b 1
)
echo [OK] Services stopped
echo.

echo To remove containers completely, run: %DOCKER_COMPOSE_CMD% down
echo.
endlocal
pause
