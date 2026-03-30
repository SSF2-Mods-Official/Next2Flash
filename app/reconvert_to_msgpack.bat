@echo off
echo ============================================
echo Reconvert file to MessagePack format
echo ============================================
echo.
echo This script will convert your SWF file to a MessagePack-based N2D file
echo that can handle files larger than 500MB.
echo.
echo Usage:
echo   reconvert_to_msgpack.bat input.swf output.n2d
echo.
echo Example:
echo   reconvert_to_msgpack.bat goku.swf goku_msgpack.n2d
echo.

if "%~1"=="" (
    echo ERROR: No input file specified
    echo.
    echo Please provide the path to your SWF file as the first argument.
    pause
    exit /b 1
)

if "%~2"=="" (
    echo ERROR: No output file specified
    echo.
    echo Please provide the desired output N2D filename as the second argument.
    pause
    exit /b 1
)

if not exist "%~1" (
    echo ERROR: Input file not found: %~1
    pause
    exit /b 1
)

echo Converting: %~1
echo Output to: %~2
echo.
echo This may take a while for large files...
echo.

python swf_to_n2d.py "%~1" "%~2"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo SUCCESS! MessagePack N2D file created.
    echo ============================================
    echo.
    echo File: %~2
    echo.
    echo You can now load this file in the Next2D tool.
    echo It will use MessagePack binary format and bypass the string length limit.
    echo.
) else (
    echo.
    echo ============================================
    echo ERROR: Conversion failed
    echo ============================================
    echo.
)

pause
