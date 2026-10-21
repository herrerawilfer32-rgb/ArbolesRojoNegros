@echo off
cd /d "%~dp0"
set "TREE_PY=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%TREE_PY%" (
  "%TREE_PY%" app.py
) else (
  python app.py
)
if errorlevel 1 pause
