@echo off
REM Run the Official 127-bit Geofac Challenge (Windows)
REM
REM This script runs the 127-bit factorization challenge with optimized
REM shell-exclusion pruning configuration.
REM
REM Expected runtime on 64-core AMD EPYC 7J13: 4.8-6.2 minutes
REM (Previous best without shell pruning: ~19 minutes)

echo ========================================
echo   127-bit Geofac Challenge Runner
echo   Shell-Exclusion Pruning Enabled
echo ========================================
echo.

REM Check Python installation
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] python not found. Please install Python 3.8+
    exit /b 1
)

REM Check Python version
python --version 2>&1 | findstr /R "Python 3\.[89]" >nul 2>nul
if %ERRORLEVEL% EQU 0 goto :version_ok

python --version 2>&1 | findstr /R "Python 3\.1[0-9]" >nul 2>nul
if %ERRORLEVEL% EQU 0 goto :version_ok

echo [WARNING] Python 3.8+ required
python --version
exit /b 1

:version_ok
echo [OK] Python version check passed

REM Check if dependencies are installed
python -c "import numpy" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Installing dependencies...
    pip install -e .
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to install dependencies
        exit /b 1
    )
)

echo [OK] Dependencies installed
echo.

REM Run the challenge
echo Starting 127-bit challenge...
echo.

python cli\challenge_127.py %*

set EXIT_CODE=%ERRORLEVEL%

echo.
if %EXIT_CODE% EQU 0 (
    echo ========================================
    echo   Challenge completed successfully!
    echo ========================================
) else (
    echo ========================================
    echo   Challenge failed or interrupted
    echo   Exit code: %EXIT_CODE%
    echo ========================================
)

exit /b %EXIT_CODE%
