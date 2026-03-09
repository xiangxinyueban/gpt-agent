#!/usr/bin/env python3
"""
视觉自动化工作流测试
测试从登录到聊天的完整流程
"""
import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_task_integration():
    """测试所有任务模块集成"""
    print("🧪 测试任务模块集成...")
    
    modules = [
        ('visual_automation.tasks.base_task', 'BaseTask'),
        ('visual_automation.tasks.browser_navigation_task', 'BrowserNavigationTask'),
        ('visual_automation.tasks.login_task', 'LoginTask'),
        ('visual_automation.tasks.login_task', 'ChatGPTLoginTask'),
        ('visual_automation.tasks.chat_task', 'ChatTask'),
    ]
    
    all_ok = True
    for module_path, class_name in modules:
        try:
            exec(f"from {module_path} import {class_name}")
            print(f"  ✅ {module_path}.{class_name}")
        except ImportError as e:
            print(f"  ❌ {module_path}: {e}")
            all_ok = False
        except Exception as e:
            print(f"  ⚠️  {module_path}: {e}")
            all_ok = False
    
    return all_ok

def test_task_initialization():
    """测试任务初始化"""
    print("\n🧪 测试任务初始化...")
    
    try:
        from visual_automation.tasks.base_task import BaseTask
        from visual_automation.tasks.browser_navigation_task import BrowserNavigationTask
        from visual_automation.tasks.login_task import LoginTask, ChatGPTLoginTask
        from visual_automation.tasks.chat_task import ChatTask
        
        # 测试基础任务（抽象类，不能直接实例化）
        print("  BaseTask: 抽象类 ✓")
        
        # 测试浏览器导航任务
        nav_task = BrowserNavigationTask(
            url="https://chat.openai.com",
            template_dir="visual_automation/config/templates/chatgpt/",
            save_screenshots=False
        )
        print(f"  BrowserNavigationTask: ✓ (目标: {nav_task.url})")
        
        # 测试登录任务
        login_task = LoginTask(
            username="test@example.com",
            password="testpassword",
            website="chatgpt",
            template_dir="visual_automation/config/templates/chatgpt/",
            save_screenshots=False
        )
        print(f"  LoginTask: ✓ (用户: {login_task.username})")
        
        # 测试ChatGPT专用登录任务
        chatgpt_login = ChatGPTLoginTask(
            username="test@example.com",
            password="testpassword",
            template_dir="visual_automation/config/templates/chatgpt/",
            save_screenshots=False
        )
        print(f"  ChatGPTLoginTask: ✓")
        
        # 测试聊天任务
        chat_task = ChatTask(
            message="Hello ChatGPT!",
            wait_for_response=True,
            response_timeout=30.0,
            template_dir="visual_automation/config/templates/chatgpt/",
            save_screenshots=False
        )
        print(f"  ChatTask: ✓ (消息: '{chat_task.message[:30]}...')")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 任务初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_template_directories():
    """检查模板目录"""
    print("\n📁 检查模板目录...")
    
    template_dirs = [
        "visual_automation/config/templates/chatgpt",
        "visual_automation/config/templates/cloudflare",
        "visual_automation/config/templates/common"
    ]
    
    all_exist = True
    for dir_path in template_dirs:
        if os.path.exists(dir_path):
            # 检查是否有PNG文件
            png_files = [f for f in os.listdir(dir_path) if f.lower().endswith('.png')] if os.path.exists(dir_path) else []
            if png_files:
                print(f"  ✅ {dir_path} ({len(png_files)} 个模板)")
            else:
                print(f"  ⚠️  {dir_path} (目录存在但为空)")
                all_exist = False
        else:
            print(f"  ❌ {dir_path} (不存在)")
            all_exist = False
    
    return all_exist

def check_screen_access():
    """检查屏幕访问"""
    print("\n🖥️  检查屏幕访问...")
    
    try:
        import pyautogui
        
        # 获取屏幕尺寸
        width, height = pyautogui.size()
        print(f"  屏幕尺寸: {width}x{height}")
        
        # 尝试截屏
        try:
            screenshot = pyautogui.screenshot()
            print(f"  截屏成功: {screenshot.size}")
            
            # 检查图像内容
            import numpy as np
            from PIL import Image
            img_array = np.array(screenshot)
            gray = np.mean(img_array, axis=2)
            
            mean_brightness = np.mean(gray)
            std_brightness = np.std(gray)
            
            print(f"  平均亮度: {mean_brightness:.1f}")
            print(f"  亮度标准差: {std_brightness:.1f}")
            
            if std_brightness < 10:
                print("  ⚠️  屏幕可能为黑屏/休眠")
                return False
            else:
                print("  ✅ 屏幕正常显示内容")
                return True
                
        except Exception as e:
            print(f"  ❌ 截屏失败: {e}")
            return False
            
    except ImportError:
        print("  ❌ 无法导入pyautogui")
        return False
    except Exception as e:
        print(f"  ❌ 屏幕检查失败: {e}")
        return False

