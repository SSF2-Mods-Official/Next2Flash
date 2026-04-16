@echo off
title Next2Flash
echo.
echo  Starting Next2Flash...
echo.

:: Check if a server is already running on port 5000
echo  Checking for existing server on port 5000...
for /f "tokens=5" %%p in ('netstat -ano 2^>nul ^| findstr ":5000 " ^| findstr "LISTENING"') do (
    echo  Next2Flash is already running. Opening browser...
    start "" "http://localhost:5000"
    echo.
    echo  Brought existing instance to front.
    echo.
    timeout /t 3 /nobreak >nul
    exit /b 0
)

python "%~dp0app\server.py" %*

echo.
if errorlevel 1 (
    echo  ERROR: Server exited with an error.
    echo  Make sure Python 3.8+ is installed and on your PATH.
) else (
    echo  Server stopped.
)
echo.
pause
