@echo off
title Next2Flash
echo.
echo  Starting Next2Flash...
echo.

:: Kill any existing server on port 5000
echo  Checking for existing server on port 5000...
for /f "tokens=5" %%p in ('netstat -ano 2^>nul ^| findstr ":5000 " ^| findstr "LISTENING"') do (
    echo  Stopping old server PID %%p...
    taskkill /F /PID %%p >nul 2^>^&1
)
timeout /t 2 /nobreak >nul

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
