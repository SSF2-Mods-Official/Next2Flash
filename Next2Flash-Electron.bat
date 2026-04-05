@echo off
title Next2Flash (Electron)
echo.
echo  Starting Next2Flash Desktop...
echo.

cd /d "%~dp0electron"
npm start

if errorlevel 1 (
    echo.
    echo  ERROR: Electron app failed to start.
    echo  Make sure you ran "npm install" in the electron folder.
    echo.
    pause
)
