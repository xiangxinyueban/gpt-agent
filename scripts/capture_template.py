#!/usr/bin/env python3
"""
交互式UI模板采集工具
用于捕获屏幕上的UI元素作为模板图像
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
    import pyautogui
    import numpy as np
    from PIL import Image, ImageDraw
except ImportError as e:
    print(f"❌ 缺少依赖: {e}")
    print("💡 请安装依赖: pip install pyautogui opencv-python pillow numpy")
    sys.exit(1)


class TemplateCaptureTool:
    """模板采集工具"""
    
    def __init__(self, template_dir: str = "visual_automation/config/templates/"):
        """
        初始化模板采集工具
        
        Args:
            template_dir: 模板保存目录
        """
        self.template_dir = template_dir
        self.screen_width, self.screen_height = pyautogui.size()
        
        print(f"📺 屏幕分辨率: {self.screen_width}x{self.screen_height}")
        print(f"📁 模板目录: {template_dir}")
        
        # 确保模板目录存在
        os.makedirs(template_dir, exist_ok=True)
    
    def capture_full_screen(self, save_path: str = None) -> np.ndarray:
        """
        捕获全屏截图
        
        Args:
            save_path: 保存路径（可选）
            
        Returns:
            截图图像（numpy数组，BGR格式）
        """
        print("📸 正在截取全屏...")
        
        # 使用pyautogui截屏
        screenshot = pyautogui.screenshot()
        
        # 转换为OpenCV格式（BGR）
        screenshot_np = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        if save_path:
            cv2.imwrite(save_path, screenshot_np)
            print(f"💾 全屏截图已保存: {save_path}")
        
        return screenshot_np
    
    def select_region_interactively(self, screenshot: np.ndarray) -> tuple:
        """
        交互式选择区域
        
        Args:
            screenshot: 截图图像
            
        Returns:
            (x, y, width, height) 或 None（如果用户取消）
        """
        print("\n🎯 交互式区域选择")
        print("=" * 40)
        print("1. 在图像上点击并拖动鼠标选择区域")
        print("2. 按 's' 保存选区")
        print("3. 按 'r' 重新选择")
        print("4. 按 'q' 或 ESC 取消")
        print("=" * 40)
        
        # 创建窗口
        window_name = "选择UI元素区域 (s=保存, r=重选, q=取消)"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        # 调整窗口大小
        cv2.resizeWindow(window_name, min(1200, self.screen_width // 2), 
                        min(800, self.screen_height // 2))
        
        # 复制图像用于绘制
        drawing_image = screenshot.copy()
        
        # 选择状态变量
        selecting = False
        x_start, y_start = -1, -1
        x_end, y_end = -1, -1
        selection_made = False
        
        def mouse_callback(event, x, y, flags, param):
            nonlocal selecting, x_start, y_start, x_end, y_end, drawing_image
            
            if event == cv2.EVENT_LBUTTONDOWN:
                selecting = True
                x_start, y_start = x, y
                x_end, y_end = x, y
                
            elif event == cv2.EVENT_MOUSEMOVE:
                if selecting:
                    x_end, y_end = x, y
                    # 更新绘制图像
                    drawing_image = screenshot.copy()
                    cv2.rectangle(drawing_image, (x_start, y_start), (x_end, y_end), 
                                (0, 255, 0), 2)
                    
            elif event == cv2.EVENT_LBUTTONUP:
                selecting = False
                x_end, y_end = x, y
                selection_made = True
        
        # 设置鼠标回调
        cv2.setMouseCallback(window_name, mouse_callback)
        
        while True:
            # 如果没有正在选择，显示当前状态
            if not selecting and not selection_made:
                drawing_image = screenshot.copy()
                cv2.putText(drawing_image, "点击并拖动选择区域", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            cv2.imshow(window_name, drawing_image)
            
            # 等待按键
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('s') or key == 13:  # 's' 或 Enter
                if selection_made:
                    break
                else:
                    print("⚠️  请先选择区域")
                    
            elif key == ord('r'):  # 'r' 重选
                selecting = False
                selection_made = False
                x_start = y_start = x_end = y_end = -1
                print("🔄 重新选择区域")
                
            elif key == ord('q') or key == 27:  # 'q' 或 ESC
                cv2.destroyAllWindows()
                return None
        
        cv2.destroyAllWindows()
        
        # 计算区域
        x = min(x_start, x_end)
        y = min(y_start, y_end)
        width = abs(x_end - x_start)
        height = abs(y_end - y_start)
        
        # 确保区域有效
        if width < 10 or height < 10:
            print("⚠️  选择区域太小，请重新选择")
            return self.select_region_interactively(screenshot)
        
        print(f"✅ 选择区域: ({x}, {y}) {width}x{height}")
        return (x, y, width, height)
    
    def auto_detect_element(self, screenshot: np.ndarray) -> list:
        """
        自动检测可能的UI元素
        
        Args:
            screenshot: 截图图像
            
        Returns:
            检测到的区域列表 [(x, y, w, h), ...]
        """
        print("🤖 正在自动检测UI元素...")
        
        # 转换为灰度图
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        
        # 使用边缘检测
        edges = cv2.Canny(gray, 50, 150)
        
        # 查找轮廓
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detected_regions = []
        
        for contour in contours:
            # 过滤太小的轮廓
            area = cv2.contourArea(contour)
            if area < 500 or area > 50000:  # 过滤太小或太大的区域
                continue
            
            # 获取边界框
            x, y, w, h = cv2.boundingRect(contour)
            
            # 过滤太窄或太高的区域
            aspect_ratio = w / h
            if aspect_ratio < 0.2 or aspect_ratio > 5.0:
                continue
            
            detected_regions.append((x, y, w, h))
        
        print(f"🔍 检测到 {len(detected_regions)} 个可能元素")
        return detected_regions
    
    def preview_detected_elements(self, screenshot: np.ndarray, regions: list):
        """
        预览自动检测到的元素
        
        Args:
            screenshot: 截图图像
            regions: 检测到的区域列表
        """
        preview = screenshot.copy()
        
        for i, (x, y, w, h) in enumerate(regions):
            # 绘制边界框
            color = (0, 255, 0) if i % 3 == 0 else (255, 0, 0) if i % 3 == 1 else (0, 0, 255)
            cv2.rectangle(preview, (x, y), (x + w, y + h), color, 2)
            
            # 添加编号
            cv2.putText(preview, str(i + 1), (x, y - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # 显示预览
        cv2.imshow("自动检测结果 (按任意键继续)", preview)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    def extract_template(self, screenshot: np.ndarray, region: tuple) -> np.ndarray:
        """
        从截图中提取模板
        
        Args:
            screenshot: 截图图像
            region: 区域 (x, y, width, height)
            
        Returns:
            模板图像
        """
        x, y, w, h = region
        template = screenshot[y:y+h, x:x+w]
        
        print(f"📐 提取模板: {w}x{h} 像素")
        return template
    
    def save_template(self, template: np.ndarray, template_name: str, 
                     category: str = "common") -> str:
        """
        保存模板图像
        
        Args:
            template: 模板图像
            template_name: 模板名称（不含扩展名）
            category: 类别目录（如 chatgpt, cloudflare, common）
            
        Returns:
            保存的文件路径
        """
        # 创建类别目录
        category_dir = os.path.join(self.template_dir, category)
        os.makedirs(category_dir, exist_ok=True)
        
        # 生成文件名
        filename = f"{template_name}.png"
        filepath = os.path.join(category_dir, filename)
        
        # 保存图像
        cv2.imwrite(filepath, template)
        
        print(f"💾 模板已保存: {filepath}")
        return filepath
    
    def run_interactive(self):
        """运行交互式模板采集"""
        print("\n" + "=" * 60)
        print("🖼️  UI模板采集工具")
        print("=" * 60)
        
        # 1. 获取模板信息
        print("\n📝 请输入模板信息")
        template_name = input("模板名称（英文，如 login_button）: ").strip()
        
        if not template_name:
            print("❌ 模板名称不能为空")
            return False
        
        category = input("类别目录（默认: common）: ").strip() or "common"
        
        # 2. 倒计时准备
        print("\n⏱️  准备截屏，请将目标UI元素显示在屏幕上...")
        for i in range(3, 0, -1):
            print(f"   {i}...")
            time.sleep(1)
        
        print("   📸 截屏!")
        
        # 3. 截取全屏
        screenshot = self.capture_full_screen()
        
        # 4. 选择模式
        print("\n🎯 选择采集模式:")
        print("  1. 交互式手动选择")
        print("  2. 自动检测元素")
        choice = input("请选择 (1/2, 默认1): ").strip() or "1"
        
        if choice == "2":
            # 自动检测模式
            regions = self.auto_detect_element(screenshot)
            
            if not regions:
                print("❌ 未检测到有效元素，切换到手动模式")
                choice = "1"
            else:
                self.preview_detected_elements(screenshot, regions)
                
                region_choice = input("请选择元素编号 (1-{}), 或按回车手动选择: ".format(len(regions))).strip()
                
                if region_choice and region_choice.isdigit():
                    idx = int(region_choice) - 1
                    if 0 <= idx < len(regions):
                        region = regions[idx]
                    else:
                        print("❌ 无效编号，切换到手动模式")
                        choice = "1"
                else:
                    print("切换到手动模式")
                    choice = "1"
        
        if choice == "1":
            # 手动选择模式
            region = self.select_region_interactively(screenshot)
            
            if region is None:
                print("❌ 用户取消选择")
                return False
        
        # 5. 提取并保存模板
        template = self.extract_template(screenshot, region)
        
        # 预览模板
        cv2.imshow("模板预览 (按任意键继续)", template)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        # 确认保存
        confirm = input("是否保存此模板？ (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ 取消保存")
            return False
        
        filepath = self.save_template(template, template_name, category)
        
        print(f"\n✅ 模板采集完成!")
        print(f"   名称: {template_name}")
        print(f"   类别: {category}")
        print(f"   尺寸: {template.shape[1]}x{template.shape[0]}")
        print(f"   路径: {filepath}")
        
        return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="UI模板采集工具")
    parser.add_argument("--dir", default="visual_automation/config/templates/",
                       help="模板保存目录")
    parser.add_argument("--name", help="模板名称（非交互模式）")
    parser.add_argument("--category", default="common", help="类别目录")
    parser.add_argument("--x", type=int, help="区域左上角X坐标")
    parser.add_argument("--y", type=int, help="区域左上角Y坐标")
    parser.add_argument("--width", type=int, help="区域宽度")
    parser.add_argument("--height", type=int, help="区域高度")
    parser.add_argument("--auto", action="store_true", help="自动模式")
    
    args = parser.parse_args()
    
    # 创建工具实例
    tool = TemplateCaptureTool(template_dir=args.dir)
    
    if args.name and args.x is not None and args.y is not None and args.width and args.height:
        # 命令行模式
        print(f"🖼️  命令行模式: {args.name}")
        
        screenshot = tool.capture_full_screen()
        region = (args.x, args.y, args.width, args.height)
        template = tool.extract_template(screenshot, region)
        tool.save_template(template, args.name, args.category)
        
    elif args.auto:
        # 自动模式（批量采集）
        print("🤖 自动检测模式")
        
        screenshot = tool.capture_full_screen()
        regions = tool.auto_detect_element(screenshot)
        
        if regions:
            tool.preview_detected_elements(screenshot, regions)
            
            for i, region in enumerate(regions):
                template = tool.extract_template(screenshot, region)
                name = f"auto_element_{i+1:03d}"
                tool.save_template(template, name, "auto_detected")
                
            print(f"✅ 保存了 {len(regions)} 个自动检测模板")
        else:
            print("❌ 未检测到元素")
            
    else:
        # 交互模式
        tool.run_interactive()


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