@echo off
chcp 65001 >nul
echo =========================================
echo   Battery Monitoring - Frontend (React)
echo =========================================
echo.
cd /d "%~dp0frontend"

echo Checking dependencies...
if not exist "node_modules" (
    echo Installing npm dependencies...
    npm install
)

echo.
echo Starting frontend server...
echo Local:  http://localhost:3000
echo.
npm run dev -- --host
pause
