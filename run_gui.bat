@echo off
REM GUI Popup Blocker Launcher
REM เรียกใช้โปรแกรม Popup Blocker แบบ GUI

echo Starting GUI Popup Blocker...
echo กำลังเปิดโปรแกรม Popup Blocker แบบ GUI...
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo ข้อผิดพลาด: ไม่พบ Python หรือไม่ได้ตั้งค่า PATH
    pause
    exit /b 1
)

REM Set environment variables (optional)
REM set CHECK_INTERVAL=2.0
REM set DEBUG=false
REM set LOG_FILE=popup_blocker.log

REM Run the GUI popup blocker
python gui_popup_blocker.py

REM Check exit code
if %errorlevel% neq 0 (
    echo.
    echo GUI Popup Blocker exited with error code %errorlevel%
    echo โปรแกรมจบการทำงานด้วยข้อผิดพลาด %errorlevel%
    pause
)

echo.
echo GUI Popup Blocker has stopped.
echo โปรแกรม GUI Popup Blocker หยุดทำงานแล้ว
pause