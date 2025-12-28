@echo off
echo ========================================
echo Pet Health RAG Chatbot Frontend
echo ========================================
echo.

cd /d "%~dp0\frontend"

echo Starting local web server...
echo.
echo Frontend will be available at: http://localhost:8080
echo.
echo Make sure the backend is running at http://localhost:8000
echo.

python -m http.server 8080

pause
