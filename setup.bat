@echo off
REM Setup script for AI Employee Bronze Tier (Windows)
REM Initializes the vault and installs dependencies

setlocal enabledelayedexpansion

echo.
echo ==========================================
echo AI Employee - Bronze Tier Setup (Windows)
echo ==========================================
echo.

REM Check Python version
echo Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.13+
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python version: %PYTHON_VERSION%

REM Install dependencies
echo.
echo Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed

REM Create drop folder
echo.
echo Creating drop folder...
if not exist "%USERPROFILE%\AI_Employee_Drop" (
    mkdir "%USERPROFILE%\AI_Employee_Drop"
)
echo [OK] Drop folder created at %USERPROFILE%\AI_Employee_Drop

REM Verify vault structure
echo.
echo Verifying vault structure...
setlocal enabledelayedexpansion

set "folders[0]=AI_Employee_Vault"
set "folders[1]=AI_Employee_Vault\Inbox"
set "folders[2]=AI_Employee_Vault\Needs_Action"
set "folders[3]=AI_Employee_Vault\Plans"
set "folders[4]=AI_Employee_Vault\Pending_Approval"
set "folders[5]=AI_Employee_Vault\Approved"
set "folders[6]=AI_Employee_Vault\Rejected"
set "folders[7]=AI_Employee_Vault\Done"
set "folders[8]=AI_Employee_Vault\Accounting"
set "folders[9]=AI_Employee_Vault\Logs"

for /l %%i in (0,1,9) do (
    if exist "!folders[%%i]!" (
        echo [OK] !folders[%%i]!
    ) else (
        echo [MISSING] !folders[%%i]!
    )
)

REM Verify core files
echo.
echo Verifying core files...

set "files[0]=AI_Employee_Vault\Dashboard.md"
set "files[1]=AI_Employee_Vault\Company_Handbook.md"
set "files[2]=filesystem_watcher.py"
set "files[3]=claude_integration.py"
set "files[4]=README.md"

for /l %%i in (0,1,4) do (
    if exist "!files[%%i]!" (
        echo [OK] !files[%%i]!
    ) else (
        echo [MISSING] !files[%%i]!
    )
)

REM Test Claude integration
echo.
echo Testing Claude integration...
python claude_integration.py >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Claude integration test failed
) else (
    echo [OK] Claude integration working
)

REM Summary
echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Open Obsidian and add vault: AI_Employee_Vault
echo 2. Start the watcher: python filesystem_watcher.py
echo 3. Drop a file in: %USERPROFILE%\AI_Employee_Drop\
echo 4. Process tasks: claude /process-vault-tasks
echo.
echo Documentation: README.md
echo Rules: AI_Employee_Vault\Company_Handbook.md
echo Status: AI_Employee_Vault\Dashboard.md
echo.
pause
