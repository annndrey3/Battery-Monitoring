@echo off
chcp 65001 >nul
echo =========================================
echo   Battery Monitoring - Full Stack
echo =========================================
echo.

if "%1"=="--ngrok" (
    echo Starting with ngrok tunnel...
    set NGROK_MODE=1
) else (
    echo Starting locally...
    set NGROK_MODE=0
)

echo Starting Backend...
start "Backend - FastAPI" cmd /k "%~dp0start-backend.bat"

timeout /t 5 /nobreak >nul

echo Starting Frontend...
start "Frontend - React" cmd /k "%~dp0start-frontend.bat"

if "%NGROK_MODE%"=="1" (
    timeout /t 8 /nobreak >nul
    echo Starting ngrok tunnel...
    start "Ngrok Tunnel" cmd /k "%~dp0start-ngrok.bat"
)

echo.
echo =========================================
echo All services started!
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
if "%NGROK_MODE%"=="1" echo Ngrok:    Check http://localhost:4040 for public URL
echo =========================================
echo.
echo Press any key to exit this window...
pause >nul
