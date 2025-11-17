@echo off
echo VTuber Tracker - Quick Start Script (Windows)
echo ============================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python could not be found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo pip could not be found. Please install pip
    pause
    exit /b 1
)

echo Installing dependencies...
pip install opencv-python mediapipe pyqt5 python-osc websocket-client requests numpy pyfakewebcam

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Dependencies installed successfully!
    echo.
    echo To start the application:
    echo   python run_app.py
    echo.
    echo To start with Android camera:
    echo   python run_app.py --stream-url http://[ANDROID_IP]:8080/video
    echo.
    echo For help:
    echo   python run_app.py --help
    echo.
    echo Press any key to exit...
    pause >nul
) else (
    echo Failed to install dependencies.
    pause
    exit /b 1
)