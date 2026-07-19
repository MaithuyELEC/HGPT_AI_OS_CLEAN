@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

if not defined PYINSTALLER_CONFIG_DIR set PYINSTALLER_CONFIG_DIR=%CD%\work\pyinstaller-config
if not exist "%PYINSTALLER_CONFIG_DIR%" mkdir "%PYINSTALLER_CONFIG_DIR%"

set PYTHON_BIN=python
if exist ".venv\Scripts\python.exe" set PYTHON_BIN=.venv\Scripts\python.exe

%PYTHON_BIN% scripts\ensure_release_icons.py
if errorlevel 1 exit /b %errorlevel%

%PYTHON_BIN% -m PyInstaller --clean --noconfirm lucid.spec
if errorlevel 1 exit /b %errorlevel%

%PYTHON_BIN% scripts\classify_pyinstaller_warnings.py
if errorlevel 1 exit /b %errorlevel%

if not exist dist\LUCID\LUCID.exe (
    echo ERROR: expected PyInstaller OneDir executable missing: dist\LUCID\LUCID.exe
    exit /b 1
)

%PYTHON_BIN% installer\verify.py windows
if errorlevel 1 exit /b %errorlevel%

if not exist release\Installer mkdir release\Installer

for /f "delims=" %%i in ('%PYTHON_BIN% -c "from pathlib import Path; ns = {}; exec(Path('src/hgpt_ai_os/version.py').read_text(), ns); print(ns['APP_VERSION'].removeprefix('v'))"') do set APP_VERSION=%%i
for /f "delims=" %%i in ('%PYTHON_BIN% -c "from pathlib import Path; ns = {}; exec(Path('src/hgpt_ai_os/version.py').read_text(), ns); print(ns['APP_RELEASE'])"') do set APP_RELEASE=%%i

where ISCC.exe >nul 2>nul
if %errorlevel%==0 (
    ISCC.exe /DMyAppVersion=%APP_VERSION% "/DMyAppRelease=%APP_RELEASE%" installer\LUCID.iss
    if errorlevel 1 exit /b %errorlevel%
) else (
    echo ERROR: Inno Setup compiler ISCC.exe was not found.
    exit /b 1
)

set INSTALLER_NAME=Lucid-AI-Studio-Setup-v%APP_VERSION%.exe

if not exist release\Installer\%INSTALLER_NAME% (
    echo ERROR: expected installer missing: release\Installer\%INSTALLER_NAME%
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command "$installer = 'release\Installer\%INSTALLER_NAME%'; $hash = Get-FileHash -Algorithm SHA256 -LiteralPath $installer; ($hash.Hash.ToLowerInvariant() + '  %INSTALLER_NAME%') | Set-Content -NoNewline -Encoding ascii -Path ($installer + '.sha256')"
if errorlevel 1 exit /b %errorlevel%

echo Windows release ready: %APP_RELEASE%
echo dist\LUCID\LUCID.exe
echo release\Installer\%INSTALLER_NAME%
echo release\Installer\%INSTALLER_NAME%.sha256
echo installer\LUCID.iss
