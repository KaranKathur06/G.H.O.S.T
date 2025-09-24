@echo off
REM G.H.O.S.T. Background Service Startup Script
REM This script starts G.H.O.S.T. in background mode without a visible window

title G.H.O.S.T. Background Service

echo Starting G.H.O.S.T. Background Service...
echo.

REM Change to G.H.O.S.T. directory
cd /d "%~dp0\.."

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
python -c "import pystray, PIL, pyaudio, vosk" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Some dependencies may be missing
    echo Installing required packages...
    pip install pystray pillow pyaudio vosk pyttsx3 psutil
)

REM Create logs directory if it doesn't exist
if not exist "data\logs" mkdir "data\logs"

REM Start G.H.O.S.T. in background mode
echo Starting G.H.O.S.T. in background mode...
echo G.H.O.S.T. will run silently in the system tray
echo To stop G.H.O.S.T., right-click the tray icon and select "Exit"
echo.

REM Run without console window (use pythonw for silent operation)
start "G.H.O.S.T. Background" /min pythonw main.py --background --no-console

REM Wait a moment to check if it started successfully
timeout /t 3 /nobreak >nul

REM Check if process is running
tasklist /fi "imagename eq pythonw.exe" /fi "windowtitle eq G.H.O.S.T. Background*" >nul 2>&1
if errorlevel 1 (
    echo WARNING: G.H.O.S.T. may not have started successfully
    echo Check the log files in data\logs\ for errors
) else (
    echo SUCCESS: G.H.O.S.T. is now running in the background
    echo Look for the G.H.O.S.T. icon in your system tray
)

echo.
echo Press any key to close this window...
pause >nul
