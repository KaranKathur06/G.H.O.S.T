@echo off
REM Install G.H.O.S.T. to Windows Startup
REM This script adds G.H.O.S.T. to automatically start with Windows

title Install G.H.O.S.T. Startup

echo Installing G.H.O.S.T. to Windows Startup...
echo.

REM Get the current directory (where G.H.O.S.T. is located)
set "GHOST_DIR=%~dp0\.."
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

REM Create startup shortcut
echo Creating startup shortcut...

REM Use PowerShell to create a proper shortcut
powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTUP_DIR%\G.H.O.S.T. Assistant.lnk'); $Shortcut.TargetPath = '%GHOST_DIR%\scripts\start_ghost_service.bat'; $Shortcut.WorkingDirectory = '%GHOST_DIR%'; $Shortcut.Description = 'G.H.O.S.T. Virtual Assistant - Background Service'; $Shortcut.Save()}"

if exist "%STARTUP_DIR%\G.H.O.S.T. Assistant.lnk" (
    echo SUCCESS: G.H.O.S.T. has been added to Windows startup
    echo G.H.O.S.T. will now start automatically when Windows boots
    echo.
    echo Startup shortcut location: %STARTUP_DIR%\G.H.O.S.T. Assistant.lnk
) else (
    echo ERROR: Failed to create startup shortcut
    echo You may need to run this script as Administrator
)

echo.
echo Additional Setup Options:
echo.
echo 1. To start G.H.O.S.T. now: Run start_ghost_service.bat
echo 2. To remove from startup: Run uninstall_startup.bat
echo 3. To test the service: Say "Ghost" after starting
echo.

REM Ask if user wants to start G.H.O.S.T. now
set /p choice="Would you like to start G.H.O.S.T. now? (y/n): "
if /i "%choice%"=="y" (
    echo Starting G.H.O.S.T. background service...
    call "%~dp0\start_ghost_service.bat"
)

echo.
echo Press any key to close this window...
pause >nul
