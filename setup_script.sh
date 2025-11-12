#!/bin/bash
# Automatic installation script for Todoist AI Summary

set -e  # Stop on error

echo "=========================================="
echo "📊 Todoist AI Summary - Installation"
echo "=========================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Install Python 3 with: sudo apt-get install python3 python3-pip python3-venv"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python $PYTHON_VERSION detected"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
if [ ! -d "venv-summary" ]; then
    python3 -m venv venv-summary
    echo "✓ Virtual environment created"
else
    echo "⚠ Virtual environment already exists"
fi

# Activate environment
source venv-summary/bin/activate

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Create directory structure
echo ""
echo "📁 Creating directory structure..."
mkdir -p data/summaries
mkdir -p logs
mkdir -p src
echo "✓ Directories created"

# Create __init__.py file if it doesn't exist
if [ ! -f "src/__init__.py" ]; then
    touch src/__init__.py
    echo "✓ src/__init__.py created"
fi

# Copy .env.example if .env doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✓ .env file created from .env.example"
        echo ""
        echo "⚠️  IMPORTANT: Edit the .env file with your API keys!"
        echo "   nano .env"
    else
        echo "⚠ .env.example not found"
    fi
else
    echo "⚠ .env file already exists (not modified)"
fi

# Test installation
echo ""
echo "🧪 Testing installation..."
python3 -c "import requests, openai, dotenv; print('✓ Modules imported successfully')" || {
    echo "❌ Error importing modules"
    exit 1
}

echo ""
echo "=========================================="
echo "✅ Installation complete!"
echo "=========================================="
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Configure your API keys in .env:"
echo "   nano .env"
echo ""
echo "2. Get your Todoist token:"
echo "   https://todoist.com/app/settings/integrations/developer"
echo ""
echo "3. Get your OpenAI key:"
echo "   https://platform.openai.com/api-keys"
echo ""
echo "4. Configure a Gmail app password:"
echo "   https://myaccount.google.com/apppasswords"
echo ""
echo "5. Test the script:"
echo "   source venv-summary/bin/activate"
echo "   python main.py"
echo ""
echo "6. Configure cron for automatic execution (see README.md)"
echo ""
echo "🚀 Happy summarizing!"