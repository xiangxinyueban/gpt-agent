#!/usr/bin/env python3
"""
Check visual automation dependencies.
"""
import sys

def check_dependencies():
    """Check if all required dependencies are installed."""
    required = [
        ('pyautogui', 'pyautogui'),
        ('cv2', 'opencv-python'),
        ('PIL', 'Pillow'),
        ('pynput', 'pynput'),
        ('numpy', 'numpy')
    ]
    
    missing = []
    available = []
    
    print("🔍 Checking visual automation dependencies...")
    
    for import_name, package_name in required:
        try:
            __import__(import_name)
            available.append(package_name)
            print(f"  ✅ {package_name} ({import_name})")
        except ImportError:
            missing.append(package_name)
            print(f"  ❌ {package_name} ({import_name})")
    
    print(f"\n📊 Summary: {len(available)}/{len(required)} dependencies available")
    
    if missing:
        print(f"\n⚠️  Missing dependencies:")
        for package in missing:
            print(f"  - {package}")
        
        print(f"\n💡 Install missing dependencies with:")
        print(f"  pip install {' '.join(missing)}")
        print(f"\n  Or install all visual dependencies:")
        print(f"  pip install -r requirements-visual.txt")
        return False
    else:
        print("\n🎉 All visual automation dependencies are available!")
        return True

def check_template_directories():
    """Check if template directories exist."""
    import os
    
    print("\n📁 Checking template directories...")
    
    template_dirs = [
        "visual_automation/config/templates/chatgpt",
        "visual_automation/config/templates/cloudflare", 
        "visual_automation/config/templates/common"
    ]
    
    all_exist = True
    for dir_path in template_dirs:
        if os.path.exists(dir_path):
            # Check if directory has image files
            image_files = [f for f in os.listdir(dir_path) 
                          if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))] if os.path.exists(dir_path) else []
            
            if image_files:
                print(f"  ✅ {dir_path} ({len(image_files)} templates)")
            else:
                print(f"  ⚠️  {dir_path} (exists but empty)")
                all_exist = False
        else:
            print(f"  ❌ {dir_path} (does not exist)")
            all_exist = False
    
    if not all_exist:
        print("\n💡 Template directories are missing or empty.")
        print("   Run the template capture script to create templates.")
    
    return all_exist

if __name__ == "__main__":
    deps_ok = check_dependencies()
    dirs_ok = check_template_directories()
    
    if deps_ok and dirs_ok:
        print("\n✨ Visual automation system is ready!")
        sys.exit(0)
    else:
        print("\n⚠️  Visual automation system needs setup.")
        sys.exit(1)