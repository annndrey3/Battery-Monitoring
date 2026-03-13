@echo off
chcp 65001 >nul
echo =========================================
echo   Battery Monitoring with Ngrok
echo =========================================
echo.

:: Запускаємо все з параметром --ngrok через start-all.bat
call "%~dp0start-all.bat" --ngrok
