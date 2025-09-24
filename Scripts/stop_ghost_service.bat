@echo off
REM G.H.O.S.T. Background Service Stop Script
REM This script stops the G.H.O.S.T. background service

title Stop G.H.O.S.T. Service

echo Stopping G.H.O.S.T. Background Service...
echo.

REM Try to stop gracefully first by finding the process
echo Looking for G.H.O.S.T. processes...

REM Find Python processes that might be G.H.O.S.T.
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fi "windowtitle eq G.H.O.S.T.*" /fo csv ^| find /v "PID"') do (
    echo Found G.H.O.S.T. process with PID %%i
    echo Stopping process %%i...
    taskkill /pid %%i /f >nul 2>&1
)

for /f "tokens=2" %%i in ('tasklist /fi "imagename eq pythonw.exe" /fi "windowtitle eq G.H.O.S.T.*" /fo csv ^| find /v "PID"') do (
    echo Found G.H.O.S.T. background process with PID %%i
    echo Stopping process %%i...
    taskkill /pid %%i /f >nul 2>&1
)

REM Alternative method - kill by command line pattern
wmic process where "name='python.exe' and commandline like '%%main.py%%background%%'" delete >nul 2>&1
wmic process where "name='pythonw.exe' and commandline like '%%main.py%%background%%'" delete >nul 2>&1

echo.
echo Checking if G.H.O.S.T. processes are stopped...

REM Verify processes are stopped
tasklist /fi "imagename eq python.exe" /fi "windowtitle eq G.H.O.S.T.*" >nul 2>&1
if errorlevel 1 (
    tasklist /fi "imagename eq pythonw.exe" /fi "windowtitle eq G.H.O.S.T.*" >nul 2>&1
    if errorlevel 1 (
        echo SUCCESS: G.H.O.S.T. background service stopped
    ) else (
        echo WARNING: Some G.H.O.S.T. processes may still be running
    )
) else (
    echo WARNING: Some G.H.O.S.T. processes may still be running
)

echo.
echo Press any key to close this window...
pause >nul
