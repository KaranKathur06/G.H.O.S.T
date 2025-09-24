@echo off
REM Remove G.H.O.S.T. from Windows Startup
REM This script removes G.H.O.S.T. from automatic startup

title Uninstall G.H.O.S.T. Startup

echo Removing G.H.O.S.T. from Windows Startup...
echo.

set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_PATH=%STARTUP_DIR%\G.H.O.S.T. Assistant.lnk"

REM Check if shortcut exists
if exist "%SHORTCUT_PATH%" (
    echo Found G.H.O.S.T. startup shortcut
    echo Removing: %SHORTCUT_PATH%
    
    del "%SHORTCUT_PATH%" >nul 2>&1
    
    if not exist "%SHORTCUT_PATH%" (
        echo SUCCESS: G.H.O.S.T. has been removed from Windows startup
        echo G.H.O.S.T. will no longer start automatically with Windows
    ) else (
        echo ERROR: Failed to remove startup shortcut
        echo You may need to run this script as Administrator
    )
) else (
    echo G.H.O.S.T. startup shortcut not found
    echo G.H.O.S.T. is not currently set to start with Windows
)

echo.
echo Note: This only removes the automatic startup.
echo G.H.O.S.T. can still be started manually using start_ghost_service.bat

REM Ask if user wants to stop currently running G.H.O.S.T.
echo.
set /p choice="Would you like to stop any currently running G.H.O.S.T. processes? (y/n): "
if /i "%choice%"=="y" (
    echo Stopping G.H.O.S.T. background service...
    call "%~dp0\stop_ghost_service.bat"
)

echo.
echo Press any key to close this window...
pause >nul
