@echo off
setlocal

cd /d "%~dp0\.."

rem Set SOURCE_DIR to your local SWF source folder, or pass it as an argument:
if "%~1" neq "" (set "SOURCE_DIR=%~1") else (set "SOURCE_DIR=C:\path\to\your\swf\data")
set "REPORT=test\roundtrip_report.json"

echo Running SWF roundtrip test...
echo Source: %SOURCE_DIR%
echo Report: %REPORT%
echo.

python test\roundtrip_all.py "%SOURCE_DIR%" -o "%REPORT%"

echo.
echo Done. Report saved to %REPORT%
pause
