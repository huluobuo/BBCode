@echo off
chcp 936 >nul
title BBCode Cloud KB Server

:: Switch to script directory
cd /d "%~dp0"

echo.
echo  ============================================
echo   BBCode Cloud KB Server (Simple)
echo  ============================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [Error] Python not found. Please install Python and add it to PATH.
    pause
    exit /b 1
)

echo [Info] Python version:
python --version
echo.

:: Check dependencies
echo [Info] Checking dependencies...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [Info] Installing dependencies...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [Error] Failed to install dependencies
        pause
        exit /b 1
    )
)

echo [Info] Dependencies installed
echo.
echo [Info] Starting server...
echo [Info] LAN access supported. Other devices can connect via LAN IP.
echo.

:: Start server
python server.py

pause
