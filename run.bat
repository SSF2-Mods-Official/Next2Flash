@echo off
setlocal EnableExtensions
cd /d "%~dp0"

:: Usage:
::   run.bat            Start the desktop app (double-click)
::   publish.bat        Build the Next2Flash Release folder

if not "%~1"=="" (
    echo Unknown argument: %~1
    echo Usage: run.bat
    echo To build the release, run publish.bat
    pause
    exit /b 1
)

set "ROOT=%CD%"
set "ELECTRON_EXE=%ROOT%\app\electron\node_modules\electron\dist\electron.exe"
set "ELECTRON_DIR=%ROOT%\app\electron"

if not exist "%ELECTRON_EXE%" (
    echo  ERROR: Electron not installed.
    echo  Run "npm install" in the app\electron folder first.
    pause
    exit /b 1
)

start "" "%ELECTRON_EXE%" "%ELECTRON_DIR%"
exit /b 0
