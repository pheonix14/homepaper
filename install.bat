@echo off
echo =========================================
echo       Homepaper Installation Script
echo =========================================

echo.
echo [1/2] Creating virtual environment...
python -m venv venv
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to create virtual environment. Make sure Python is installed.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2/2] Installing dependencies (this may take a minute)...
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\python.exe -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to install dependencies.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo =========================================
echo Installation complete! You can now run the app using run.bat
echo =========================================
pause
