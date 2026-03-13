@echo off
chcp 65001 >nul
echo =========================================
echo   Battery Monitoring - Setup
echo =========================================
echo.

echo [1/5] Checking Python...
python --version 2>nul || (
    echo ERROR: Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

echo [2/5] Checking Node.js...
node --version 2>nul || (
    echo ERROR: Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)

echo.
echo [3/5] Installing Backend Dependencies...
cd /d "%~dp0backend"
python -m venv venv 2>nul
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    pip install -r requirements.txt
)

echo.
echo [4/5] Installing Frontend Dependencies...
cd /d "%~dp0frontend"
npm install

echo.
echo [5/5] Checking ngrok...
if not exist "%TEMP%\ngrok\ngrok.exe" (
    echo Downloading ngrok...
    powershell -Command "Invoke-WebRequest -Uri 'https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip' -OutFile '%TEMP%\ngrok.zip' -UseBasicParsing; Expand-Archive -Path '%TEMP%\ngrok.zip' -DestinationPath '%TEMP%\ngrok' -Force"
    echo ngrok downloaded successfully.
)

echo.
echo =========================================
echo Setup Complete!
echo =========================================
echo.
echo Run 'start-all.bat' to start the application.
echo Run 'start-with-ngrok.bat' to start with public URL.
pause
