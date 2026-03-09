"""
Screen capture module for visual automation.
Handles taking screenshots of the screen or specific regions.
"""
import pyautogui
import cv2
import numpy as np
from PIL import Image
import time
import os
from typing import Tuple, Optional, Union

class ScreenCapturer:
    """Capture screenshots for visual automation."""
    
    def __init__(self, monitor: int = 0, region: Optional[Tuple[int, int, int, int]] = None):
        """
        Initialize screen capturer.
        
        Args:
            monitor: Monitor number (0 for primary)
            region: Optional region to capture (x, y, width, height)
        """
        self.monitor = monitor
        self.region = region
        
        # Get screen size
        self.screen_width, self.screen_height = pyautogui.size()
        print(f"📺 Screen size: {self.screen_width}x{self.screen_height}")
    
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None, 
                      save_path: Optional[str] = None) -> np.ndarray:
        """
        Capture screenshot of the entire screen or a region.
        
        Args:
            region: Optional region (x, y, width, height)
            save_path: Optional path to save screenshot
            
        Returns:
            Screenshot as numpy array (BGR format for OpenCV)
        """
        try:
            # Use provided region or instance region or full screen
            capture_region = region or self.region
            
            # Take screenshot
            screenshot = pyautogui.screenshot(region=capture_region)
            
            # Convert PIL Image to numpy array (BGR for OpenCV)
            screenshot_np = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Save if requested
            if save_path:
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                cv2.imwrite(save_path, screenshot_np)
                print(f"💾 Screenshot saved to: {save_path}")
            
            return screenshot_np
            
        except Exception as e:
            print(f"❌ Failed to capture screen: {e}")
            raise
    
    def capture_and_show(self, region: Optional[Tuple[int, int, int, int]] = None, 
                        window_name: str = "Screenshot"):
        """
        Capture screen and display it (for debugging).
        
        Args:
            region: Optional region to capture
            window_name: Window name for display
        """
        screenshot = self.capture_screen(region)
        
        # Display the screenshot
        cv2.imshow(window_name, screenshot)
        print("🖼️  Press any key to close the window...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    def capture_multiple(self, count: int = 3, interval: float = 1.0,
                        save_dir: str = "screenshots/captures/") -> list:
        """
        Capture multiple screenshots at intervals.
        
        Args:
            count: Number of screenshots to take
            interval: Time between captures (seconds)
            save_dir: Directory to save screenshots
            
        Returns:
            List of screenshot arrays
        """
        screenshots = []
        os.makedirs(save_dir, exist_ok=True)
        
        for i in range(count):
            print(f"📸 Capture {i+1}/{count}...")
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(save_dir, f"capture_{timestamp}_{i}.png")
            
            screenshot = self.capture_screen(save_path=save_path)
            screenshots.append(screenshot)
            
            if i < count - 1:
                time.sleep(interval)
        
        return screenshots
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """
        Get current mouse position.
        
        Returns:
            (x, y) coordinates
        """
        return pyautogui.position()
    
    def highlight_region(self, region: Tuple[int, int, int, int], 
                        color: Tuple[int, int, int] = (0, 255, 0),
                        thickness: int = 2) -> np.ndarray:
        """
        Capture screen and highlight a specific region.
        
        Args:
            region: Region to highlight (x, y, width, height)
            color: BGR color tuple
            thickness: Line thickness
            
        Returns:
            Screenshot with highlighted region
        """
        screenshot = self.capture_screen()
        
        # Draw rectangle
        x, y, w, h = region
        cv2.rectangle(screenshot, (x, y), (x + w, y + h), color, thickness)
        
        # Add label
        label = f"Region: ({x}, {y}) {w}x{h}"
        cv2.putText(screenshot, label, (x, y - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)
        
        return screenshot
    
    def find_color_region(self, color_bgr: Tuple[int, int, int], 
                         tolerance: int = 10) -> Optional[Tuple[int, int, int, int]]:
        """
        Find region containing a specific color.
        
        Args:
            color_bgr: Target color in BGR format
            tolerance: Color tolerance
            
        Returns:
            Bounding box (x, y, width, height) or None
        """
        screenshot = self.capture_screen()
        
        # Create mask for target color
        lower = np.array([max(0, c - tolerance) for c in color_bgr])
        upper = np.array([min(255, c + tolerance) for c in color_bgr])
        mask = cv2.inRange(screenshot, lower, upper)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Get bounding box of largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            return (x, y, w, h)
        
        return None


# Quick test function
def test_screen_capturer():
    """Test the screen capturer."""
    print("🧪 Testing ScreenCapturer...")
    
    capturer = ScreenCapturer()
    
    # Test 1: Full screen capture
    print("1. Capturing full screen...")
    full_screen = capturer.capture_screen(save_path="test_fullscreen.png")
    print(f"   Captured: {full_screen.shape[1]}x{full_screen.shape[0]}")
    
    # Test 2: Region capture
    print("2. Capturing region (100, 100, 300, 200)...")
    region = (100, 100, 300, 200)
    region_screen = capturer.capture_screen(region=region, save_path="test_region.png")
    print(f"   Captured region: {region_screen.shape[1]}x{region_screen.shape[0]}")
    
    # Test 3: Mouse position
    print("3. Getting mouse position...")
    x, y = capturer.get_mouse_position()
    print(f"   Mouse at: ({x}, {y})")
    
    # Test 4: Highlight region
    print("4. Highlighting region...")
    highlighted = capturer.highlight_region((200, 200, 100, 50))
    cv2.imwrite("test_highlighted.png", highlighted)
    
    print("✅ ScreenCapturer tests completed!")


if __name__ == "__main__":
    test_screen_capturer()