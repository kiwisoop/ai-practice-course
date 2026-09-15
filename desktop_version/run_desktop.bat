@echo off
rem Created with Codex on 2026-09-10.
cd /d "%~dp0\.."
if not exist ".venv\Scripts\python.exe" (
  python -m venv .venv || goto :error
)
call ".venv\Scripts\python.exe" -m pip install -r requirements.txt || goto :error
call ".venv\Scripts\python.exe" desktop_version\digit_recognition.py || goto :error
exit /b 0

:error
echo.
echo The application could not start. Check that Python 3.11 is installed.
pause
exit /b 1
