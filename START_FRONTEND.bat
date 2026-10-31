@echo off
title EcoQuest Frontend Server
color 0B

echo ==========================================
echo   EcoQuest Frontend Startup Script
echo ==========================================
echo.

if exist "Gamified-Environmental-Education-main\frontend" (
    cd Gamified-Environmental-Education-main\frontend
)

echo [*] Starting Vite React Frontend...
echo [*] App will be available at: http://localhost:5173
echo ==========================================
echo.

npm run dev

pause
