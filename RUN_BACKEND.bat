@echo off
echo ================================================
echo    HORROR ORACLE - FLASK + LANGCHAIN BACKEND
echo ================================================
echo.
echo Starting the server...
echo.

REM Check if virtual environment exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Run the Flask app
python app.py

pause


