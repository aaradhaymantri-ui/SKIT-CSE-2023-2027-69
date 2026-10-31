@echo off
title EcoQuest Backend Server
color 0A

echo ==========================================
echo   EcoQuest Backend Startup Script
echo ==========================================
echo.

:: 1. Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment 'venv' not found!
    echo Please create it first by running: python -m venv venv
    pause
    exit /b 1
)

:: 2. Activate virtual environment
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat

:: 3. Ensure core dependencies are installed
echo [*] Verifying dependencies...
pip show psycopg2-binary >nul 2>&1
if errorlevel 1 (
    echo [*] Installing missing dependencies...
    pip install flask==2.3.3 werkzeug==2.3.7 flask-cors flask-sqlalchemy requests python-dotenv psycopg2-binary supabase
)

:: 4. Navigate to backend directory if at project root
if exist "Gamified-Environmental-Education-main\backend\app.py" (
    cd Gamified-Environmental-Education-main\backend
)

:: 5. Run the Flask app
echo.
echo [*] Starting EcoQuest Backend Server...
echo [*] Server will be available at: http://localhost:5000
echo [*] Press Ctrl+C to stop the server.
echo ==========================================
echo.

python app.py

pause
