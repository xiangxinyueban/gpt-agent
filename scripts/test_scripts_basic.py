#!/usr/bin/env python3
"""
模板采集脚本基本测试
验证脚本能否导入和初始化，不执行实际操作
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """测试脚本导入"""
    print("🧪 测试脚本导入...")
    
    scripts = [
        ('capture_template', 'TemplateCaptureTool'),
        ('process_template', 'TemplateProcessor'),
        ('test_template', 'TemplateTester'),
    ]
    
    all_ok = True
    for script_name, class_name in scripts:
        try:
            module = __import__(f'scripts.{script_name}', fromlist=[class_name])
            if hasattr(module, class_name):
                print(f"  ✅ {script_name}.py: {class_name}")
            else:
                print(f"  ❌ {script_name}.py: 找不到类 {class_name}")
                all_ok = False
        except ImportError as e:
            print(f"  ❌ {script_name}.py: {e}")
            all_ok = False
        except Exception as e:
            print(f"  ⚠️  {script_name}.py: {e}")
            all_ok = False
    
    return all_ok

def test_capture_template():
    """测试capture_template.py"""
    print("\n🧪 测试capture_template.py...")
    
    try:
        from scripts.capture_template import TemplateCaptureTool
        
        # 测试初始化（不实际截图）
        tool = TemplateCaptureTool(template_dir="test_tmp/")
        print(f"  ✅ TemplateCaptureTool 初始化成功")
        print(f"     屏幕: {tool.screen_width}x{tool.screen_height}")
        print(f"     目录: {tool.template_dir}")
        
        # 清理测试目录
        import shutil
        if os.path.exists("test_tmp"):
            shutil.rmtree("test_tmp")
            
        return True
    except Exception as e:
        print(f"  ❌ capture_template 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_process_template():
    """测试process_template.py"""
    print("\n🧪 测试process_template.py...")
    
    try:
        from scripts.process_template import TemplateProcessor
        
        # 测试初始化
        processor = TemplateProcessor()
        print(f"  ✅ TemplateProcessor 初始化成功")
        
        return True
    except Exception as e:
        print(f"  ❌ process_template 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_test_template():
    """测试test_template.py"""
    print("\n🧪 测试test_template.py...")
    
    try:
        from scripts.test_template import TemplateTester
        
        # 测试初始化
        tester = TemplateTester(template_dir="test_tmp/")
        print(f"  ✅ TemplateTester 初始化成功")
        print(f"     屏幕: {tester.screen_width}x{tester.screen_height}")
        
        # 清理测试目录
        import shutil
        if os.path.exists("test_tmp"):
            shutil.rmtree("test_tmp")
            
        return True
    except Exception as e:
        print(f"  ❌ test_template 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_help_commands():
    """测试脚本的命令行帮助"""
    print("\n🧪 测试命令行帮助...")
    
    scripts = [
        "capture_template.py",
        "process_template.py", 
        "test_template.py"
    ]
    
    all_ok = True
    for script in scripts:
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, os.path.join("scripts", script), "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                print(f"  ✅ {script}: --help 成功")
            else:
                print(f"  ⚠️  {script}: --help 失败 (返回码: {result.returncode})")
                print(f"     输出: {result.stderr[:100]}")
                all_ok = False
                
        except subprocess.TimeoutExpired:
            print(f"  ❌ {script}: --help 超时 (可能卡住)")
            all_ok = False
        except Exception as e:
            print(f"  ❌ {script}: --help 错误: {e}")
            all_ok = False
    
    return all_ok

def main():
    """主测试函数"""
    print("=" * 60)
    print("模板采集脚本 - 基本测试")
    print("=" * 60)
    
    # 测试1: 导入测试
    imports_ok = test_imports()
    
    # 测试2: 各脚本初始化
    capture_ok = test_capture_template()
    process_ok = test_process_template()
    test_ok = test_test_template()
    
    # 测试3: 命令行帮助
    help_ok = test_help_commands()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    results = [
        ("脚本导入", imports_ok),
        ("capture_template.py", capture_ok),
        ("process_template.py", process_ok),
        ("test_template.py", test_ok),
        ("命令行帮助", help_ok)
    ]
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✨ 所有基本测试通过！脚本可以正常运行。")
        print("\n下一步建议:")
        print("1. 运行实际测试（需要UI界面）:")
        print("   python scripts/capture_template.py --interactive")
        print("2. 创建示例模板进行测试")
        print("3. 开始采集ChatGPT UI模板")
        return 0
    else:
        print("⚠️  部分测试失败，需要修复。")
        return 1

if __name__ == "__main__":
    sys.exit(main())