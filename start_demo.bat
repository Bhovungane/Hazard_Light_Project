@echo off
REM Quick start script for supervisor demonstration
REM Double-click this to start the live camera demo

echo ========================================
echo Vehicle Light Inspection - LIVE DEMO
echo ========================================
echo.
echo Starting live camera demonstration...
echo.
echo Instructions:
echo   1. Point your laptop camera at vehicle lights
echo   2. Ensure lights are clearly visible
echo   3. Wait 2-3 seconds for detection
echo   4. Results appear in real-time
echo.
echo Press 'q' in video window to quit
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed
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

REM Launch demo
python demo_live_camera.py

if errorlevel 1 (
    echo.
    echo An error occurred. Check the error message above.
    pause
)

