@echo off
title EcoQuest Platform Launcher
color 0A

echo ================================================================
echo   Launching EcoQuest (Backend Flask + Frontend Vite React)
echo ================================================================
echo.

start "EcoQuest Backend" cmd /k "START_ECOQUEST.bat"
start "EcoQuest Frontend" cmd /k "START_FRONTEND.bat"

echo [*] Backend launching at:  http://localhost:5000
echo [*] Frontend launching at: http://localhost:5173
echo.
