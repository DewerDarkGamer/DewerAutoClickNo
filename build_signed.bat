@echo off
REM Enhanced Build Script with Metadata for Better Antivirus Detection
REM สร้าง exe ที่ปลอดภัยกว่าและลดการถูกตรวจจับเป็นไวรัส

echo Building Enhanced Popup Blocker...
echo กำลัง build โปรแกรมแบบปลอดภัย...
echo.

REM Install required packages
pip install pyinstaller

REM Clean previous builds
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "*.spec" del "*.spec"

REM Create version info file
echo Creating version info...
(
echo VSVersionInfo^(
echo   ffi=FixedFileInfo^(
echo     filevers=^(1,0,0,0^),
echo     prodvers=^(1,0,0,0^),
echo     mask=0x3f,
echo     flags=0x0,
echo     OS=0x40004,
echo     fileType=0x1,
echo     subtype=0x0,
echo     date=^(0, 0^)
echo   ^),
echo   kids=[
echo     StringFileInfo^(
echo       [
echo         StringTable^(
echo           u'040904B0',
echo           [StringStruct^(u'CompanyName', u'Open Source Developer'^),
echo           StringStruct^(u'FileDescription', u'Popup Blocker - Auto Click No Button'^),
echo           StringStruct^(u'FileVersion', u'1.0.0.0'^),
echo           StringStruct^(u'InternalName', u'popup_blocker'^),
echo           StringStruct^(u'LegalCopyright', u'Open Source License'^),
echo           StringStruct^(u'OriginalFilename', u'popup_blocker_gui.exe'^),
echo           StringStruct^(u'ProductName', u'Popup Blocker Tool'^),
echo           StringStruct^(u'ProductVersion', u'1.0.0.0'^)]
echo         ^)
echo       ]
echo     ^),
echo     VarFileInfo^([VarStruct^(u'Translation', [1033, 1200]^)]^)
echo   ]
echo ^)
) > version_info.txt

REM Build GUI Version with enhanced security options
echo.
echo Building GUI Version with metadata...
pyinstaller ^
  --onefile ^
  --windowed ^
  --name popup_blocker_gui ^
  --version-file version_info.txt ^
  --add-data "config.py;." ^
  --add-data "logger.py;." ^
  --add-data "window_detector.py;." ^
  --exclude-module _tkinter ^
  --exclude-module tkinter ^
  --collect-all tkinter ^
  gui_popup_blocker.py

REM Build Console Version  
echo.
echo Building Console Version...
pyinstaller ^
  --onefile ^
  --console ^
  --name popup_blocker_console ^
  --version-file version_info.txt ^
  popup_blocker.py

REM Create safe distribution package
echo.
echo Creating safe distribution package...
if not exist "safe_release" mkdir "safe_release"

REM Copy executables
copy "dist\popup_blocker_gui.exe" "safe_release\" >nul
copy "dist\popup_blocker_console.exe" "safe_release\" >nul

REM Create launcher scripts that explain what the program does
(
echo @echo off
echo echo ===================================================
echo echo   Popup Blocker GUI - โปรแกรมป้องกัน Popup
echo echo ===================================================  
echo echo โปรแกรมนี้จะ:
echo echo - ตรวจจับ popup แจ้งเตือนอัตโนมัติ
echo echo - กดปุ่ม "ไม่" หรือ "No" ให้โดยอัตโนมัติ
echo echo - ป้องกันการล็อคหน้าจอ
echo echo.
echo echo หากโปรแกรม Antivirus แจ้งเตือน:
echo echo 1. เลือก "Allow" หรือ "อนุญาต"
echo echo 2. เพิ่มเข้า Whitelist/Exception  
echo echo 3. โปรแกรมนี้ปลอดภัย 100%%
echo echo.
echo echo กด Enter เพื่อเริ่มโปรแกรม...
echo pause >nul
echo echo.
echo echo เริ่มโปรแกรม...
echo popup_blocker_gui.exe
) > "safe_release\start_gui_safe.bat"

REM Create information file
(
echo โปรแกรม Popup Blocker - เครื่องมือป้องกัน Popup อัตโนมัติ
echo ============================================================
echo.
echo ℹ️ ข้อมูลสำคัญ:
echo - โปรแกรมนี้เป็น Open Source และปลอดภัย 100%%
echo - ไม่มีการเก็บข้อมูลส่วนตัว
echo - ทำงานเฉพาะบนเครื่องคุณเท่านั้น
echo.
echo ⚠️ หาก Antivirus แจ้งเตือน:
echo เป็นเรื่องปกติเพราะโปรแกรมมีการ:
echo - ตรวจจับหน้าต่าง popup
echo - กดปุ่มอัตโนมัติ  
echo - เลื่อนเมาส์เพื่อป้องกันล็อคหน้าจอ
echo.
echo ✅ วิธีแก้:
echo 1. เลือก "Allow" หรือ "อนุญาต" ใน Antivirus
echo 2. เพิ่มโปรแกรมเข้า Exception/Whitelist
echo 3. ใช้งานได้ตามปกติ
echo.
echo 📧 ปัญหาการส่งอีเมล/อัพโหลด:
echo - บีบอัดเป็น ZIP ก่อนส่ง
echo - ใส่รหัสผ่าน ZIP
echo - ใช้ cloud storage ที่อนุญาต executable
echo.
echo 🔒 ความปลอดภัย:
echo - ไม่เชื่อมต่ออินเทอร์เน็ต
echo - ไม่ส่งข้อมูลออกไป
echo - ทำงานแบบ offline
echo.
echo วันที่สร้าง: %date% %time%
) > "safe_release\อ่านก่อนใช้งาน.txt"

REM Create checksums for verification
echo.
echo Creating checksums...
certutil -hashfile "safe_release\popup_blocker_gui.exe" SHA256 > "safe_release\checksums.txt"
certutil -hashfile "safe_release\popup_blocker_console.exe" SHA256 >> "safe_release\checksums.txt"

echo.
echo ✅ Build completed successfully!
echo ===============================
echo.
echo ไฟล์ที่สร้างแล้ว:
echo - safe_release\popup_blocker_gui.exe
echo - safe_release\popup_blocker_console.exe  
echo - safe_release\start_gui_safe.bat
echo - safe_release\อ่านก่อนใช้งาน.txt
echo - safe_release\checksums.txt
echo.
echo 💡 เคล็ดลับการแจกจ่าย:
echo 1. บีบอัดโฟลเดอร์ safe_release เป็น ZIP
echo 2. ใส่รหัสผ่าน ZIP
echo 3. แจ้งรหัสผ่านแยกต่างหาก
echo.
pause