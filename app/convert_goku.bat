@echo off
setlocal enabledelayedexpansion

echo ============================================
echo Auto-Find and Convert Goku to MessagePack
echo ============================================
echo.

REM Search for goku files
echo Searching for goku SWF/SSF files...
echo.

set GOKU_FILE=
set SEARCH_PATHS=converted ..\converted . ..

for %%P in (%SEARCH_PATHS%) do (
    if exist "%%P\goku.swf" (
        set GOKU_FILE=%%P\goku.swf
        goto :found
    )
    if exist "%%P\goku.ssf" (
        set GOKU_FILE=%%P\goku.ssf
        goto :found
    )
    if exist "%%P\goku\goku.swf" (
        set GOKU_FILE=%%P\goku\goku.swf
        goto :found
    )
    if exist "%%P\goku\goku.ssf" (
        set GOKU_FILE=%%P\goku\goku.ssf
        goto :found
    )
)

REM Deep search
echo Running deep search (may take a moment)...
for /r "." %%F in (goku.swf goku.ssf) do (
    if exist "%%F" (
        set GOKU_FILE=%%F
        goto :found
    )
)

echo.
echo ============================================
echo File Not Found
echo ============================================
echo.
echo Could not automatically find goku.swf or goku.ssf
echo.
echo Please run manually:
echo   reconvert_to_msgpack.bat "full\path\to\goku.swf" goku_msgpack.n2d
echo.
echo Or try find_goku.bat to see all locations
echo.
pause
exit /b 1

:found
echo FOUND: !GOKU_FILE!
echo.
set OUTPUT_FILE=goku_msgpack.n2d

REM Check if output already exists
if exist "!OUTPUT_FILE!" (
    echo WARNING: Output file already exists: !OUTPUT_FILE!
    set /p OVERWRITE="Overwrite? (y/n): "
    if /i not "!OVERWRITE!"=="y" (
        echo Cancelled by user
        pause
        exit /b 0
    )
)

echo.
echo Converting to MessagePack format...
echo Input:  !GOKU_FILE!
echo Output: !OUTPUT_FILE!
echo.
echo This may take several minutes for large files...
echo.

python swf_to_n2d.py "!GOKU_FILE!" "!OUTPUT_FILE!"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo SUCCESS!
    echo ============================================
    echo.
    echo Created: !OUTPUT_FILE!
    echo.
    echo This file uses MessagePack binary format and can handle
    echo large files that exceed the JavaScript string length limit.
    echo.
    echo Next steps:
    echo   1. Load !OUTPUT_FILE! in the Next2D tool
    echo   2. Check console for: [N2F] Loading MessagePack format (binary)
    echo   3. File should load successfully without string length error
    echo.
) else (
    echo.
    echo ============================================
    echo Conversion Failed
    echo ============================================
    echo.
    echo Check the error message above for details.
    echo.
)

pause
