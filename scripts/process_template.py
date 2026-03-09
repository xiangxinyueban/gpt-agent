#!/usr/bin/env python3
"""
模板处理工具
用于优化和增强UI模板图像
"""
import sys
import os
import glob
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import cv2
    import numpy as np
    from PIL import Image, ImageEnhance, ImageFilter
except ImportError as e:
    print(f"❌ 缺少依赖: {e}")
    print("💡 请安装依赖: pip install opencv-python pillow numpy")
    sys.exit(1)


class TemplateProcessor:
    """模板处理工具"""
    
    def __init__(self):
        """初始化处理器"""
        print("🛠️  模板处理器已初始化")
    
    def load_image(self, image_path: str) -> np.ndarray:
        """
        加载图像
        
        Args:
            image_path: 图像路径
            
        Returns:
            图像数组 (BGR格式)
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图像不存在: {image_path}")
        
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"无法加载图像: {image_path}")
        
        print(f"📄 加载图像: {image_path} ({image.shape[1]}x{image.shape[0]})")
        return image
    
    def save_image(self, image: np.ndarray, output_path: str):
        """
        保存图像
        
        Args:
            image: 图像数组
            output_path: 输出路径
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, image)
        print(f"💾 保存图像: {output_path}")
    
    def resize_template(self, template: np.ndarray, max_size: tuple = (200, 200)) -> np.ndarray:
        """
        调整模板大小
        
        Args:
            template: 模板图像
            max_size: 最大尺寸 (width, height)
            
        Returns:
            调整后的图像
        """
        h, w = template.shape[:2]
        max_w, max_h = max_size
        
        # 如果图像已经小于最大尺寸，直接返回
        if w <= max_w and h <= max_h:
            print(f"📏 尺寸合适: {w}x{h} (无需调整)")
            return template
        
        # 计算缩放比例
        scale_w = max_w / w
        scale_h = max_h / h
        scale = min(scale_w, scale_h)
        
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # 使用高质量缩放
        resized = cv2.resize(template, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        print(f"📏 调整尺寸: {w}x{h} -> {new_w}x{new_h} (缩放: {scale:.2f})")
        return resized
    
    def remove_background(self, template: np.ndarray, threshold: float = 0.9) -> np.ndarray:
        """
        尝试移除背景（简单版本）
        
        Args:
            template: 模板图像
            threshold: 背景检测阈值
            
        Returns:
            处理后的图像
        """
        print("🎨 尝试移除背景...")
        
        # 转换为灰度图
        gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        
        # 创建二值掩码
        _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 反转掩码（假设背景较亮）
        if np.mean(mask) > 127:
            mask = cv2.bitwise_not(mask)
        
        # 应用掩码
        result = cv2.bitwise_and(template, template, mask=mask)
        
        # 转换为RGBA（添加透明度通道）
        rgba = cv2.cvtColor(result, cv2.COLOR_BGR2BGRA)
        
        # 设置透明度
        rgba[:, :, 3] = mask
        
        print(f"🎨 背景移除完成 (阈值: {threshold})")
        return rgba
    
    def enhance_contrast(self, template: np.ndarray, factor: float = 1.5) -> np.ndarray:
        """
        增强对比度
        
        Args:
            template: 模板图像
            factor: 增强因子 (1.0 = 不变)
            
        Returns:
            增强后的图像
        """
        print(f"🌈 增强对比度 (因子: {factor})...")
        
        # 使用PIL进行对比度增强
        pil_image = Image.fromarray(cv2.cvtColor(template, cv2.COLOR_BGR2RGB))
        enhancer = ImageEnhance.Contrast(pil_image)
        enhanced_pil = enhancer.enhance(factor)
        
        # 转换回OpenCV格式
        enhanced = cv2.cvtColor(np.array(enhanced_pil), cv2.COLOR_RGB2BGR)
        
        return enhanced
    
    def sharpen_image(self, template: np.ndarray, strength: float = 2.0) -> np.ndarray:
        """
        锐化图像
        
        Args:
            template: 模板图像
            strength: 锐化强度
            
        Returns:
            锐化后的图像
        """
        print(f"🔍 锐化图像 (强度: {strength})...")
        
        # 使用PIL进行锐化
        pil_image = Image.fromarray(cv2.cvtColor(template, cv2.COLOR_BGR2RGB))
        
        # 应用锐化滤镜
        sharpened = pil_image.filter(ImageFilter.UnsharpMask(
            radius=2, percent=int(strength * 100), threshold=3))
        
        # 转换回OpenCV格式
        result = cv2.cvtColor(np.array(sharpened), cv2.COLOR_RGB2BGR)
        
        return result
    
    def normalize_brightness(self, template: np.ndarray, target_brightness: float = 128) -> np.ndarray:
        """
        标准化亮度
        
        Args:
            template: 模板图像
            target_brightness: 目标亮度值 (0-255)
            
        Returns:
            标准化后的图像
        """
        print(f"💡 标准化亮度 (目标: {target_brightness})...")
        
        # 转换为灰度图计算当前亮度
        gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        current_brightness = np.mean(gray)
        
        # 计算调整因子
        if current_brightness == 0:
            print("⚠️  亮度为0，跳过调整")
            return template
        
        adjustment_factor = target_brightness / current_brightness
        
        # 调整亮度
        adjusted = cv2.convertScaleAbs(template, alpha=adjustment_factor, beta=0)
        
        print(f"💡 亮度调整: {current_brightness:.1f} -> {np.mean(cv2.cvtColor(adjusted, cv2.COLOR_BGR2GRAY)):.1f}")
        return adjusted
    
    def add_border(self, template: np.ndarray, border_size: int = 5, 
                  border_color: tuple = (0, 0, 0)) -> np.ndarray:
        """
        添加边框（帮助模板匹配）
        
        Args:
            template: 模板图像
            border_size: 边框大小
            border_color: 边框颜色 (B, G, R)
            
        Returns:
            带边框的图像
        """
        print(f"🖼️  添加边框 ({border_size}px)...")
        
        # 添加边框
        bordered = cv2.copyMakeBorder(
            template, 
            border_size, border_size, border_size, border_size,
            cv2.BORDER_CONSTANT, value=border_color
        )
        
        return bordered
    
    def create_variants(self, template: np.ndarray, variant_count: int = 3) -> list:
        """
        创建模板变体（增加匹配鲁棒性）
        
        Args:
            template: 原始模板
            variant_count: 变体数量
            
        Returns:
            变体列表
        """
        print(f"🔄 创建 {variant_count} 个模板变体...")
        
        variants = []
        
        # 变体1: 轻微缩放（95%）
        scale_95 = cv2.resize(template, None, fx=0.95, fy=0.95, interpolation=cv2.INTER_AREA)
        variants.append(("scaled_95", scale_95))
        
        # 变体2: 轻微缩放（105%）
        scale_105 = cv2.resize(template, None, fx=1.05, fy=1.05, interpolation=cv2.INTER_AREA)
        variants.append(("scaled_105", scale_105))
        
        # 变体3: 轻微旋转（-5度）
        if variant_count >= 3:
            h, w = template.shape[:2]
            center = (w // 2, h // 2)
            matrix = cv2.getRotationMatrix2D(center, -5, 1.0)
            rotated = cv2.warpAffine(template, matrix, (w, h))
            variants.append(("rotated_-5", rotated))
        
        # 变体4: 轻微旋转（+5度）
        if variant_count >= 4:
            matrix = cv2.getRotationMatrix2D(center, 5, 1.0)
            rotated = cv2.warpAffine(template, matrix, (w, h))
            variants.append(("rotated_+5", rotated))
        
        # 变体5: 轻微亮度变化
        if variant_count >= 5:
            brightened = cv2.convertScaleAbs(template, alpha=1.2, beta=10)
            variants.append(("brightened", brightened))
        
        return variants
    
    def batch_process(self, input_dir: str, output_dir: str, 
                     operations: list = None, max_size: tuple = (200, 200)):
        """
        批量处理模板
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            operations: 操作列表 ['resize', 'contrast', 'sharpen', 'normalize']
            max_size: 最大尺寸
        """
        if operations is None:
            operations = ['resize', 'contrast', 'sharpen']
        
        print(f"🔄 批量处理: {input_dir} -> {output_dir}")
        print(f"   操作: {operations}")
        print(f"   最大尺寸: {max_size}")
        
        # 查找所有图像文件
        image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp']
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(glob.glob(os.path.join(input_dir, ext)))
        
        print(f"🔍 找到 {len(image_files)} 个图像文件")
        
        for i, image_path in enumerate(image_files):
            print(f"\n[{i+1}/{len(image_files)}] 处理: {os.path.basename(image_path)}")
            
            try:
                # 加载图像
                image = self.load_image(image_path)
                
                # 应用操作
                processed = image.copy()
                
                if 'resize' in operations:
                    processed = self.resize_template(processed, max_size)
                
                if 'contrast' in operations:
                    processed = self.enhance_contrast(processed, factor=1.5)
                
                if 'sharpen' in operations:
                    processed = self.sharpen_image(processed, strength=2.0)
                
                if 'normalize' in operations:
                    processed = self.normalize_brightness(processed, target_brightness=130)
                
                if 'border' in operations:
                    processed = self.add_border(processed, border_size=5)
                
                # 保存处理后的图像
                rel_path = os.path.relpath(image_path, input_dir)
                output_path = os.path.join(output_dir, rel_path)
                self.save_image(processed, output_path)
                
            except Exception as e:
                print(f"❌ 处理失败: {e}")
        
        print(f"\n✅ 批量处理完成!")
    
    def process_single(self, input_path: str, output_path: str = None, 
                      operations: list = None, preview: bool = True):
        """
        处理单个模板
        
        Args:
            input_path: 输入路径
            output_path: 输出路径（None则自动生成）
            operations: 操作列表
            preview: 是否预览结果
        """
        if operations is None:
            operations = ['resize', 'contrast', 'sharpen']
        
        print(f"🛠️  处理单个模板: {input_path}")
        print(f"   操作: {operations}")
        
        # 加载图像
        image = self.load_image(input_path)
        
        if preview:
            cv2.imshow("原始图像 (按任意键继续)", image)
            cv2.waitKey(0)
        
        # 应用操作
        processed = image.copy()
        
        if 'resize' in operations:
            processed = self.resize_template(processed, max_size=(200, 200))
        
        if 'contrast' in operations:
            processed = self.enhance_contrast(processed, factor=1.5)
        
        if 'sharpen' in operations:
            processed = self.sharpen_image(processed, strength=2.0)
        
        if 'normalize' in operations:
            processed = self.normalize_brightness(processed, target_brightness=130)
        
        if 'border' in operations:
            processed = self.add_border(processed, border_size=5)
        
        if 'bgremove' in operations:
            processed = self.remove_background(processed)
        
        # 生成输出路径
        if output_path is None:
            input_dir = os.path.dirname(input_path)
            input_name = os.path.basename(input_path)
            input_stem = os.path.splitext(input_name)[0]
            output_dir = os.path.join(input_dir, "processed")
            output_path = os.path.join(output_dir, f"{input_stem}_processed.png")
        
        # 保存处理后的图像
        self.save_image(processed, output_path)
        
        if preview:
            cv2.imshow("处理后的图像 (按任意键继续)", processed)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        
        # 创建变体
        create_variants = input("是否创建模板变体？ (y/N): ").strip().lower()
        if create_variants == 'y':
            variants = self.create_variants(processed, variant_count=3)
            
            variant_dir = os.path.join(os.path.dirname(output_path), "variants")
            os.makedirs(variant_dir, exist_ok=True)
            
            for name, variant in variants:
                variant_path = os.path.join(variant_dir, f"{os.path.splitext(os.path.basename(output_path))[0]}_{name}.png")
                self.save_image(variant, variant_path)
            
            print(f"✅ 创建了 {len(variants)} 个变体到 {variant_dir}")
        
        print(f"\n✅ 处理完成!")
        print(f"   输入: {input_path}")
        print(f"   输出: {output_path}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="模板处理工具")
    parser.add_argument("--input", "-i", required=True, help="输入文件或目录")
    parser.add_argument("--output", "-o", help="输出文件或目录")
    parser.add_argument("--operations", "-op", default="resize,contrast,sharpen",
                       help="操作列表，逗号分隔 (resize,contrast,sharpen,normalize,border,bgremove)")
    parser.add_argument("--max-width", type=int, default=200, help="最大宽度")
    parser.add_argument("--max-height", type=int, default=200, help="最大高度")
    parser.add_argument("--batch", "-b", action="store_true", help="批量处理模式")
    parser.add_argument("--preview", "-p", action="store_true", help="预览模式")
    
    args = parser.parse_args()
    
    # 创建处理器
    processor = TemplateProcessor()
    
    # 解析操作列表
    operations = [op.strip() for op in args.operations.split(',')]
    
    if args.batch or os.path.isdir(args.input):
        # 批量处理模式
        input_dir = args.input
        output_dir = args.output or os.path.join(input_dir, "processed")
        
        processor.batch_process(
            input_dir=input_dir,
            output_dir=output_dir,
            operations=operations,
            max_size=(args.max_width, args.max_height)
        )
    else:
        # 单个文件处理
        processor.process_single(
            input_path=args.input,
            output_path=args.output,
            operations=operations,
            preview=args.preview
        )


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