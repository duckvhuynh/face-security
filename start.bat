@echo off
echo =======================================
echo    Face Security System Startup
echo =======================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

echo Python is installed.

:: Change to script directory
cd /d "%~dp0"

:: Check if required packages are installed
echo Checking dependencies...
python -c "import cv2, mediapipe, tkinter, cryptography, keyboard, sklearn" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Some required packages are missing. Installing...
    echo.
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install required packages
        echo Please run: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

echo All dependencies are installed.
echo.

:: Launch the application
echo Starting Face Security System...
echo.
python launcher.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start the application
    echo Check the error messages above for details
    pause
)
