"""
Input simulation module for visual automation.
Simulates mouse and keyboard input with human-like variations.
"""
import pyautogui
import pynput
from pynput import mouse, keyboard
import time
import random
import numpy as np
from typing import Tuple, Optional, Union, List
import math

class HumanizedInputSimulator:
    """Simulate human-like mouse and keyboard input."""
    
    def __init__(self, 
                 click_delay_range: Tuple[float, float] = (0.1, 0.3),
                 type_delay_range: Tuple[float, float] = (0.05, 0.15),
                 move_duration_range: Tuple[float, float] = (0.3, 0.8),
                 human_variance: bool = True):
        """
        Initialize input simulator.
        
        Args:
            click_delay_range: Range for delay between clicks (seconds)
            type_delay_range: Range for delay between keystrokes (seconds)
            move_duration_range: Range for mouse movement duration (seconds)
            human_variance: Whether to add human-like variations
        """
        self.click_delay_range = click_delay_range
        self.type_delay_range = type_delay_range
        self.move_duration_range = move_duration_range
        self.human_variance = human_variance
        
        # Safety feature - fail-safe point
        pyautogui.FAILSAFE = True
        
        # Initialize listeners for monitoring (optional)
        self.mouse_listener = None
        self.keyboard_listener = None
        
        print("🎮 Input simulator initialized")
    
    # ===== Mouse Operations =====
    
    def move_to(self, x: int, y: int, duration: Optional[float] = None):
        """
        Move mouse to coordinates with human-like motion.
        
        Args:
            x: Target X coordinate
            y: Target Y coordinate
            duration: Movement duration (seconds). If None, random within range.
        """
        if duration is None:
            duration = random.uniform(*self.move_duration_range)
        
        # Add small random offset for human-like imperfection
        if self.human_variance:
            offset_x = random.randint(-2, 2)
            offset_y = random.randint(-2, 2)
            x += offset_x
            y += offset_y
        
        # Use pyautogui's easeInOutQuad for natural movement
        pyautogui.moveTo(x, y, duration=duration, 
                        tween=pyautogui.easeInOutQuad)
        
        # Small pause at destination
        time.sleep(random.uniform(0.05, 0.15))
    
    def move_to_region(self, region: Tuple[int, int, int, int], 
                      offset_ratio: Tuple[float, float] = (0.5, 0.5)):
        """
        Move mouse to a region with offset ratio.
        
        Args:
            region: (x, y, width, height)
            offset_ratio: (x_ratio, y_ratio) where 0.0 is top/left, 1.0 is bottom/right
        """
        x, y, w, h = region
        target_x = x + int(w * offset_ratio[0])
        target_y = y + int(h * offset_ratio[1])
        
        self.move_to(target_x, target_y)
    
    def click(self, x: Optional[int] = None, y: Optional[int] = None, 
             button: str = 'left', clicks: int = 1, interval: Optional[float] = None):
        """
        Click at coordinates or current position.
        
        Args:
            x: X coordinate (None for current position)
            y: Y coordinate (None for current position)
            button: 'left', 'right', or 'middle'
            clicks: Number of clicks
            interval: Time between clicks (seconds)
        """
        # Move to position if coordinates provided
        if x is not None and y is not None:
            self.move_to(x, y)
        
        # Human-like pre-click hesitation
        if self.human_variance:
            time.sleep(random.uniform(0.05, 0.2))
        
        # Perform click(s)
        for i in range(clicks):
            pyautogui.click(button=button)
            
            # Add delay between multiple clicks
            if i < clicks - 1:
                if interval is None:
                    interval = random.uniform(*self.click_delay_range)
                time.sleep(interval)
        
        # Post-click pause
        if self.human_variance:
            time.sleep(random.uniform(0.1, 0.3))
    
    def click_region(self, region: Tuple[int, int, int, int], 
                    button: str = 'left', clicks: int = 1,
                    offset_ratio: Tuple[float, float] = (0.5, 0.5)):
        """
        Click within a region.
        
        Args:
            region: (x, y, width, height)
            button: Mouse button
            clicks: Number of clicks
            offset_ratio: Position within region to click
        """
        x, y, w, h = region
        target_x = x + int(w * offset_ratio[0])
        target_y = y + int(h * offset_ratio[1])
        
        self.click(target_x, target_y, button, clicks)
    
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int,
            duration: Optional[float] = None, button: str = 'left'):
        """
        Drag mouse from start to end position.
        
        Args:
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            end_x: Ending X coordinate
            end_y: Ending Y coordinate
            duration: Drag duration (seconds)
            button: Mouse button to hold
        """
        if duration is None:
            duration = random.uniform(0.5, 1.5)
        
        # Move to start position
        self.move_to(start_x, start_y)
        
        # Drag to end position
        pyautogui.dragTo(end_x, end_y, duration=duration, button=button)
    
    def scroll(self, clicks: int, direction: str = 'down'):
        """
        Scroll mouse wheel.
        
        Args:
            clicks: Number of scroll clicks
            direction: 'up' or 'down'
        """
        multiplier = 1 if direction == 'down' else -1
        
        # Human-like scrolling with variation
        for i in range(abs(clicks)):
            pyautogui.scroll(multiplier * random.randint(80, 120))
            
            if i < abs(clicks) - 1:
                time.sleep(random.uniform(0.05, 0.15))
    
    # ===== Keyboard Operations =====
    
    def type_text(self, text: str, delay_range: Optional[Tuple[float, float]] = None):
        """
        Type text with human-like timing and errors.
        
        Args:
            text: Text to type
            delay_range: Custom delay range between keystrokes
        """
        if delay_range is None:
            delay_range = self.type_delay_range
        
        # Simulate human typing patterns
        words = text.split()
        
        for word_idx, word in enumerate(words):
            # Type each character
            for char_idx, char in enumerate(word):
                # Small chance of typo and correction
                if (self.human_variance and random.random() < 0.01 and char_idx > 0):
                    # Type wrong character
                    wrong_char = random.choice('asdfghjkl;')
                    pyautogui.press(wrong_char)
                    time.sleep(random.uniform(0.1, 0.3))
                    
                    # Backspace and correct
                    pyautogui.press('backspace')
                    time.sleep(random.uniform(0.1, 0.2))
                
                # Type character
                pyautogui.write(char, interval=0)
                
                # Delay between characters
                time.sleep(random.uniform(*delay_range))
            
            # Delay between words
            if word_idx < len(words) - 1:
                pyautogui.write(' ', interval=0)
                time.sleep(random.uniform(0.1, 0.3))
    
    def press_keys(self, keys: Union[str, List[str]], 
                  delay_between: Optional[float] = None):
        """
        Press one or more keys.
        
        Args:
            keys: Single key string or list of keys
            delay_between: Delay between key presses
        """
        if isinstance(keys, str):
            keys = [keys]
        
        for i, key in enumerate(keys):
            pyautogui.press(key)
            
            if i < len(keys) - 1:
                if delay_between is None:
                    delay_between = random.uniform(0.05, 0.15)
                time.sleep(delay_between)
    
    def hotkey(self, *keys: str):
        """
        Press a hotkey combination.
        
        Args:
            *keys: Keys to press simultaneously
        """
        # Human-like hesitation before hotkey
        if self.human_variance:
            time.sleep(random.uniform(0.1, 0.3))
        
        pyautogui.hotkey(*keys)
        
        # Pause after hotkey
        if self.human_variance:
            time.sleep(random.uniform(0.2, 0.5))
    
    # ===== Advanced Operations =====
    
    def click_and_type(self, region: Tuple[int, int, int, int], text: str,
                      offset_ratio: Tuple[float, float] = (0.5, 0.5)):
        """
        Click on a region and type text.
        
        Args:
            region: Region to click
            text: Text to type
            offset_ratio: Click position within region
        """
        # Click to focus
        self.click_region(region, offset_ratio=offset_ratio)
        
        # Small pause for focus
        time.sleep(random.uniform(0.1, 0.3))
        
        # Type text
        self.type_text(text)
    
    def human_hesitation(self, min_delay: float = 0.2, max_delay: float = 0.8):
        """
        Simulate human hesitation/thinking time.
        
        Args:
            min_delay: Minimum hesitation time
            max_delay: Maximum hesitation time
        """
        if self.human_variance:
            time.sleep(random.uniform(min_delay, max_delay))
    
    # ===== Monitoring =====
    
    def start_monitoring(self):
        """Start monitoring mouse and keyboard input (for debugging)."""
        def on_move(x, y):
            print(f'Mouse moved to ({x}, {y})')
        
        def on_click(x, y, button, pressed):
            action = 'pressed' if pressed else 'released'
            print(f'Mouse {action} at ({x}, {y}) with {button}')
        
        def on_press(key):
            try:
                print(f'Key pressed: {key.char}')
            except AttributeError:
                print(f'Special key pressed: {key}')
        
        self.mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click)
        self.keyboard_listener = keyboard.Listener(on_press=on_press)
        
        self.mouse_listener.start()
        self.keyboard_listener.start()
        print("👀 Input monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring input."""
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        print("👀 Input monitoring stopped")


# Quick test function
def test_input_simulator():
    """Test the input simulator."""
    print("🧪 Testing HumanizedInputSimulator...")
    
    simulator = HumanizedInputSimulator(
        click_delay_range=(0.05, 0.1),
        type_delay_range=(0.02, 0.05),
        move_duration_range=(0.1, 0.3),
        human_variance=True
    )
    
    print("1. Getting current mouse position...")
    current_x, current_y = pyautogui.position()
    print(f"   Current position: ({current_x}, {current_y})")
    
    print("2. Testing mouse movement (small offset)...")
    # Move slightly from current position
    simulator.move_to(current_x + 50, current_y + 50)
    
    print("3. Testing click...")
    # Click at current position
    simulator.click()
    
    print("4. Testing keyboard input...")
    # Type a test message
    simulator.type_text("Hello, this is a test!")
    
    print("5. Testing hotkey...")
    # Simulate Ctrl+C (copy)
    simulator.hotkey('ctrl', 'c')
    
    print("✅ Input simulator tests completed!")
    print("⚠️  Note: These were minimal tests. Full tests would require visual verification.")


if __name__ == "__main__":
    test_input_simulator()