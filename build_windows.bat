@echo off
echo Building MBOX Email Viewer...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Clean previous builds
echo Cleaning previous builds...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del *.spec 2>nul

REM Build with PyInstaller
echo Building executable...
pyinstaller --onefile --windowed ^
    --name "MBOX Email Viewer" ^
    --icon assets\icon.ico ^
    --add-data "assets;assets" ^
    --hidden-import email.mime.multipart ^
    --hidden-import email.mime.text ^
    --hidden-import email.mime.base ^
    src\main.py

echo.
echo Build complete! Check the dist folder.
pause