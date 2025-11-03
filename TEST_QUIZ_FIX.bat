@echo off
echo.
echo ========================================
echo    TESTING QUIZ LOADING FIX
echo ========================================
echo.
echo This will test if the quiz backend is working...
echo.

python test_quiz_simple.py

echo.
echo ========================================
echo.
echo If you saw "SUCCESS!" above, the backend is working!
echo.
echo Now open your browser and test:
echo   1. Go to http://localhost:5000
echo   2. Click "Face Your Nightmares"
echo   3. The quiz should load in about 3.5 seconds
echo.
echo OR use the diagnostic page:
echo   - Open: test_quiz_frontend.html
echo.
echo ========================================
pause

