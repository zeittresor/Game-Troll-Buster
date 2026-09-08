@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Run install_and_run.bat first.
  pause
  exit /b 1
)

".venv\Scripts\python.exe" -m pip install pyinstaller
if errorlevel 1 goto :fail

rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q "Game Troll Buster.spec" 2>nul

".venv\Scripts\python.exe" -m PyInstaller ^
  --noconfirm --clean --windowed ^
  --name "Game Troll Buster" ^
  --add-data "assets;assets" ^
  --collect-all steam ^
  app.py

if errorlevel 1 goto :fail

echo.
echo Build created:
echo   dist\Game Troll Buster\
pause
exit /b 0

:fail
echo.
echo Build failed.
pause
exit /b 1
