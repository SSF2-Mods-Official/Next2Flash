@echo off
setlocal EnableDelayedExpansion
title Next2Flash — Build Release

echo.
echo  =============================================
echo   Next2Flash — Build Release (Windows EXE)
echo  =============================================
echo.

set "ROOT=%~dp0"
set "APP_DIR=%ROOT%app"
set "ELECTRON_DIR=%ROOT%electron"
set "BUILD_DIR=%ROOT%build"

:: ── Check prerequisites ────────────────────────────────────────────────────
where python >nul 2>&1
if errorlevel 1 (
    echo  ERROR: python not found on PATH.
    echo  Install Python 3.8+ from https://python.org
    goto :fail
)

where node >nul 2>&1
if errorlevel 1 (
    echo  ERROR: node.js not found on PATH.
    echo  Install Node.js from https://nodejs.org
    goto :fail
)

where npm >nul 2>&1
if errorlevel 1 (
    echo  ERROR: npm not found on PATH.
    goto :fail
)

:: ── Step 1: Build the web UI assets ───────────────────────────────────────
echo  [1/4] Building web UI (gulp)...
echo.
cd /d "%APP_DIR%"
if not exist node_modules (
    echo  Installing app node dependencies...
    call npm install
    if errorlevel 1 goto :fail
)
call npm run build
if errorlevel 1 (
    echo  ERROR: app npm run build failed.
    goto :fail
)
echo.
echo  Web UI built successfully.
echo.

:: ── Step 2: Install electron dependencies ────────────────────────────────
echo  [2/4] Installing Electron dependencies...
echo.
cd /d "%ELECTRON_DIR%"
call npm install
if errorlevel 1 (
    echo  ERROR: npm install in electron/ failed.
    goto :fail
)
echo.

:: ── Step 3: Clean previous build output ──────────────────────────────────
echo  [3/4] Cleaning previous build folder...
if exist "%BUILD_DIR%" (
    rmdir /s /q "%BUILD_DIR%"
)
echo  Done.
echo.

:: ── Step 4: Build with electron-builder ──────────────────────────────────
echo  [4/4] Building Electron app (portable EXE)...
echo.
cd /d "%ELECTRON_DIR%"
call npx electron-builder --win portable --config.directories.output="..\build"
if errorlevel 1 (
    echo  ERROR: electron-builder failed.
    goto :fail
)

echo.
echo  =============================================
echo   Build complete!
echo   Output: %BUILD_DIR%\
echo  =============================================
echo.
echo  The portable EXE is ready to run — no install required.
echo.
explorer "%BUILD_DIR%"
goto :end

:fail
echo.
echo  Build FAILED. See errors above.
echo.
pause
exit /b 1

:end
pause
exit /b 0
