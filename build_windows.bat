@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

set PYTHON_BIN=python
if exist ".venv\Scripts\python.exe" set PYTHON_BIN=.venv\Scripts\python.exe

%PYTHON_BIN% scripts\ensure_release_icons.py
if errorlevel 1 exit /b %errorlevel%

%PYTHON_BIN% -m PyInstaller --clean --noconfirm lucid.spec
if errorlevel 1 exit /b %errorlevel%

for /f "delims=" %%i in ('%PYTHON_BIN% -c "from pathlib import Path; ns = {}; exec(Path('src/hgpt_ai_os/version.py').read_text(), ns); print(ns['APP_RELEASE'])"') do set APP_RELEASE=%%i

if not exist release\Windows mkdir release\Windows
if not exist release\Installer mkdir release\Installer
if not exist release\ReleaseNotes mkdir release\ReleaseNotes
if not exist installer mkdir installer

if exist release\Windows\LUCID rmdir /s /q release\Windows\LUCID
xcopy /E /I /Y dist\LUCID release\Windows\LUCID
if errorlevel 1 exit /b %errorlevel%

copy /Y dist\LUCID\LUCID.exe release\Windows\LUCID.exe
if errorlevel 1 exit /b %errorlevel%

copy /Y RELEASE_NOTES.md release\ReleaseNotes\RELEASE_NOTES.md
if errorlevel 1 exit /b %errorlevel%

%PYTHON_BIN% scripts\write_inno_script.py
if errorlevel 1 exit /b %errorlevel%

where ISCC.exe >nul 2>nul
if %errorlevel%==0 (
    ISCC.exe installer\LUCID.iss
    if errorlevel 1 exit /b %errorlevel%
    if exist "release\Installer\LUCID Setup.exe" copy /Y "release\Installer\LUCID Setup.exe" "release\Windows\LUCID Setup.exe"
) else (
    echo Inno Setup not detected. Installer script generated: installer\LUCID.iss
)

echo Windows release ready: %APP_RELEASE%
echo release\Windows\LUCID.exe
echo release\Windows\LUCID
echo installer\LUCID.iss
