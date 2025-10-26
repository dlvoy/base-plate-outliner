@echo off
REM Setup script for irregular baseplate generator (Windows)
REM This script creates a virtual environment and installs dependencies

echo =========================================
echo Irregular Baseplate Generator Setup
echo =========================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Git is not installed or not in PATH
    echo Please install Git and try again
    pause
    exit /b 1
)

REM Check and initialize git submodules
echo Checking MachineBlocks submodule...
if not exist "machineblocks\lib\block.scad" (
    echo MachineBlocks submodule not found. Initializing...
    git submodule update --init --recursive

    if %errorlevel% neq 0 (
        echo Error: Failed to initialize git submodules
        echo Please run: git submodule update --init --recursive
        pause
        exit /b 1
    )
    echo MachineBlocks submodule initialized successfully
) else (
    echo MachineBlocks submodule already initialized
)
echo.

REM Check if Python 3 is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3 and try again
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv .venv

if %errorlevel% neq 0 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)

echo Virtual environment created successfully
echo.

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

if %errorlevel% neq 0 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

echo Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo.
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo =========================================
echo Setup completed successfully!
echo =========================================
echo.
echo To use the script:
echo   1. Activate the virtual environment:
echo      .venv\Scripts\activate
echo.
echo   2. Run the script:
echo      python generate_irregular_baseplate.py image.png
echo.
echo   3. When done, deactivate the environment:
echo      deactivate
echo.
echo Virtual environment is currently activated.
echo You can start using the script right away!
echo.
pause
