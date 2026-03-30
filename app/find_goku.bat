@echo off
echo ============================================
echo Search for Goku SWF/SSF files
echo ============================================
echo.
echo Searching common locations...
echo.

set FOUND=0

echo Checking app\converted folder...
if exist "converted\goku.swf" (
    echo FOUND: converted\goku.swf
    set FOUND=1
)
if exist "converted\goku.ssf" (
    echo FOUND: converted\goku.ssf
    set FOUND=1
)
if exist "converted\goku\*.swf" (
    echo FOUND: converted\goku\*.swf
    dir /b /s "converted\goku\*.swf"
    set FOUND=1
)
if exist "converted\goku\*.ssf" (
    echo FOUND: converted\goku\*.ssf
    dir /b /s "converted\goku\*.ssf"
    set FOUND=1
)

echo.
echo Checking parent directory...
if exist "..\goku.swf" (
    echo FOUND: ..\goku.swf
    set FOUND=1
)
if exist "..\goku.ssf" (
    echo FOUND: ..\goku.ssf
    set FOUND=1
)

echo.
echo Searching deeper (this may take a moment)...
for /r "." %%F in (goku*.swf goku*.ssf) do (
    if exist "%%F" (
        echo FOUND: %%F
        set FOUND=1
    )
)

echo.
if %FOUND%==0 (
    echo ============================================
    echo No goku files found in this directory tree
    echo ============================================
    echo.
    echo Please manually locate your goku.swf or goku.ssf file.
    echo It may be in:
    echo   - Your SSF2 game directory
    echo   - Downloads folder
    echo   - Desktop
    echo.
    echo Once found, run:
    echo   reconvert_to_msgpack.bat "path\to\goku.swf" goku_msgpack.n2d
    echo.
) else (
    echo.
    echo ============================================
    echo Found file(s) above
    echo ============================================
    echo.
    echo To convert, run:
    echo   reconvert_to_msgpack.bat "path\from\above" goku_msgpack.n2d
    echo.
)

pause
