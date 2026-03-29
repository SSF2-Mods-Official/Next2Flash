@echo off
REM ============================================================
REM  Next2Flash — Rebuild & Launch (Debug)
REM  Usage:  rebuild.bat          — build + launch
REM          rebuild.bat build    — build only (no launch)
REM          rebuild.bat run      — launch only (skip build)
REM          rebuild.bat release  — full release build (NSIS+MSI)
REM ============================================================
setlocal

set "PROJECT_DIR=%~dp0"
set "PATH=%USERPROFILE%\.cargo\bin;%PATH%"

cd /d "%PROJECT_DIR%"

REM --- Run Python tests first (fast sanity check) ---
if /i "%1"=="run" goto :launch
echo.
echo === Running Python tests ===
python -m pytest test_swf_export.py test_swf_roundtrip.py --tb=short -q
if errorlevel 1 (
    echo.
    echo *** Tests FAILED — fix errors before building ***
    pause
    exit /b 1
)
echo.

REM --- Release build ---
if /i "%1"=="release" (
    echo === Building RELEASE bundle ===
    call npx tauri build
    if errorlevel 1 (
        echo *** Release build FAILED ***
        pause
        exit /b 1
    )
    echo.
    echo === Release build complete ===
    echo   EXE:  src-tauri\target\release\next2flash.exe
    echo   NSIS: src-tauri\target\release\bundle\nsis\Next2Flash_1.0.0_x64-setup.exe
    echo   MSI:  src-tauri\target\release\bundle\msi\Next2Flash_1.0.0_x64_en-US.msi
    pause
    exit /b 0
)

if /i "%1"=="build" goto :build_only

REM --- Default: build debug + launch ---
:build_and_run
echo === Building DEBUG + Launching ===
call npx tauri dev
exit /b %errorlevel%

:build_only
echo === Building DEBUG (no launch) ===
cd /d "%PROJECT_DIR%src-tauri"
cargo build
if errorlevel 1 (
    echo *** Debug build FAILED ***
    pause
    exit /b 1
)
echo.
echo === Debug build complete ===
echo   EXE: src-tauri\target\debug\next2flash.exe
pause
exit /b 0

:launch
echo === Launching (skip build) ===
echo Starting Python server...
start /b python server.py
timeout /t 2 /nobreak >nul
echo Starting app...
start "" "%PROJECT_DIR%src-tauri\target\release\next2flash.exe"
exit /b 0
