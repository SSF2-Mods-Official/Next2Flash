@echo off
setlocal EnableDelayedExpansion
title Next2Flash - Build Release

echo.
echo  ==============================================
echo   Next2Flash - Build Windows Release
echo  ==============================================
echo.

set "ROOT=%~dp0"
set "APP_DIR=%ROOT%app"
set "ELECTRON_DIR=%ROOT%electron"
set "BUILD_DIR=%ROOT%build"
set "UNPACKED=%BUILD_DIR%\win-unpacked"
set "ZIPOUT=%BUILD_DIR%\Next2Flash-win-x64.zip"

:: ---------- Check prerequisites ------------------------------------------
where python >nul 2>&1
if errorlevel 1 (
    echo  ERROR: python not found on PATH.
    echo  Install Python 3.8+ from https://python.org
    goto :fail
)
where node >nul 2>&1
if errorlevel 1 (
    echo  ERROR: node.js not found on PATH.
    echo  Install Node.js LTS from https://nodejs.org
    goto :fail
)
where npm >nul 2>&1
if errorlevel 1 (
    echo  ERROR: npm not found on PATH.
    goto :fail
)

:: ---------- Step 1: Install Python deps + PyInstaller --------------------
echo  [1/6] Installing Python dependencies...
python -m pip install --quiet -r "%APP_DIR%\requirements.txt"
if errorlevel 1 ( echo  ERROR: pip install failed. & goto :fail )
python -m pip install --quiet pyinstaller
if errorlevel 1 ( echo  ERROR: Failed to install PyInstaller. & goto :fail )
echo  Python deps OK.
echo.

:: ---------- Step 2: Bundle server.py into server.exe ---------------------
echo  [2/6] Bundling Python server into server.exe...
echo  (Takes 1-3 minutes on first run)
echo.

if exist "%APP_DIR%\dist\server.exe" del /f /q "%APP_DIR%\dist\server.exe"
if exist "%APP_DIR%\build_tmp" rmdir /s /q "%APP_DIR%\build_tmp"

pushd "%APP_DIR%"
python -m PyInstaller ^
    --onefile ^
    --name server ^
    --distpath "%APP_DIR%\dist" ^
    --workpath "%APP_DIR%\build_tmp" ^
    --specpath "%APP_DIR%\build_tmp" ^
    --hidden-import PIL._imaging ^
    --hidden-import msgpack ^
    --collect-submodules as3_decompiler ^
    --noconfirm ^
    --clean ^
    server.py
popd

if not exist "%APP_DIR%\dist\server.exe" (
    echo  ERROR: server.exe not produced. Check output above.
    goto :fail
)
echo  server.exe OK.
echo.

:: ---------- Step 3: Smoke-test server.exe --------------------------------
echo  [3/6] Smoke-testing server.exe...
set "SMOKE_DIR=%TEMP%\n2f_smoke"
if exist "%SMOKE_DIR%" rmdir /s /q "%SMOKE_DIR%"
mkdir "%SMOKE_DIR%"
echo ^<!DOCTYPE html^>^<html^>^<body^>test^</body^>^</html^> > "%SMOKE_DIR%\index.html"

set N2F_WEB_ROOT=%SMOKE_DIR%
set N2F_PORT=15099
set N2F_ELECTRON=1
start /b "" "%APP_DIR%\dist\server.exe"

:: Wait for server.exe to respond (up to 90 seconds - PyInstaller extracts on first run)
echo  Waiting for server.exe to start (first run may take ~60s)...
set SMOKE_OK=0
for /l %%i in (1,1,90) do (
    if !SMOKE_OK!==0 (
        timeout /t 1 /nobreak >nul
        curl -s -o nul -w "%%{http_code}" "http://127.0.0.1:15099/api/health" 2>nul | findstr "200" >nul 2>&1
        if not errorlevel 1 (
            set SMOKE_OK=1
            echo  server.exe responded OK on attempt %%i.
        )
    )
)

:: Kill the smoke-test server process
taskkill /f /im server.exe >nul 2>&1
if exist "%SMOKE_DIR%" rmdir /s /q "%SMOKE_DIR%"

if !SMOKE_OK!==0 (
    echo  ERROR: server.exe did not respond within 90s.
    echo  Check that antivirus is not blocking it.
    goto :fail
)
echo  Smoke test passed.
echo.

:: ---------- Step 4: Build the web UI assets ------------------------------
echo  [4/6] Building web UI assets (gulp)...
pushd "%APP_DIR%"
if not exist node_modules (
    echo  Installing app node dependencies...
    call npm install
    if errorlevel 1 ( popd & goto :fail )
)
call npm run build
set GULPERR=%ERRORLEVEL%
popd
if %GULPERR% neq 0 ( echo  ERROR: npm run build failed. & goto :fail )
echo  Web UI OK.
echo.

:: ---------- Step 5: Install Electron dependencies ------------------------
echo  [5/6] Installing Electron dependencies...
pushd "%ELECTRON_DIR%"
call npm install
set NPMERR=%ERRORLEVEL%
popd
if %NPMERR% neq 0 ( echo  ERROR: npm install failed. & goto :fail )
echo  Electron deps OK.
echo.

:: ---------- Step 6: Package + Zip ----------------------------------------
echo  [6/6] Packaging Electron app...
echo.

if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"

set CSC_IDENTITY_AUTO_DISCOVERY=false
set WIN_CSC_LINK=

pushd "%ELECTRON_DIR%"
npx electron-builder --win dir >nul 2>&1
popd

if not exist "%UNPACKED%\Next2Flash.exe" (
    echo  ERROR: electron-builder did not produce Next2Flash.exe
    goto :fail
)
echo  Electron app built OK.
echo.

echo  Creating ZIP...
if exist "%ZIPOUT%" del /f /q "%ZIPOUT%"
powershell -NoProfile -Command "Compress-Archive -Path '%UNPACKED%\*' -DestinationPath '%ZIPOUT%' -Force"
if not exist "%ZIPOUT%" ( echo  ERROR: ZIP failed. & goto :fail )

for %%f in ("%ZIPOUT%") do set "ZIPSIZE=%%~zf"
set /a ZIPMB=%ZIPSIZE% / 1048576

echo.
echo  ==============================================
echo   BUILD COMPLETE
echo   ZIP:  %ZIPOUT%
echo   Size: ~%ZIPMB% MB
echo  ==============================================
echo.
echo  Distribute the ZIP. Users extract and run
echo  Next2Flash.exe - no Python or Node needed.
echo.
explorer "%BUILD_DIR%"
goto :end

:fail
echo.
echo  *** BUILD FAILED - see errors above ***
echo.
pause
exit /b 1

:end
pause
exit /b 0