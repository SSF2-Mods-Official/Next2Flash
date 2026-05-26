@echo off
setlocal enabledelayedexpansion
title Next2Flash (Desktop)
echo.
echo  Starting Next2Flash...
echo.

set "ROOT=%~dp0"
set "APP_DIR=%ROOT%app"
set "ELECTRON_EXE=%ROOT%electron\node_modules\electron\dist\electron.exe"
set "ELECTRON_DIR=%ROOT%electron"

if not exist "%ELECTRON_EXE%" (
    echo  ERROR: Electron not installed.
    echo  Run "npm install" in the electron folder first.
    pause
    exit /b 1
)

where python >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python not found in PATH.
    echo  Install Python 3.9+ and run: pip install flask pillow msgpack
    pause
    exit /b 1
)

:: Kill any process currently listening on port 5000 (handles multiple orphans, not just PID file)
echo  Checking for existing processes on port 5000...
for /f "tokens=5" %%P in ('netstat -ano 2^>nul ^| findstr /C:":5000 " ^| findstr "LISTENING"') do (
    echo  Killing process %%P on port 5000...
    taskkill /PID %%P /F >nul 2>&1
)
:: Also clean up PID file if present
if exist "%APP_DIR%\server.pid" (
    del /f /q "%APP_DIR%\server.pid" 2>nul
)
:: Give OS a moment to release the port
powershell -NoProfile -Command "Start-Sleep -Milliseconds 800" >nul 2>&1

:: Start Python server in a minimized background window
echo  Starting Python server...
start "Next2Flash Server" /MIN /D "%APP_DIR%" python server.py --no-browser

:: Wait up to 30s for the server to respond
echo  Waiting for server (up to 30s)...
powershell -NoProfile -Command "$url='http://127.0.0.1:5000/api/health'; $deadline=(Get-Date).AddSeconds(30); while((Get-Date) -lt $deadline){try{$r=Invoke-WebRequest -Uri $url -TimeoutSec 1 -UseBasicParsing -EA Stop; if($r.StatusCode -eq 200){exit 0}}catch{} Start-Sleep -Milliseconds 500} exit 1"

if errorlevel 1 (
    echo.
    echo  ERROR: Python server did not respond within 30 seconds.
    echo  Check the "Next2Flash Server" window for error details.
    pause
    exit /b 1
)

:launch_electron
echo  Server ready. Launching Electron...
set "N2F_SKIP_SERVER_SPAWN=1"
start "" "%ELECTRON_EXE%" "%ELECTRON_DIR%"
