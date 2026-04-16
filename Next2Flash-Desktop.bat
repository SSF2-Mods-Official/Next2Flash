@echo off
:: Launch Next2Flash Desktop without a console window.
:: Invokes electron.exe directly — no cmd/npx intermediary.

set "ELECTRON_EXE=%~dp0electron\node_modules\electron\dist\electron.exe"
set "ELECTRON_DIR=%~dp0electron"

if not exist "%ELECTRON_EXE%" (
    echo  ERROR: electron.exe not found.
    echo  Run "npm install" in the electron folder first.
    pause
    exit /b 1
)

start "" "%ELECTRON_EXE%" "%ELECTRON_DIR%"
exit
