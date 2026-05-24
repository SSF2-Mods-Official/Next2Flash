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
echo  [1/5] Installing Python dependencies...
python -m pip install --quiet -r "%APP_DIR%\requirements.txt"
if errorlevel 1 ( echo  ERROR: pip install failed. & goto :fail )
python -m pip install --quiet pyinstaller
if errorlevel 1 ( echo  ERROR: Failed to install PyInstaller. & goto :fail )
echo  Python deps OK.
echo.

:: ---------- Step 2: Bundle server.py into server.exe ---------------------
echo  [2/5] Bundling Python server into server.exe...
echo  (Takes 1-2 minutes on first run)
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
echo  server.exe OK  (%APP_DIR%\dist\server.exe)
echo.

:: ---------- Step 3: Build the web UI assets ------------------------------
echo  [3/5] Building web UI assets (gulp)...
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

:: ---------- Step 4: Install Electron dependencies ------------------------
echo  [4/5] Installing Electron dependencies...
pushd "%ELECTRON_DIR%"
call npm install
set NPMERR=%ERRORLEVEL%
popd
if %NPMERR% neq 0 ( echo  ERROR: npm install failed. & goto :fail )
echo  Electron deps OK.
echo.

:: ---------- Step 5: Build unpacked app with electron-builder -------------
echo  [5/5] Packaging Electron app...
echo.

if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"

set CSC_IDENTITY_AUTO_DISCOVERY=false
set WIN_CSC_LINK=

pushd "%ELECTRON_DIR%"
:: Run electron-builder. It prints a winCodeSign symlink warning (harmless on
:: Windows) but still produces win-unpacked successfully. We check for the
:: actual output file instead of relying on the exit code.
npx electron-builder --win dir >nul 2>&1
popd

if not exist "%UNPACKED%\Next2Flash.exe" (
    echo  ERROR: electron-builder did not produce Next2Flash.exe
    echo  Try running:  cd electron  then:  npx electron-builder --win dir
    goto :fail
)
echo  Electron app built OK.
echo.

:: ---------- Zip the unpacked folder with PowerShell ----------------------
echo  Creating ZIP archive...
if exist "%ZIPOUT%" del /f /q "%ZIPOUT%"

powershell -NoProfile -Command ^
    "Compress-Archive -Path '%UNPACKED%\*' -DestinationPath '%ZIPOUT%' -Force"

if not exist "%ZIPOUT%" (
    echo  ERROR: ZIP creation failed.
    goto :fail
)

for %%f in ("%ZIPOUT%") do set "ZIPSIZE=%%~zf"
set /a ZIPMB=%ZIPSIZE% / 1048576

echo.
echo  ==============================================
echo   BUILD COMPLETE
echo   ZIP:  %ZIPOUT%
echo   Size: ~%ZIPMB% MB
echo  ==============================================
echo.
echo  Distribute the ZIP. Users extract it and
echo  double-click Next2Flash.exe - no install needed.
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