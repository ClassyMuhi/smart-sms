@echo off
REM Startup script for Smart SMS Authentication Module (Windows)
REM Run this script to quickly set up and start the development server

REM Colors not available in Windows batch, using titles instead
title Smart SMS - Authentication Module Setup

echo.
echo ========================================
echo Smart SMS - Authentication Module
echo Setup ^& Run Script
echo ========================================

REM Check Python
echo.
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found!
    exit /b 1
)

REM Create virtual environment if not exists
if not exist "venv" (
    echo.
    echo [2/5] Creating virtual environment...
    python -m venv venv
) else (
    echo.
    echo [2/5] Virtual environment already exists
)

REM Activate virtual environment
echo.
echo [3/5] Installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt

REM Run migrations
echo.
echo [4/5] Running database migrations...
python manage.py migrate

REM Create superuser if needed
echo.
echo [5/5] Setting up admin user...
echo Admin credentials (optional):
echo - Phone: +1234567890
echo - Email: admin@example.com
echo.

REM Start server
echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo Starting development server...
echo.
python manage.py runserver

pause
