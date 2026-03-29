@echo off
title Next2Flash
echo.
echo  Starting Next2Flash...
echo.
python "%~dp0app\server.py" %*
if errorlevel 1 (
    echo.
    echo  ERROR: Python not found or server failed to start.
    echo  Make sure Python 3.8+ is installed and on your PATH.
    echo.
    pause
)
