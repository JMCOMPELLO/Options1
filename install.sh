#!/bin/bash
# Installation script for Advanced Options Backtest Platform

echo "========================================="
echo "Options Backtest Platform Installer"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Install requirements
echo ""
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "✗ Failed to install dependencies"
    exit 1
fi

# Check for .env file
echo ""
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.template .env
    echo "⚠️  Please edit .env and add your Massive API key"
    echo ""
    echo "Get your API key from: https://polygon.io/"
    echo "Then edit .env file and replace 'your_api_key_here' with your actual key"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "========================================="
echo "Installation Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Massive API key (if not done)"
echo "2. Run: python3 options_backtest_app.py"
echo "3. See QUICKSTART.md for usage guide"
echo ""
echo "Happy backtesting!"
