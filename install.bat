@echo off
REM Installation script for Vehicle Light Inspection System
REM For Windows production deployment

echo ========================================
echo Vehicle Light Inspection System
echo Installation Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Checking Python installation...
python --version
echo.

echo [2/4] Creating necessary directories...
if not exist "logs" mkdir logs
if not exist "training_data\running_lights" mkdir training_data\running_lights
if not exist "training_data\hazard_lights" mkdir training_data\hazard_lights
if not exist "output" mkdir output
echo Directories created.
echo.

echo [3/4] Installing Python dependencies...
echo This may take a few minutes...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)
echo.
echo Dependencies installed successfully!
echo.

echo [4/4] Verifying installation...
python -c "import cv2; import numpy; import sklearn; print('All dependencies verified!')"
if errorlevel 1 (
    echo.
    echo WARNING: Some dependencies may not be installed correctly
    echo Please check the error messages above
    pause
    exit /b 1
)
echo.

echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo You can now run the inspection system:
echo   - Double-click: start_inspection.bat
echo   - Or run: python inspection_app.py
echo.
echo For training a model (optional):
echo   - Add videos to training_data folders
echo   - Run: python train_model.py
echo.
pause

