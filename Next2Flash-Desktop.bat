@echo off
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

:: Check if a server is already running on port 5000
powershell -NoProfile -Command "try{$r=Invoke-WebRequest -Uri 'http://127.0.0.1:5000/api/health' -TimeoutSec 1 -UseBasicParsing -EA Stop; if($r.StatusCode -eq 200){exit 0}}catch{} exit 1" >nul 2>&1
if not errorlevel 1 (
    echo  Server already running on port 5000, reusing it.
    goto :launch_electron
)

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
