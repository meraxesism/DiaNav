@echo off
REM Human Detection Safety System Startup Script

echo 🚨 Starting Human Detection Safety System...

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo ✅ Virtual environment activated
)

REM Run the system
python main.py %*
