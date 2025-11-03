@echo off
echo.
echo ========================================
echo   Horror Oracle - Google Auth Fix
echo ========================================
echo.
echo This script will help you fix Google authentication.
echo.
echo STEP 1: Opening Google Cloud Console...
echo.
start https://console.cloud.google.com/apis/credentials/consent
echo.
echo INSTRUCTIONS:
echo.
echo 1. In the browser window that just opened:
echo    - Look for "Publishing status"
echo    - If it says "Testing", scroll down to "Test users"
echo    - Click "+ ADD USERS"
echo    - Enter YOUR email address (the one you want to sign in with)
echo    - Click SAVE
echo.
echo 2. WAIT 3-5 MINUTES for changes to take effect
echo.
echo 3. Then come back and press any key to continue...
pause
echo.
echo ========================================
echo   Starting Flask Server
echo ========================================
echo.
echo Server will start on http://localhost:5000
echo.
echo To test Google authentication:
echo 1. Open: http://localhost:5000/test-google-auth-detailed.html
echo 2. Click the Google Sign-In button
echo 3. Check the diagnostic results
echo.
echo Press Ctrl+C to stop the server
echo.
python horror.py

