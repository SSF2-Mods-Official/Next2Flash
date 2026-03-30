@echo off
setlocal

cd /d "%~dp0\.."

set "SOURCE_DIR=C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data"
set "REPORT=test\roundtrip_report.json"

echo Running SWF roundtrip test...
echo Source: %SOURCE_DIR%
echo Report: %REPORT%
echo.

python test\roundtrip_all.py "%SOURCE_DIR%" -o "%REPORT%"

echo.
echo Done. Report saved to %REPORT%
pause
