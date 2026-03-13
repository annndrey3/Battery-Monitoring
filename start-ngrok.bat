@echo off
chcp 65001 >nul
echo =========================================
echo   Battery Monitoring - Ngrok Tunnel
echo =========================================
echo.

set NGROK_PATH=%TEMP%\ngrok\ngrok.exe

echo Checking ngrok...
if not exist "%NGROK_PATH%" (
    echo Downloading ngrok...
    powershell -Command "Invoke-WebRequest -Uri 'https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip' -OutFile '%TEMP%\ngrok.zip' -UseBasicParsing; Expand-Archive -Path '%TEMP%\ngrok.zip' -DestinationPath '%TEMP%\ngrok' -Force"
    echo Download complete.
)

echo.
echo Starting ngrok tunnel to localhost:3000...
echo Dashboard: http://localhost:4040
echo.
echo Wait for "Session Status: online" message
echo Then open the HTTPS URL from the dashboard
echo.

"%NGROK_PATH%" http http://localhost:3000
pause
