@echo off
echo ========================================
echo Pet Health RAG Chatbot Backend
echo ========================================
echo.

cd /d "%~dp0"

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Starting FastAPI server...
echo API will be available at: http://localhost:8000
echo API documentation at: http://localhost:8000/docs
echo.

python -m backend.main

pause
