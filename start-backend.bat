@echo off
chcp 65001 >nul
echo =========================================
echo   Battery Monitoring - Backend (FastAPI)
echo =========================================
echo.
cd /d "%~dp0backend"

echo Checking dependencies...
python -c "import fastapi, uvicorn, sqlalchemy, google.generativeai" 2>nul || (
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo Checking .env configuration...
if not exist ".env" (
    if exist ".env.example" (
        echo Creating .env from .env.example...
        copy .env.example .env
    )
)

echo.
echo Applying database migrations...
alembic upgrade head

echo.
echo Starting backend server...
echo URL: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
