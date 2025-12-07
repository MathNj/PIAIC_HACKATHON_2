@echo off
REM Test runner script for TODO API Backend (Windows)
REM
REM Usage:
REM   run_tests.bat              Run all tests
REM   run_tests.bat auth         Run only auth tests
REM   run_tests.bat tasks        Run only task tests
REM   run_tests.bat --cov        With coverage report

echo ================================
echo   TODO API Test Suite
echo ================================
echo.

REM Navigate to backend directory
cd /d %~dp0

REM Check if pytest is installed
python -m pytest --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pytest not found. Installing test dependencies...
    pip install -q pytest pytest-asyncio httpx
)

REM Parse arguments
set PYTEST_ARGS=-v
set RUN_COV=false

:parse_args
if "%1"=="" goto run_tests
if "%1"=="--cov" set RUN_COV=true
if "%1"=="--coverage" set RUN_COV=true
if "%1"=="auth" set PYTEST_ARGS=%PYTEST_ARGS% -m auth
if "%1"=="tasks" set PYTEST_ARGS=%PYTEST_ARGS% -m tasks
if "%1"=="integration" set PYTEST_ARGS=%PYTEST_ARGS% -m integration
if "%1"=="-v" set PYTEST_ARGS=%PYTEST_ARGS% -vv
if "%1"=="--verbose" set PYTEST_ARGS=%PYTEST_ARGS% -vv
shift
goto parse_args

:run_tests
REM Add coverage if requested
if "%RUN_COV%"=="true" (
    echo Installing coverage tools...
    pip install -q pytest-cov
    set PYTEST_ARGS=%PYTEST_ARGS% --cov=app --cov-report=html --cov-report=term
)

REM Run tests
echo Running tests...
echo.

python -m pytest %PYTEST_ARGS%

REM Show results
echo.
if %errorlevel% equ 0 (
    echo ================================
    echo   All tests passed!
    echo ================================
    if "%RUN_COV%"=="true" (
        echo.
        echo Coverage report generated at: htmlcov\index.html
    )
) else (
    echo ================================
    echo   Some tests failed
    echo ================================
    exit /b 1
)
