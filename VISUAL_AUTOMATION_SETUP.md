# Visual Automation Setup Guide for MacBook

## 📋 Prerequisites

### 1. Python Environment
```bash
# Check Python version (requires 3.8+)
python3 --version

# Install pip if not available
python3 -m ensurepip --upgrade
```

### 2. Clone Repository
```bash
git clone https://github.com/xiangxinyueban/gpt-agent.git
cd gpt-agent
```

### 3. Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate on MacBook
source venv/bin/activate

# Or using fish shell
source venv/bin/activate.fish

# Or using csh/tcsh
source venv/bin/activate.csh
```

## 📦 Install Dependencies

### Install Visual Automation Dependencies
```bash
pip install -r requirements-visual.txt
```

### Install Screenshot Tools (Mac specific)
```bash
# Install Python dependencies for screenshots
pip install pyobjc-core pyobjc-framework-Quartz

# For better screenshot quality
pip install mss
```

## 🖥️ Setup for MacOS Screenshots

### Permissions Required
MacOS requires screen recording permission for screenshots:

1. **Open System Preferences** → **Security & Privacy** → **Privacy**
2. Select **Screen Recording** from the left sidebar
3. Click the lock icon to make changes (enter password)
4. Check the box next to **Terminal** (or your IDE/terminal app)
5. Restart Terminal after granting permission

### Test Screenshot Functionality
```bash
python3 -c "
import pyautogui
import cv2
import numpy as np
from PIL import Image

# Test screenshot
screenshot = pyautogui.screenshot()
print(f'Screenshot size: {screenshot.size}')

# Save test image
screenshot.save('test_mac_screenshot.png')
print('✅ Screenshot test successful!')
"
```

## 🚀 Quick Start Guide

### 1. Prepare ChatGPT Interface
1. Open **Safari** or **Chrome** browser
2. Navigate to **https://chat.openai.com**
3. Complete login (including human verification if needed)
4. Keep ChatGPT chat interface visible

### 2. Capture UI Templates
```bash
# Run interactive template capture tool
python scripts/capture_template.py --interactive
```

**Recommended Templates to Capture:**
1. `login_button.png` - Login button
2. `chat_input.png` - Chat input field
3. `send_button.png` - Send button
4. `user_avatar.png` - User avatar (logged-in indicator)

**Template Storage:**
- Templates are saved to `visual_automation/config/templates/chatgpt/`
- Create subdirectories as needed: `chatgpt/`, `common/`, etc.

### 3. Test Template Recognition
```bash
# Test a single template
python scripts/test_template.py --template visual_automation/config/templates/chatgpt/login_button.png

# Batch test all templates
python scripts/test_template.py --dir visual_automation/config/templates/chatgpt/

# Interactive testing
python scripts/test_template.py --interactive
```

### 4. Optimize Templates
```bash
# Process a single template
python scripts/process_template.py --input visual_automation/config/templates/chatgpt/login_button.png --operations resize,contrast,sharpen

# Batch process all templates
python scripts/process_template.py --input visual_automation/config/templates/chatgpt/ --batch --operations resize,contrast,sharpen
```

## 🧪 Test Visual Automation Workflow

### Run Integration Tests
```bash
# Test module imports and initialization
python test_visual_integration.py

# Test complete visual workflow
python test_visual_workflow.py
```

### Test ChatGPT Chat Task
```bash
python3 -c "
from visual_automation.tasks.chat_task import ChatTask

# Initialize chat task
task = ChatTask(
    message='Hello ChatGPT from MacBook!',
    template_dir='visual_automation/config/templates/chatgpt/',
    save_screenshots=True
)

print(f'✅ ChatTask initialized: {task.message}')
print('Note: Actual execution requires UI templates')
"
```

## 🔧 Troubleshooting

### Common Issues on MacOS

#### 1. Screenshot Permission Error
**Error**: `PyAutoGUI cannot take screenshots on macOS.`
**Solution**: 
- Grant Screen Recording permission to Terminal
- Restart Terminal after granting permission
- Test with: `python3 -c "import pyautogui; print(pyautogui.size())"`

#### 2. OpenCV Import Error
**Error**: `ImportError: No module named cv2`
**Solution**:
```bash
# Install OpenCV
pip install opencv-python

# Or if using Homebrew
brew install opencv
pip install opencv-python
```

#### 3. Missing Dependencies
**Error**: Various import errors
**Solution**:
```bash
# Install all dependencies
pip install -r requirements.txt
pip install -r requirements-visual.txt
```

#### 4. Template Not Found
**Error**: `FileNotFoundError` when testing templates
**Solution**:
- Ensure templates are captured first
- Check template directory path
- Use absolute paths if needed

## 📁 Project Structure

```
gpt-agent/
├── scripts/                    # Template management tools
│   ├── capture_template.py     # Capture UI elements
│   ├── process_template.py     # Optimize templates
│   └── test_template.py        # Test template recognition
├── visual_automation/          # Core visual automation
│   ├── core/                   # Core modules
│   │   ├── screen_capturer.py  # Screen capture
│   │   ├── image_locator.py    # Image recognition
│   │   ├── input_simulator.py  # Mouse/keyboard input
│   │   └── workflow_executor.py # Workflow management
│   └── tasks/                  # Specific tasks
│       ├── base_task.py        # Base task class
│       ├── browser_navigation_task.py
│       ├── login_task.py       # Login task
│       ├── chat_task.py        # ChatGPT chat task
│       └── __pycache__/
├── config/                     # Configuration
│   └── templates/              # UI template storage
│       ├── chatgpt/            # ChatGPT templates
│       ├── common/             # Common UI elements
│       └── cloudflare/         # Cloudflare verification
├── tests/                      # Tests
└── requirements-visual.txt     # Visual automation dependencies
```

## 🎯 Next Steps

1. **Capture Templates**: Use the interactive tool to capture ChatGPT UI elements
2. **Test Recognition**: Verify templates can be accurately recognized
3. **Run Integration Tests**: Test the complete visual workflow
4. **Integrate with Main Agent**: Combine visual automation with existing GPT agent

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section
2. Verify all permissions are granted
3. Ensure dependencies are installed
4. Test with the provided test scripts

**Note**: The visual automation system is designed to work alongside the existing DOM-based automation. It provides an alternative approach for handling Cloudflare and human verification challenges.