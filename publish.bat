@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "ROOT=%CD%"
set "PY=%ROOT%\dist\python"
set "ELECTRON=%ROOT%\app\electron"
set "UNPACKED=%ROOT%\dist\pack\win-unpacked"
set "RELEASE=%ROOT%\Next2Flash Release"

echo.
echo  Building Next2Flash Release...
echo.

if exist "%PY%\pythonw.exe" goto have_python
echo  Preparing private Python...
call :prepare_python
if errorlevel 1 goto fail

:have_python
if exist "%ELECTRON%\node_modules\electron\dist\electron.exe" goto have_electron
echo  Installing Electron...
pushd "%ELECTRON%"
call npm install
if errorlevel 1 (
    popd
    echo  ERROR: npm install failed.
    goto fail
)
popd

:have_electron
echo  Packaging the app...
taskkill /f /im Next2Flash.exe >nul 2>&1
if exist "%UNPACKED%" rmdir /s /q "%UNPACKED%"

set CSC_IDENTITY_AUTO_DISCOVERY=false
set WIN_CSC_LINK=
pushd "%ELECTRON%"
call npx electron-builder --win dir
set "PACKERR=%ERRORLEVEL%"
popd
if not "%PACKERR%"=="0" (
    echo  ERROR: electron-builder failed.
    goto fail
)
if not exist "%UNPACKED%\Next2Flash.exe" (
    echo  ERROR: Next2Flash.exe was not produced.
    goto fail
)

echo  Writing the release folder...
if exist "%RELEASE%" rmdir /s /q "%RELEASE%"
if exist "%RELEASE%" (
    echo  ERROR: Could not replace "%RELEASE%". Close that folder and re-run publish.bat.
    goto fail
)
mkdir "%RELEASE%"
move "%UNPACKED%" "%RELEASE%\runtime" >nul
if not exist "%RELEASE%\runtime\Next2Flash.exe" (
    echo  ERROR: Could not move the app into "%RELEASE%\runtime".
    goto fail
)
if not exist "%RELEASE%\runtime\resources\python\pythonw.exe" (
    echo  ERROR: Bundled Python is missing from the release.
    goto fail
)
set "CSC=%WINDIR%\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
if not exist "%CSC%" (
    echo  ERROR: The .NET Framework compiler is missing. The launcher needs it.
    goto fail
)
"%PY%\python.exe" "%ROOT%\app\lib\app_icon.py" "%ROOT%\app\icon.png" "%ROOT%\dist\icon.ico"
if errorlevel 1 (
    echo  ERROR: Could not build the app icon.
    goto fail
)
"%CSC%" /nologo /target:winexe /optimize+ /win32icon:"%ROOT%\dist\icon.ico" /out:"%RELEASE%\Next2Flash.exe" /reference:System.Windows.Forms.dll "%ELECTRON%\launcher.cs"
if errorlevel 1 (
    echo  ERROR: Could not compile the launcher.
    goto fail
)
"%PY%\python.exe" "%ROOT%\app\lib\app_icon.py" "%ROOT%\app\icon.png" "%ROOT%\dist\icon.ico" "%RELEASE%\runtime\Next2Flash.exe"
if errorlevel 1 (
    echo  ERROR: Could not set the app icon.
    goto fail
)

echo.
echo  Ready: "%RELEASE%"
echo  Run Next2Flash.exe in that folder.
echo.
explorer "%RELEASE%"
goto end

:prepare_python
set "PYVER=3.13.3"
set "ZIP=%ROOT%\dist\python-embed.zip"
if not exist "%ROOT%\dist" mkdir "%ROOT%\dist"
echo  Downloading Python %PYVER%...
powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/%PYVER%/python-%PYVER%-embed-amd64.zip' -OutFile '%ZIP%'"
if errorlevel 1 (
    echo  ERROR: Could not download Python.
    exit /b 1
)
mkdir "%PY%"
powershell -NoProfile -Command "Expand-Archive -LiteralPath '%ZIP%' -DestinationPath '%PY%' -Force"
if errorlevel 1 (
    echo  ERROR: Could not unpack Python.
    exit /b 1
)
del /f /q "%ZIP%"
powershell -NoProfile -Command "$p = Get-ChildItem -LiteralPath '%PY%' -Filter 'python*._pth' | Select-Object -First 1; $zipName = $p.BaseName + '.zip'; Set-Content -LiteralPath $p.FullName -Value @($zipName, '.', 'Lib\site-packages', 'import site') -Encoding ascii"
powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%PY%\get-pip.py'"
if errorlevel 1 (
    echo  ERROR: Could not download pip.
    exit /b 1
)
"%PY%\python.exe" "%PY%\get-pip.py" --no-warn-script-location
if errorlevel 1 (
    echo  ERROR: pip install failed.
    exit /b 1
)
"%PY%\python.exe" -m pip install --no-warn-script-location -r "%ROOT%\app\requirements.txt"
if errorlevel 1 (
    echo  ERROR: Could not install Pillow and msgpack.
    exit /b 1
)
del /f /q "%PY%\get-pip.py"
exit /b 0

:fail
echo.
echo  Publish failed.
if not defined N2F_NO_PAUSE pause
exit /b 1

:end
if not defined N2F_NO_PAUSE pause
exit /b 0
