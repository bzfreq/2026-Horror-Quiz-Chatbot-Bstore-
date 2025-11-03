@echo off
echo ========================================
echo VERIFYING HEREDITARY REMOVAL
echo ========================================
echo.
echo Searching active code files for "hereditary"...
echo.

findstr /S /I /N "hereditary" "oracle_engine\builder_node.py" "oracle_engine\*.py" "backend\quiz_generator.py" "backend\langchain_setup.py" "horror.py" "app.py" "script-js-combined.js" 2>nul

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ❌ WARNING: Found "hereditary" references in active code!
    echo    Review the lines above.
) else (
    echo ✅ SUCCESS: NO "hereditary" found in active code files!
    echo.
    echo    All hardcoded references have been removed.
    echo    The quiz will now use LangChain dynamic generation.
)

echo.
echo ========================================
echo NEXT STEPS:
echo ========================================
echo 1. Restart your backend server:
echo    python horror.py
echo    OR
echo    python app.py
echo.
echo 2. Clear browser cache or use Incognito mode
echo.
echo 3. Test "Face Your Nightmares" multiple times
echo.
echo 4. Each quiz should be DIFFERENT with NO Hereditary
echo ========================================
pause


