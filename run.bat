@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Local environment missing. Starting setup...
  call install_and_run.bat
  exit /b %errorlevel%
)
".venv\Scripts\python.exe" app.py
