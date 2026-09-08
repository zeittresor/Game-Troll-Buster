@echo off
setlocal
cd /d "%~dp0"
title Game Troll Buster - Installer

echo ============================================================
echo   Game Troll Buster v0.2.0 - Local Setup
echo ============================================================
echo.
echo Everything is installed into this project folder.
echo No global Python packages are modified.
echo.

where py >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python launcher "py" was not found.
  echo Install Python 3.11 or 3.12 and enable the Python launcher.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo [1/3] Creating local virtual environment...
  py -3 -m venv .venv
  if errorlevel 1 goto :fail
) else (
  echo [1/3] Reusing existing local virtual environment.
)

echo [2/3] Installing/updating dependencies...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :fail
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :fail

echo [3/3] Starting Game Troll Buster...
".venv\Scripts\python.exe" app.py
exit /b %errorlevel%

:fail
echo.
echo [ERROR] Setup failed. Review the output above.
pause
exit /b 1
