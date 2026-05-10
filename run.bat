@echo off
cd /d "%~dp0"
echo Starting InjuryAssist...
if not exist venv (
    echo Virtual environment not found! Please run setup first.
    pause
    exit /b 1
)
call venv\Scripts\activate
python app.py
pause
