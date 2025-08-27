@echo off
REM Local Build Script for Popup Blocker
REM สำหรับ build exe บนเครื่องตัวเอง

echo Building Popup Blocker executables...
echo กำลัง build โปรแกรม Popup Blocker...
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo ข้อผิดพลาด: ไม่พบ Python หรือไม่ได้ตั้งค่า PATH
    pause
    exit /b 1
)

REM Install PyInstaller if not available
echo Installing PyInstaller...
echo กำลังติดตั้ง PyInstaller...
pip install pyinstaller

REM Clean previous builds
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "*.spec" del "*.spec"

REM Build Console Version
echo.
echo Building Console Version...
echo กำลัง build เวอร์ชัน Console...
pyinstaller --onefile --console --name popup_blocker_console popup_blocker.py

REM Build GUI Version
echo.
echo Building GUI Version...
echo กำลัง build เวอร์ชัน GUI...
pyinstaller --onefile --windowed --name popup_blocker_gui gui_popup_blocker.py

REM Create release folder
echo.
echo Creating release package...
echo กำลังสร้างแพ็กเกจ...
if not exist "release" mkdir "release"
copy "dist\popup_blocker_console.exe" "release\" >nul
copy "dist\popup_blocker_gui.exe" "release\" >nul
copy "run.bat" "release\" >nul
copy "run_gui.bat" "release\" >nul

echo.
echo Build completed successfully!
echo การ build เสร็จสิ้น!
echo.
echo Files created: ไฟล์ที่สร้างแล้ว:
echo - dist\popup_blocker_console.exe (Console version)
echo - dist\popup_blocker_gui.exe (GUI version)  
echo - release\ folder with all files
echo.
echo You can now distribute the files in the 'release' folder
echo คุณสามารถแจกจ่ายไฟล์ในโฟลเดอร์ 'release' ได้แล้ว
pause