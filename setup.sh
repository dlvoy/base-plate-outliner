#!/bin/bash
# Setup script for irregular baseplate generator
# This script creates a virtual environment and installs dependencies

echo "========================================="
echo "Irregular Baseplate Generator Setup"
echo "========================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "Error: Git is not installed or not in PATH"
    echo "Please install Git and try again"
    exit 1
fi

# Check and initialize git submodules
echo "Checking MachineBlocks submodule..."
if [ ! -f "machineblocks/lib/block.scad" ]; then
    echo "MachineBlocks submodule not found. Initializing..."
    git submodule update --init --recursive

    if [ $? -ne 0 ]; then
        echo "Error: Failed to initialize git submodules"
        echo "Please run: git submodule update --init --recursive"
        exit 1
    fi
    echo "MachineBlocks submodule initialized successfully"
else
    echo "MachineBlocks submodule already initialized"
fi
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3 and try again"
    exit 1
fi

echo "Python 3 found: $(python3 --version)"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv

if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment"
    echo "Make sure python3-venv is installed"
    echo "On Ubuntu/Debian: sudo apt install python3-venv"
    exit 1
fi

echo "Virtual environment created successfully"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment"
    exit 1
fi

echo "Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo ""
echo "========================================="
echo "Setup completed successfully!"
echo "========================================="
echo ""
echo "To use the script:"
echo "  1. Activate the virtual environment:"
echo "     source .venv/bin/activate"
echo ""
echo "  2. Run the script:"
echo "     python3 generate_irregular_baseplate.py image.png"
echo ""
echo "  3. When done, deactivate the environment:"
echo "     deactivate"
echo ""
echo "Virtual environment is currently activated."
echo "You can start using the script right away!"
echo ""
