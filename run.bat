@echo off
echo Starting Homepaper...

if not exist venv\Scripts\python.exe (
    echo Error: Virtual environment not found! Please run install.bat first.
    pause
    exit /b 1
)

start "" venv\Scripts\pythonw.exe main.py
