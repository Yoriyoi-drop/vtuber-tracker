#!/bin/bash
# Quick start script for VTuber Tracker

echo "VTuber Tracker - Quick Start Script"
echo "==================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Python3 could not be found. Please install Python 3.8+"
    exit 1
fi

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo "pip could not be found. Please install pip"
    exit 1
fi

echo "Installing dependencies..."
pip install opencv-python mediapipe pyqt5 python-osc websocket-client requests numpy pyfakewebcam

if [ $? -eq 0 ]; then
    echo "Dependencies installed successfully!"
    echo ""
    echo "To start the application:"
    echo "  python run_app.py"
    echo ""
    echo "To start with Android camera:"
    echo "  python run_app.py --stream-url http://[ANDROID_IP]:8080/video"
    echo ""
    echo "For help:"
    echo "  python run_app.py --help"
else
    echo "Failed to install dependencies."
fi