def generate_template_checklist():
    """生成模板采集清单"""
    print("\n📋 ChatGPT模板采集清单:")
    print("=" * 50)
    
    templates = {
        "登录相关": [
            "login_button.png - 登录按钮",
            "username_field.png - 用户名输入框",
            "password_field.png - 密码输入框",
            "submit_button.png - 提交按钮",
            "human_verification.png - 人机验证复选框"
        ],
        "聊天界面": [
            "chat_input.png - 聊天输入框",
            "send_button.png - 发送按钮",
            "user_avatar.png - 用户头像（登录标识）",
            "new_chat_button.png - 新聊天按钮",
            "chat_history.png - 聊天历史区域"
        ],
        "响应指示": [
            "typing_indicator.png - 正在输入指示器",
            "ai_message.png - AI消息气泡",
            "user_message.png - 用户消息气泡"
        ],
        "错误处理": [
            "error_message.png - 错误消息",
            "rate_limit.png - 频率限制提示",
            "network_error.png - 网络错误"
        ]
    }
    
    for category, items in templates.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  - {item}")
    
    print("\n💡 采集命令:")
    print("  cd /home/liang/.openclaw/workspace/gpt-agent")
    print("  source venv/bin/activate")
    print("  python scripts/capture_template.py --interactive")

def provide_wakeup_guide():
    """提供显示器唤醒指南"""
    print("\n🔧 显示器唤醒指南:")
    print("=" * 50)
    print("如果屏幕为黑屏/休眠状态，请尝试以下方法:")
    print()
    print("1. 物理唤醒:")
    print("   - 移动鼠标或触摸板")
    print("   - 按下键盘任意键")
    print("   - 按电源按钮（短暂按下）")
    print()
    print("2. 命令行唤醒:")
    print("   # 禁用屏幕保护")
    print("   xset s off")
    print("   # 禁用DPMS（显示器电源管理）")
    print("   xset -dpms")
    print("   # 强制唤醒显示器")
    print("   xset dpms force on")
    print()
    print("3. 检查Firefox:")
    print("   # 确保Firefox在前台运行")
    print("   # 访问 https://chat.openai.com")
    print("   # 完成登录和人机验证")
    print()
    print("4. 检查显示设置:")
    print("   # 查看当前显示器状态")
    print("   xrandr --query")
    print("   # 如果有多个显示器，确保正确配置")

def main():
    """主测试函数"""
    print("=" * 60)
    print("🤖 视觉自动化工作流测试")
    print("=" * 60)
    
    # 测试1: 任务模块集成
    integration_ok = test_task_integration()
    
    # 测试2: 任务初始化
    init_ok = test_task_initialization()
    
    # 测试3: 模板目录检查
    templates_exist = check_template_directories()
    
    # 测试4: 屏幕访问检查
    screen_ok = check_screen_access()
    
    # 输出总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    
    results = [
        ("任务模块集成", integration_ok),
        ("任务初始化", init_ok),
        ("模板目录检查", templates_exist),
        ("屏幕访问", screen_ok)
    ]
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    # 提供下一步指导
    print("\n" + "=" * 60)
    if all_passed and screen_ok and templates_exist:
        print("✨ 所有测试通过！可以开始模板采集和自动化测试。")
        generate_template_checklist()
    elif not screen_ok:
        print("⚠️  屏幕访问失败，可能为黑屏/休眠状态。")
        provide_wakeup_guide()
        print("\n💡 建议: 先唤醒显示器并打开ChatGPT，然后采集模板。")
    elif not templates_exist:
        print("⚠️  模板目录为空，需要采集UI模板。")
        generate_template_checklist()
        print("\n💡 建议: 使用采集工具创建ChatGPT界面模板。")
    else:
        print("⚠️  部分测试失败，需要修复。")
    
    # 提供完整的操作流程
    print("\n" + "=" * 60)
    print("🚀 完整操作流程:")
    print("=" * 60)
    print("1. 唤醒显示器并确保可见")
    print("2. 打开Firefox，访问 https://chat.openai.com")
    print("3. 完成登录（包括人机验证）")
    print("4. 采集ChatGPT界面模板:")
    print("   cd /home/liang/.openclaw/workspace/gpt-agent")
    print("   source venv/bin/activate")
    print("   python scripts/capture_template.py --interactive")
    print("5. 测试模板识别:")
    print("   python scripts/test_template.py --interactive")
    print("6. 运行视觉自动化测试:")
    print("   # 创建测试脚本使用ChatTask")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())