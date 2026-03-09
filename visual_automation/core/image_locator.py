"""
Image location module for visual automation.
Uses template matching to find UI elements on screen.
"""
import cv2
import numpy as np
import os
import json
from typing import Dict, List, Tuple, Optional, Union
from pathlib import Path
import time

class ImageLocator:
    """Locate UI elements using template matching."""
    
    def __init__(self, template_dir: str = "config/templates/", 
                 confidence_threshold: float = 0.85):
        """
        Initialize image locator.
        
        Args:
            template_dir: Directory containing template images
            confidence_threshold: Minimum confidence for matches (0.0-1.0)
        """
        self.template_dir = template_dir
        self.confidence_threshold = confidence_threshold
        self.templates: Dict[str, np.ndarray] = {}
        self.template_info: Dict[str, dict] = {}
        
        # Load all templates on initialization
        self.load_all_templates()
    
    def load_template(self, template_name: str) -> Optional[np.ndarray]:
        """
        Load a single template image.
        
        Args:
            template_name: Name of template file (with or without extension)
            
        Returns:
            Template image as numpy array (BGR) or None if not found
        """
        # Try different extensions
        extensions = ['.png', '.jpg', '.jpeg', '.bmp']
        
        for ext in extensions:
            # Try with and without extension
            for name_variant in [template_name, template_name + ext]:
                template_path = os.path.join(self.template_dir, name_variant)
                
                if os.path.exists(template_path):
                    template = cv2.imread(template_path)
                    if template is not None:
                        self.templates[template_name] = template
                        
                        # Store template info
                        self.template_info[template_name] = {
                            'path': template_path,
                            'size': template.shape[:2][::-1],  # (width, height)
                            'loaded_at': time.time()
                        }
                        
                        print(f"📄 Loaded template: {template_name} ({template.shape[1]}x{template.shape[0]})")
                        return template
        
        print(f"⚠️  Template not found: {template_name}")
        return None
    
    def load_all_templates(self):
        """Load all template images from the template directory."""
        if not os.path.exists(self.template_dir):
            print(f"📁 Creating template directory: {self.template_dir}")
            os.makedirs(self.template_dir, exist_ok=True)
            return
        
        # Find all image files
        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
        
        for root, dirs, files in os.walk(self.template_dir):
            for file in files:
                if Path(file).suffix.lower() in image_extensions:
                    # Use relative path as template name
                    rel_path = os.path.relpath(os.path.join(root, file), self.template_dir)
                    template_name = Path(rel_path).stem  # Remove extension
                    
                    # Load template
                    self.load_template(rel_path)
    
    def find_template(self, screenshot: np.ndarray, template_name: str, 
                     method: int = cv2.TM_CCOEFF_NORMED) -> Tuple[Optional[Tuple[int, int, int, int]], float]:
        """
        Find a template in a screenshot.
        
        Args:
            screenshot: Screenshot to search in (BGR format)
            template_name: Name of template to find
            method: OpenCV template matching method
            
        Returns:
            Tuple of (region, confidence) where region is (x, y, width, height) or None
        """
        # Load template if not already loaded
        if template_name not in self.templates:
            template = self.load_template(template_name)
            if template is None:
                return None, 0.0
        
        template = self.templates[template_name]
        
        # Perform template matching
        result = cv2.matchTemplate(screenshot, template, method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # For TM_CCOEFF_NORMED, higher values are better
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            confidence = 1.0 - min_val
            top_left = min_loc
        else:
            confidence = max_val
            top_left = max_loc
        
        # Check if confidence meets threshold
        if confidence < self.confidence_threshold:
            return None, confidence
        
        # Calculate region
        template_height, template_width = template.shape[:2]
        region = (top_left[0], top_left[1], template_width, template_height)
        
        return region, confidence
    
    def find_all_instances(self, screenshot: np.ndarray, template_name: str,
                          method: int = cv2.TM_CCOEFF_NORMED,
                          overlap_threshold: float = 0.5) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """
        Find all instances of a template in a screenshot.
        
        Args:
            screenshot: Screenshot to search in
            template_name: Name of template to find
            method: OpenCV template matching method
            overlap_threshold: Maximum allowed overlap between detections
            
        Returns:
            List of (region, confidence) tuples
        """
        # Load template if not already loaded
        if template_name not in self.templates:
            template = self.load_template(template_name)
            if template is None:
                return []
        
        template = self.templates[template_name]
        template_height, template_width = template.shape[:2]
        
        # Perform template matching
        result = cv2.matchTemplate(screenshot, template, method)
        
        # For TM_CCOEFF_NORMED, we want values above threshold
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            locations = np.where(result <= 1.0 - self.confidence_threshold)
            values = 1.0 - result[locations]
        else:
            locations = np.where(result >= self.confidence_threshold)
            values = result[locations]
        
        # Convert to list of (x, y, confidence)
        points = []
        for y, x, val in zip(locations[0], locations[1], values):
            points.append((x, y, val))
        
        # Group nearby detections
        detections = []
        points.sort(key=lambda p: p[2], reverse=True)  # Sort by confidence
        
        for x, y, confidence in points:
            region = (x, y, template_width, template_height)
            
            # Check if this region overlaps with existing detections
            overlap = False
            for existing_region, _ in detections:
                if self._regions_overlap(region, existing_region, overlap_threshold):
                    overlap = True
                    break
            
            if not overlap:
                detections.append((region, confidence))
        
        return detections
    
    def _regions_overlap(self, region1: Tuple[int, int, int, int], 
                        region2: Tuple[int, int, int, int],
                        threshold: float = 0.5) -> bool:
        """Check if two regions overlap above threshold."""
        x1, y1, w1, h1 = region1
        x2, y2, w2, h2 = region2
        
        # Calculate intersection
        x_left = max(x1, x2)
        y_top = max(y1, y2)
        x_right = min(x1 + w1, x2 + w2)
        y_bottom = min(y1 + h1, y2 + h2)
        
        if x_right <= x_left or y_bottom <= y_top:
            return False
        
        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        area1 = w1 * h1
        area2 = w2 * h2
        
        # Check if overlap exceeds threshold of either region
        overlap_ratio1 = intersection_area / area1
        overlap_ratio2 = intersection_area / area2
        
        return max(overlap_ratio1, overlap_ratio2) > threshold
    
    def wait_for_element(self, screenshot_func, template_name: str, 
                        timeout: float = 30.0, interval: float = 0.5,
                        **kwargs) -> Tuple[Optional[Tuple[int, int, int, int]], float]:
        """
        Wait for an element to appear on screen.
        
        Args:
            screenshot_func: Function that returns a screenshot
            template_name: Template to wait for
            timeout: Maximum time to wait (seconds)
            interval: Time between checks (seconds)
            **kwargs: Additional arguments for find_template
            
        Returns:
            Tuple of (region, confidence) or (None, 0.0) if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            screenshot = screenshot_func()
            region, confidence = self.find_template(screenshot, template_name, **kwargs)
            
            if region is not None:
                print(f"✅ Found {template_name} with confidence {confidence:.3f}")
                return region, confidence
            
            print(f"⏳ Waiting for {template_name}... ({time.time() - start_time:.1f}s)")
            time.sleep(interval)
        
        print(f"⏰ Timeout waiting for {template_name}")
        return None, 0.0
    
    def visualize_match(self, screenshot: np.ndarray, 
                       region: Tuple[int, int, int, int],
                       confidence: float,
                       template_name: str = "Element") -> np.ndarray:
        """
        Draw visualization of matched region on screenshot.
        
        Args:
            screenshot: Original screenshot
            region: Matched region (x, y, width, height)
            confidence: Match confidence
            template_name: Name of template for label
            
        Returns:
            Screenshot with visualization
        """
        result = screenshot.copy()
        x, y, w, h = region
        
        # Draw rectangle
        color = (0, 255, 0) if confidence > 0.9 else (0, 200, 255) if confidence > 0.8 else (0, 100, 255)
        thickness = 2
        cv2.rectangle(result, (x, y), (x + w, y + h), color, thickness)
        
        # Draw label background
        label = f"{template_name}: {confidence:.3f}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        text_size = cv2.getTextSize(label, font, font_scale, thickness)[0]
        
        # Background rectangle for text
        cv2.rectangle(result, (x, y - text_size[1] - 10), 
                     (x + text_size[0], y), color, -1)
        
        # Draw text
        cv2.putText(result, label, (x, y - 5), font, font_scale, 
                   (255, 255, 255), thickness)
        
        return result
    
    def save_template(self, image: np.ndarray, template_name: str):
        """
        Save an image as a template.
        
        Args:
            image: Image to save as template (BGR format)
            template_name: Name for the template
        """
        # Ensure template directory exists
        os.makedirs(self.template_dir, exist_ok=True)
        
        # Construct full path
        template_path = os.path.join(self.template_dir, f"{template_name}.png")
        
        # Save image
        cv2imwrite(template_path, image)
        print(f"💾 Saved template: {template_path} ({image.shape[1]}x{image.shape[0]})")
        
        # Reload into cache
        self.load_template(template_name)


# Quick test function
def test_image_locator():
    """Test the image locator."""
    print("🧪 Testing ImageLocator...")
    
    # Create a simple test template
    test_template = np.zeros((50, 100, 3), dtype=np.uint8)
    test_template[10:40, 20:80] = (0, 0, 255)  # Red rectangle
    
    # Create test directory
    test_dir = "test_templates/"
    os.makedirs(test_dir, exist_ok=True)
    cv2.imwrite(os.path.join(test_dir, "test_button.png"), test_template)
    
    # Initialize locator
    locator = ImageLocator(template_dir=test_dir, confidence_threshold=0.7)
    
    # Create a test screenshot with the template
    test_screenshot = np.zeros((200, 300, 3), dtype=np.uint8)
    test_screenshot[75:125, 50:150] = test_template  # Place template at (50, 75)
    
    # Test 1: Find template
    print("1. Finding template...")
    region, confidence = locator.find_template(test_screenshot, "test_button")
    
    if region:
        x, y, w, h = region
        print(f"   Found at: ({x}, {y}) {w}x{h}, confidence: {confidence:.3f}")
        
        # Test 2: Visualize
        print("2. Visualizing match...")
        visualized = locator.visualize_match(test_screenshot, region, confidence, "test_button")
        cv2.imwrite("test_visualized.png", visualized)
    else:
        print("   Template not found")
    
    # Test 3: Find all instances
    print("3. Finding all instances...")
    # Add another instance
    test_screenshot[30:80, 200:250] = test_template[:50, :50]  # Partial match
    
    instances = locator.find_all_instances(test_screenshot, "test_button")
    print(f"   Found {len(instances)} instances")
    
    # Cleanup
    import shutil
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    
    print("✅ ImageLocator tests completed!")


if __name__ == "__main__":
    test_image_locator()