#!/bin/bash
# Quick setup script for visual automation on MacBook

set -e  # Exit on error

echo "🚀 MacBook Visual Automation Setup"
echo "=================================="

# Check Python
echo "🔍 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+ from python.org"
    exit 1
fi

python_version=$(python3 --version | awk '{print $2}')
echo "✅ Python $python_version found"

# Clone repository if not already cloned
if [ ! -d "gpt-agent" ]; then
    echo "📥 Cloning repository..."
    git clone https://github.com/xiangxinyueban/gpt-agent.git
    cd gpt-agent
else
    echo "📁 Repository already exists"
    cd gpt-agent
    echo "🔄 Pulling latest changes..."
    git pull
fi

# Create virtual environment
echo "🐍 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements-visual.txt

# Additional Mac-specific dependencies
echo "🍎 Installing Mac-specific dependencies..."
pip install pyobjc-core pyobjc-framework-Quartz mss

# Test screenshot functionality
echo "🖥️  Testing screenshot functionality..."
python3 -c "
import pyautogui
try:
    width, height = pyautogui.size()
    print(f'✅ Screen resolution: {width}x{height}')
    screenshot = pyautogui.screenshot()
    print(f'✅ Screenshot test successful: {screenshot.size}')
except Exception as e:
    print(f'❌ Screenshot test failed: {e}')
    print('💡 You may need to grant Screen Recording permission to Terminal')
    print('   System Preferences → Security & Privacy → Privacy → Screen Recording')
"

echo ""
echo "=================================="
echo "✅ Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Grant Screen Recording permission to Terminal if needed"
echo "2. Open ChatGPT in browser and login"
echo "3. Capture UI templates:"
echo "   python scripts/capture_template.py --interactive"
echo "4. Test templates:"
echo "   python scripts/test_template.py --interactive"
echo ""
echo "📚 Detailed guide: VISUAL_AUTOMATION_SETUP.md"