@echo off
:: n2f.bat — Shortcut to run the Next2Flash CLI tool
:: Usage: n2f convert input.swf
::        n2f compile input.n2d
::        n2f info input.n2d
::        n2f --help
python "%~dp0n2f.py" %*
