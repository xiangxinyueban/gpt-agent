#!/usr/bin/env python3
"""
快速集成测试，验证视觉自动化模块能正常工作。
此测试不执行实际自动化操作，只测试模块初始化。
"""
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_module_imports():
    """测试所有模块能否导入"""
    print("🧪 测试模块导入...")
    
    modules = [
        ('visual_automation.core.screen_capturer', 'ScreenCapturer'),
        ('visual_automation.core.image_locator', 'ImageLocator'),
        ('visual_automation.core.input_simulator', 'HumanizedInputSimulator'),
        ('visual_automation.core.workflow_executor', 'WorkflowExecutor'),
        ('visual_automation.tasks.base_task', 'BaseTask'),
        ('visual_automation.tasks.browser_navigation_task', 'BrowserNavigationTask'),
        ('visual_automation.tasks.login_task', 'LoginTask'),
        ('visual_automation.tasks.login_task', 'ChatGPTLoginTask'),
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

def test_module_initialization():
    """测试模块初始化"""
    print("\n🧪 测试模块初始化...")
    
    try:
        from visual_automation.core.screen_capturer import ScreenCapturer
        capturer = ScreenCapturer()
        print(f"  ✅ ScreenCapturer: {capturer.screen_width}x{capturer.screen_height}")
        
        from visual_automation.core.image_locator import ImageLocator
        locator = ImageLocator(template_dir="visual_automation/config/templates/chatgpt/")
        print(f"  ✅ ImageLocator: confidence_threshold={locator.confidence_threshold}")
        
        from visual_automation.core.input_simulator import HumanizedInputSimulator
        simulator = HumanizedInputSimulator()
        print(f"  ✅ HumanizedInputSimulator initialized")
        
        from visual_automation.tasks.base_task import BaseTask
        print(f"  ✅ BaseTask class accessible")
        
        return True
    except Exception as e:
        print(f"  ❌ Module initialization failed: {e}")
        return False

def test_workflow_executor():
    """测试工作流执行器"""
    print("\n🧪 测试工作流执行器...")
    
    try:
        from visual_automation.core.workflow_executor import WorkflowExecutor
        
        # 使用空的模板目录进行测试
        executor = WorkflowExecutor(
            template_dir="visual_automation/config/templates/empty_test/",
            save_screenshots=False
        )
        
        print(f"  ✅ WorkflowExecutor initialized")
        
        # 添加一个简单的测试步骤
        def test_step(exec):
            print("    Test step executed")
            return {"test": "success"}
        
        executor.create_step(
            name="test_step",
            description="Test step",
            action=test_step
        )
        
        print(f"  ✅ Test step added")
        
        return True
    except Exception as e:
        print(f"  ❌ WorkflowExecutor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("视觉自动化系统 - 集成测试")
    print("=" * 60)
    
    # 测试1: 模块导入
    imports_ok = test_module_imports()
    
    # 测试2: 模块初始化
    init_ok = test_module_initialization()
    
    # 测试3: 工作流执行器
    workflow_ok = test_workflow_executor()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    results = [
        ("模块导入", imports_ok),
        ("模块初始化", init_ok),
        ("工作流执行器", workflow_ok)
    ]
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✨ 所有测试通过！视觉自动化系统准备就绪。")
        print("下一步：采集UI模板并开发ChatGPT专用任务。")
        return 0
    else:
        print("⚠️  部分测试失败，需要修复。")
        return 1

if __name__ == "__main__":
    sys.exit(main())