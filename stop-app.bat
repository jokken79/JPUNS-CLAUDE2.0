@echo off
echo ==========================================
echo UNS-ClaudeJP 2.0 - Stop Application
echo ==========================================
echo.

echo Stopping services...
docker-compose stop
if errorlevel 1 (
    echo [ERROR] Failed to stop services
    pause
    exit /b 1
)
echo [OK] Services stopped
echo.

echo Application stopped successfully.
echo Run start-app.bat to start it again.
echo.
pause