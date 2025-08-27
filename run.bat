@echo off
REM Popup Blocker Launcher
REM This batch file starts the popup blocker with proper error handling

echo Starting Popup Blocker...
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python or add it to your system PATH
    pause
    exit /b 1
)

REM Set environment variables (optional)
REM set CHECK_INTERVAL=2.0
REM set DEBUG=false
REM set LOG_FILE=popup_blocker.log

REM Run the popup blocker
python popup_blocker.py

REM Check exit code
if %errorlevel% neq 0 (
    echo.
    echo Popup Blocker exited with error code %errorlevel%
    pause
)

echo.
echo Popup Blocker has stopped.
pause
