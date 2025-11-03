@echo off
echo.
echo =========================================================
echo    HORROR ORACLE - QUICK START
echo =========================================================
echo.
echo This will start the backend server that powers the quiz!
echo.
echo IMPORTANT: Keep this window open while using the app!
echo.
echo =========================================================
echo.
pause
echo.
echo Starting server...
echo.

REM Check if virtual environment exists
if exist venv\Scripts\activate.bat (
    echo [1/2] Activating virtual environment...
    call venv\Scripts\activate.bat
    echo.
)

echo [2/2] Starting Flask backend...
echo.
echo =========================================================
echo  LOOK FOR THIS MESSAGE:
echo  "Running on http://127.0.0.1:5000"
echo.
echo  Once you see it, open your browser to:
echo  http://localhost:5000
echo =========================================================
echo.

REM Run the Flask app
python app.py

pause

