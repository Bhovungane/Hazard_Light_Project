@echo off
REM Start script for Vehicle Light Inspection System
REM Double-click this file to launch the inspection application

echo Starting Vehicle Light Inspection System...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please run install.bat first
    pause
    exit /b 1
)

REM Check if dependencies are installed
python -c "import cv2" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Dependencies not installed
    echo Please run install.bat first
    pause
    exit /b 1
)

REM Launch the GUI application
python inspection_app.py

if errorlevel 1 (
    echo.
    echo An error occurred. Check the logs folder for details.
    pause
)

