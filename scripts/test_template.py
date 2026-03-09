#!/usr/bin/env python3
"""
模板测试工具
用于测试UI模板的识别准确性
"""
import sys
import os
import time
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import cv2
    import numpy as np
    import pyautogui
    from PIL import Image
except ImportError as e:
    print(f"❌ 缺少依赖: {e}")
    print("💡 请安装依赖: pip install opencv-python pillow numpy pyautogui")
    sys.exit(1)


class TemplateTester:
    """模板测试工具"""
    
    def __init__(self, template_dir: str = "visual_automation/config/templates/"):
        """
        初始化模板测试器
        
        Args:
            template_dir: 模板目录
        """
        self.template_dir = template_dir
        self.screen_width, self.screen_height = pyautogui.size()
        
        print(f"📺 屏幕分辨率: {self.screen_width}x{self.screen_height}")
        print(f"📁 模板目录: {template_dir}")
        
        # 缓存已加载的模板
        self.templates = {}
        
    def load_template(self, template_path: str) -> np.ndarray:
        """
        加载模板图像
        
        Args:
            template_path: 模板路径
            
        Returns:
            模板图像
        """
        if template_path in self.templates:
            return self.templates[template_path]
        
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"模板不存在: {template_path}")
        
        template = cv2.imread(template_path)
        if template is None:
            raise ValueError(f"无法加载模板: {template_path}")
        
        self.templates[template_path] = template
        print(f"📄 加载模板: {template_path} ({template.shape[1]}x{template.shape[0]})")
        return template
    
    def find_templates_in_directory(self, directory: str) -> list:
        """
        查找目录中的所有模板文件
        
        Args:
            directory: 目录路径
            
        Returns:
            模板文件路径列表
        """
        if not os.path.exists(directory):
            print(f"⚠️  目录不存在: {directory}")
            return []
        
        image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
        template_files = []
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if Path(file).suffix.lower() in image_extensions:
                    template_files.append(os.path.join(root, file))
        
        print(f"🔍 在 {directory} 中找到 {len(template_files)} 个模板")
        return template_files
    
    def capture_screen(self, region: tuple = None) -> np.ndarray:
        """
        捕获屏幕截图
        
        Args:
            region: 区域 (x, y, width, height)，None为全屏
            
        Returns:
            截图图像
        """
        print("📸 正在截取屏幕...")
        
        if region:
            x, y, w, h = region
            screenshot = pyautogui.screenshot(region=(x, y, w, h))
        else:
            screenshot = pyautogui.screenshot()
        
        # 转换为OpenCV格式
        screenshot_np = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        return screenshot_np
    
    def find_template(self, screenshot: np.ndarray, template: np.ndarray, 
                     method: int = cv2.TM_CCOEFF_NORMED, 
                     threshold: float = 0.8) -> list:
        """
        在截图中查找模板
        
        Args:
            screenshot: 截图图像
            template: 模板图像
            method: 匹配方法
            threshold: 置信度阈值
            
        Returns:
            匹配结果列表 [(x, y, width, height, confidence), ...]
        """
        # 执行模板匹配
        result = cv2.matchTemplate(screenshot, template, method)
        
        # 获取匹配位置
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            # 对于平方差方法，值越小越好
            locations = np.where(result <= 1.0 - threshold)
            values = 1.0 - result[locations]
        else:
            # 对于相关系数方法，值越大越好
            locations = np.where(result >= threshold)
            values = result[locations]
        
        # 转换为位置列表
        matches = []
        h, w = template.shape[:2]
        
        for y, x, confidence in zip(locations[0], locations[1], values):
            matches.append((x, y, w, h, confidence))
        
        return matches
    
    def non_max_suppression(self, matches: list, overlap_threshold: float = 0.5) -> list:
        """
        非极大值抑制，去除重叠的检测结果
        
        Args:
            matches: 匹配结果列表
            overlap_threshold: 重叠阈值
            
        Returns:
            抑制后的结果列表
        """
        if not matches:
            return []
        
        # 按置信度排序
        matches = sorted(matches, key=lambda x: x[4], reverse=True)
        
        suppressed = []
        
        while matches:
            # 取置信度最高的结果
            current = matches.pop(0)
            suppressed.append(current)
            
            # 计算与剩余结果的重叠
            to_remove = []
            for i, other in enumerate(matches):
                if self._boxes_overlap(current, other, overlap_threshold):
                    to_remove.append(i)
            
            # 移除重叠的结果
            for i in reversed(to_remove):
                matches.pop(i)
        
        return suppressed
    
    def _boxes_overlap(self, box1: tuple, box2: tuple, threshold: float = 0.5) -> bool:
        """检查两个边界框是否重叠超过阈值"""
        x1, y1, w1, h1, _ = box1
        x2, y2, w2, h2, _ = box2
        
        # 计算交集
        x_left = max(x1, x2)
        y_top = max(y1, y2)
        x_right = min(x1 + w1, x2 + w2)
        y_bottom = min(y1 + h1, y2 + h2)
        
        if x_right <= x_left or y_bottom <= y_top:
            return False
        
        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        area1 = w1 * h1
        area2 = w2 * h2
        
        # 计算重叠比例
        overlap_ratio = intersection_area / min(area1, area2)
        
        return overlap_ratio > threshold
    
    def visualize_matches(self, screenshot: np.ndarray, matches: list, 
                         template_name: str = "Template") -> np.ndarray:
        """
        在截图上可视化匹配结果
        
        Args:
            screenshot: 截图图像
            matches: 匹配结果列表
            template_name: 模板名称
            
        Returns:
            可视化图像
        """
        visualization = screenshot.copy()
        
        for i, (x, y, w, h, confidence) in enumerate(matches):
            # 根据置信度选择颜色
            if confidence > 0.9:
                color = (0, 255, 0)  # 绿色（高置信度）
            elif confidence > 0.8:
                color = (0, 200, 255)  # 橙色（中高置信度）
            else:
                color = (0, 100, 255)  # 红色（低置信度）
            
            # 绘制边界框
            cv2.rectangle(visualization, (x, y), (x + w, y + h), color, 2)
            
            # 绘制置信度标签
            label = f"{template_name}: {confidence:.3f}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            thickness = 1
            
            # 计算文本大小
            text_size = cv2.getTextSize(label, font, font_scale, thickness)[0]
            
            # 绘制文本背景
            cv2.rectangle(visualization, (x, y - text_size[1] - 10),
                         (x + text_size[0], y), color, -1)
            
            # 绘制文本
            cv2.putText(visualization, label, (x, y - 5), font, font_scale,
                       (255, 255, 255), thickness)
            
            # 添加编号（如果多个匹配）
            if len(matches) > 1:
                cv2.putText(visualization, f"#{i+1}", (x + 5, y + 20), font,
                           font_scale, (255, 255, 255), thickness)
        
        return visualization
    
    def test_single_template(self, template_path: str, threshold: float = 0.8,
                           region: tuple = None, method: int = cv2.TM_CCOEFF_NORMED):
        """
        测试单个模板
        
        Args:
            template_path: 模板路径
            threshold: 置信度阈值
            region: 搜索区域
            method: 匹配方法
        """
        print(f"\n🧪 测试模板: {template_path}")
        print(f"   阈值: {threshold}")
        print(f"   方法: {self._method_name(method)}")
        
        if region:
            print(f"   区域: {region}")
        
        # 加载模板
        template = self.load_template(template_path)
        
        # 截取屏幕
        screenshot = self.capture_screen(region)
        
        # 查找模板
        start_time = time.time()
        matches = self.find_template(screenshot, template, method, threshold)
        elapsed = time.time() - start_time
        
        print(f"⏱️  匹配耗时: {elapsed*1000:.1f}ms")
        
        # 应用非极大值抑制
        if matches:
            matches = self.non_max_suppression(matches)
            print(f"🔍 找到 {len(matches)} 个匹配 (抑制后)")
        else:
            print("❌ 未找到匹配")
        
        # 显示结果
        if matches:
            for i, (x, y, w, h, confidence) in enumerate(matches):
                print(f"  {i+1}. 位置: ({x}, {y}) 尺寸: {w}x{h} 置信度: {confidence:.3f}")
        
        # 可视化结果
        template_name = os.path.splitext(os.path.basename(template_path))[0]
        visualization = self.visualize_matches(screenshot, matches, template_name)
        
        # 显示结果
        cv2.imshow(f"匹配结果: {template_name}", visualization)
        print("🖼️  按任意键关闭窗口...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        return len(matches) > 0
    
    def test_threshold_sensitivity(self, template_path: str, region: tuple = None):
        """
        测试模板的阈值敏感性
        
        Args:
            template_path: 模板路径
            region: 搜索区域
        """
        print(f"\n📊 测试阈值敏感性: {template_path}")
        
        # 加载模板
        template = self.load_template(template_path)
        
        # 截取屏幕
        screenshot = self.capture_screen(region)
        
        # 测试不同阈值
        thresholds = [0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95]
        results = []
        
        for threshold in thresholds:
            matches = self.find_template(screenshot, template, cv2.TM_CCOEFF_NORMED, threshold)
            matches = self.non_max_suppression(matches)
            results.append((threshold, len(matches)))
            
            if matches:
                avg_confidence = np.mean([m[4] for m in matches])
                print(f"  阈值 {threshold:.2f}: {len(matches)} 个匹配, 平均置信度 {avg_confidence:.3f}")
            else:
                print(f"  阈值 {threshold:.2f}: 0 个匹配")
        
        # 找到最佳阈值（最多匹配且阈值最高）
        max_matches = max(results, key=lambda x: x[1])[1]
        if max_matches > 0:
            best_threshold = max([t for t, m in results if m == max_matches])
            print(f"✨ 推荐阈值: {best_threshold:.2f}")
        else:
            print("⚠️  在所有阈值下都未找到匹配")
    
    def batch_test_templates(self, template_dir: str, threshold: float = 0.8):
        """
        批量测试模板
        
        Args:
            template_dir: 模板目录
            threshold: 置信度阈值
        """
        print(f"\n🔄 批量测试模板: {template_dir}")
        
        # 查找所有模板
        template_files = self.find_templates_in_directory(template_dir)
        
        if not template_files:
            print("❌ 未找到模板文件")
            return
        
        results = []
        
        for template_path in template_files:
            try:
                # 截取屏幕
                screenshot = self.capture_screen()
                
                # 加载模板
                template = self.load_template(template_path)
                
                # 测试模板
                matches = self.find_template(screenshot, template, cv2.TM_CCOEFF_NORMED, threshold)
                matches = self.non_max_suppression(matches)
                
                found = len(matches) > 0
                match_count = len(matches)
                avg_confidence = np.mean([m[4] for m in matches]) if matches else 0
                
                results.append({
                    'template': os.path.basename(template_path),
                    'found': found,
                    'match_count': match_count,
                    'avg_confidence': avg_confidence,
                    'path': template_path
                })
                
                status = "✅" if found else "❌"
                print(f"{status} {os.path.basename(template_path)}: {match_count} 个匹配, 平均置信度 {avg_confidence:.3f}")
                
            except Exception as e:
                print(f"⚠️  测试失败 {os.path.basename(template_path)}: {e}")
                results.append({
                    'template': os.path.basename(template_path),
                    'found': False,
                    'match_count': 0,
                    'avg_confidence': 0,
                    'path': template_path,
                    'error': str(e)
                })
        
        # 输出总结
        print(f"\n📊 批量测试总结")
        print(f"   测试模板数: {len(template_files)}")
        
        successful = sum(1 for r in results if r['found'])
        print(f"   成功识别: {successful}/{len(template_files)} ({successful/len(template_files)*100:.1f}%)")
        
        if successful > 0:
            avg_conf = np.mean([r['avg_confidence'] for r in results if r['found']])
            print(f"   平均置信度: {avg_conf:.3f}")
        
        # 显示失败的模板
        failed = [r for r in results if not r['found']]
        if failed:
            print(f"\n❌ 失败的模板:")
            for r in failed:
                print(f"   - {r['template']}")
    
    def _method_name(self, method: int) -> str:
        """获取匹配方法名称"""
        methods = {
            cv2.TM_CCOEFF: 'TM_CCOEFF',
            cv2.TM_CCOEFF_NORMED: 'TM_CCOEFF_NORMED',
            cv2.TM_CCORR: 'TM_CCORR',
            cv2.TM_CCORR_NORMED: 'TM_CCORR_NORMED',
            cv2.TM_SQDIFF: 'TM_SQDIFF',
            cv2.TM_SQDIFF_NORMED: 'TM_SQDIFF_NORMED'
        }
        return methods.get(method, f'Unknown ({method})')
    
    def interactive_test(self):
        """交互式测试模式"""
        print("\n" + "=" * 60)
        print("🧪 交互式模板测试")
        print("=" * 60)
        
        # 选择模板目录
        categories = []
        if os.path.exists(self.template_dir):
            for item in os.listdir(self.template_dir):
                if os.path.isdir(os.path.join(self.template_dir, item)):
                    categories.append(item)
        
        if categories:
            print("\n📁 可用的模板类别:")
            for i, category in enumerate(categories, 1):
                print(f"  {i}. {category}")
            
            print(f"  {len(categories)+1}. 手动输入路径")
            
            choice = input(f"选择类别 (1-{len(categories)+1}, 默认1): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(categories):
                category = categories[int(choice) - 1]
                test_dir = os.path.join(self.template_dir, category)
            else:
                test_dir = input("请输入模板路径: ").strip()
        else:
            test_dir = input("请输入模板路径: ").strip()
        
        if not os.path.exists(test_dir):
            print(f"❌ 路径不存在: {test_dir}")
            return
        
        # 选择模板
        template_files = self.find_templates_in_directory(test_dir)
        
        if not template_files:
            print("❌ 未找到模板文件")
            return
        
        print(f"\n🔍 找到 {len(template_files)} 个模板:")
        for i, template_path in enumerate(template_files[:20], 1):  # 只显示前20个
            template_name = os.path.splitext(os.path.basename(template_path))[0]
            print(f"  {i}. {template_name}")
        
        if len(template_files) > 20:
            print(f"  ... 和 {len(template_files) - 20} 个更多")
        
        choice = input(f"选择模板 (1-{min(20, len(template_files))}), 或输入路径: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= min(20, len(template_files)):
            template_path = template_files[int(choice) - 1]
        else:
            template_path = choice if os.path.exists(choice) else os.path.join(test_dir, choice)
        
        # 测试参数
        print("\n⚙️  测试参数")
        threshold = float(input("置信度阈值 (0.0-1.0, 默认0.8): ").strip() or "0.8")
        
        # 选择搜索区域
        region_choice = input("搜索区域 (1=全屏, 2=指定区域, 默认1): ").strip() or "1"
        
        region = None
        if region_choice == "2":
            print("📐 请指定区域 (格式: x,y,width,height)")
            region_str = input("区域: ").strip()
            if region_str:
                try:
                    x, y, w, h = map(int, region_str.split(','))
                    region = (x, y, w, h)
                except:
                    print("⚠️  区域格式错误，使用全屏")
        
        # 执行测试
        self.test_single_template(template_path, threshold, region)
        
        # 是否测试阈值敏感性
        sensitivity = input("\n是否测试阈值敏感性？ (y/N): ").strip().lower()
        if sensitivity == 'y':
            self.test_threshold_sensitivity(template_path, region)
        
        # 是否批量测试其他模板
        batch = input("\n是否批量测试此目录下所有模板？ (y/N): ").strip().lower()
        if batch == 'y':
            self.batch_test_templates(test_dir, threshold)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="模板测试工具")
    parser.add_argument("--template", "-t", help="模板文件路径")
    parser.add_argument("--dir", "-d", help="模板目录路径")
    parser.add_argument("--threshold", "-th", type=float, default=0.8,
                       help="置信度阈值 (默认: 0.8)")
    parser.add_argument("--region", "-r", help="搜索区域 x,y,width,height")
    parser.add_argument("--method", "-m", type=int, default=cv2.TM_CCOEFF_NORMED,
                       help=f"匹配方法 (默认: {cv2.TM_CCOEFF_NORMED})")
    parser.add_argument("--batch", "-b", action="store_true", help="批量测试模式")
    parser.add_argument("--sensitivity", "-s", action="store_true", 
                       help="测试阈值敏感性")
    parser.add_argument("--interactive", "-i", action="store_true",
                       help="交互式模式")
    
    args = parser.parse_args()
    
    # 创建测试器
    tester = TemplateTester()
    
    # 解析区域参数
    region = None
    if args.region:
        try:
            x, y, w, h = map(int, args.region.split(','))
            region = (x, y, w, h)
        except:
            print("⚠️  区域格式错误，使用全屏")
    
    if args.interactive:
        # 交互式模式
        tester.interactive_test()
        
    elif args.batch and args.dir:
        # 批量测试模式
        tester.batch_test_templates(args.dir, args.threshold)
        
    elif args.sensitivity and args.template:
        # 阈值敏感性测试
        tester.test_threshold_sensitivity(args.template, region)
        
    elif args.template:
        # 单个模板测试
        tester.test_single_template(args.template, args.threshold, region, args.method)
        
    elif args.dir:
        # 批量测试默认目录
        tester.batch_test_templates(args.dir, args.threshold)
        
    else:
        print("❌ 请指定模板文件或目录，或使用 --interactive 进入交互模式")
        print("💡 使用 --help 查看帮助信息")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)