@echo off
echo ====================================================================
echo Installing G.H.O.S.T. Enhanced Essential Dependencies
echo ====================================================================
echo.

echo Installing core dependencies (this may take a few minutes)...
pip install openai psutil requests numpy fuzzywuzzy python-Levenshtein

echo.
echo Installing speech dependencies...
pip install SpeechRecognition edge-tts pyttsx3

echo.
echo Installing optional dependencies (can be skipped if errors occur)...
pip install pygame pywin32

echo.
echo ====================================================================
echo Installation complete!
echo ====================================================================
echo.
echo You can now run: python ghost_enhanced.py --test
echo.
pause
