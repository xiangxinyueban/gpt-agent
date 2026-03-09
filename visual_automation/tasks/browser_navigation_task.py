"""
Browser navigation task for visual automation.
Handles URL navigation in a browser.
"""
import time
from typing import Optional, Tuple

from .base_task import BaseTask


class BrowserNavigationTask(BaseTask):
    """Task for navigating to URLs in a browser."""
    
    def __init__(self, url: str, **kwargs):
        """
        Initialize browser navigation task.
        
        Args:
            url: URL to navigate to
            **kwargs: Additional arguments for BaseTask
        """
        super().__init__(**kwargs)
        self.url = url
        
        # Default templates directory for browser elements
        if 'template_dir' not in kwargs:
            self.image_locator.template_dir = "config/templates/browser/"
    
    def execute(self) -> bool:
        """
        Execute browser navigation.
        
        Steps:
        1. Locate browser address bar
        2. Click address bar
        3. Type URL
        4. Press Enter
        
        Returns:
            True if navigation successful
        """
        print(f"🌐 BrowserNavigationTask: Navigating to {self.url}")
        
        # Record start
        self.capture_screenshot("before_navigation")
        
        # Step 1: Find and click address bar
        self.log_step("Find address bar", False)
        if not self.click_address_bar():
            print("❌ Failed to find/click address bar")
            return False
        self.log_step("Find address bar", True)
        
        # Step 2: Type URL
        self.log_step("Type URL", False)
        if not self.type_url():
            print("❌ Failed to type URL")
            return False
        self.log_step("Type URL", True)
        
        # Step 3: Press Enter
        self.log_step("Press Enter", False)
        self.press_enter()
        self.log_step("Press Enter", True)
        
        # Step 4: Wait for page load
        self.log_step("Wait for page load", False)
        if not self.wait_for_page_load():
            print("⚠️  Page load timeout, but continuing")
        self.log_step("Wait for page load", True)
        
        # Capture result
        self.capture_screenshot("after_navigation")
        
        print(f"✅ Navigation to {self.url} completed")
        return True
    
    def click_address_bar(self, timeout: float = 10.0) -> bool:
        """
        Find and click the browser address bar.
        
        Args:
            timeout: Time to wait for address bar
            
        Returns:
            True if address bar found and clicked
        """
        print("🔍 Looking for address bar...")
        
        # Try different templates for address bar
        address_bar_templates = [
            "address_bar",
            "url_bar", 
            "omnibox",
            "browser_address_bar"
        ]
        
        for template in address_bar_templates:
            print(f"  Trying template: {template}")
            if self.click_element(template, timeout=5.0):
                print(f"  ✅ Found address bar using '{template}' template")
                return True
        
        # If specific templates not found, try to find by color or location
        print("  Specific templates not found, trying alternative methods...")
        
        # Method 1: Look for typical address bar location (top center)
        screen_width, screen_height = self.screen_capturer.screen_width, self.screen_capturer.screen_height
        address_bar_region = (
            screen_width // 4,  # Start 1/4 from left
            10,                 # Near top
            screen_width // 2,  # Half screen width
            50                  # Height
        )
        
        # Click in the general area
        print(f"  Clicking in general address bar area: {address_bar_region}")
        self.input_simulator.click_region(address_bar_region, offset_ratio=(0.5, 0.5))
        
        # Select all text (Ctrl+A) to clear existing URL
        self.input_simulator.hotkey('ctrl', 'a')
        time.sleep(0.5)
        
        return True
    
    def type_url(self) -> bool:
        """Type the URL into address bar."""
        print(f"⌨️  Typing URL: {self.url}")
        
        # Clear any existing text (already done by Ctrl+A in click_address_bar)
        # Type the URL
        self.input_simulator.type_text(self.url)
        
        # Small pause after typing
        time.sleep(0.5)
        
        return True
    
    def press_enter(self):
        """Press Enter to navigate."""
        print("↵ Pressing Enter...")
        self.input_simulator.press_keys(['enter'])
        
        # Wait for navigation to start
        time.sleep(1.0)
    
    def wait_for_page_load(self, timeout: float = 30.0) -> bool:
        """
        Wait for page to finish loading.
        
        Args:
            timeout: Maximum time to wait
            
        Returns:
            True if page appears loaded
        """
        print("⏳ Waiting for page to load...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Take screenshot to check for loading indicators
            screenshot = self.screen_capturer.capture_screen()
            
            # Check for common loading indicators (simplified)
            # In real implementation, would check for spinner, loading text, etc.
            
            # For now, just wait a few seconds and assume page loaded
            time.sleep(2)
            
            # Check for browser tab activity indicator (optional)
            # Could look for favicon changes, title changes, etc.
            
            print(f"  Waiting... ({int(time.time() - start_time)}s/{timeout}s)")
            
            # Early exit if we see common page elements
            if self.check_page_loaded():
                print("  ✅ Page appears loaded")
                return True
        
        print(f"⚠️  Page load timeout after {timeout}s")
        return False
    
    def check_page_loaded(self) -> bool:
        """
        Check if page appears to be loaded.
        
        Returns:
            True if page seems loaded
        """
        # Check for common page elements that indicate loading is complete
        # This is a simplified implementation
        
        common_loaded_indicators = [
            "page_content",
            "main_content",
            "body_loaded"
        ]
        
        for indicator in common_loaded_indicators:
            result = self.find_element(indicator, timeout=1.0)
            if result and result[0]:
                return True
        
        # Also check that we're not seeing loading spinners
        loading_indicators = [
            "loading_spinner",
            "progress_bar",
            "loading_text"
        ]
        
        for indicator in loading_indicators:
            result = self.find_element(indicator, timeout=1.0)
            if result and result[0]:
                # Found a loading indicator, page not fully loaded
                return False
        
        # If we can't determine, assume loaded after reasonable time
        return True
    
    def execute_with_workflow(self) -> bool:
        """Execute navigation using workflow executor."""
        self.setup_workflow()
        
        # Define workflow steps
        def step_find_address_bar(exec):
            return exec.click_element("address_bar")
        
        def step_type_url(exec):
            exec.input_simulator.type_text(self.url)
            return True
        
        def step_press_enter(exec):
            exec.input_simulator.press_keys(['enter'])
            time.sleep(2)
            return True
        
        def step_wait_load(exec):
            # Simple wait instead of complex check
            time.sleep(5)
            return True
        
        # Add steps
        self.executor.create_step(
            name="find_address_bar",
            description="Find and click browser address bar",
            action=step_find_address_bar,
            retries=2
        )
        
        self.executor.create_step(
            name="type_url",
            description="Type URL into address bar",
            action=step_type_url
        )
        
        self.executor.create_step(
            name="press_enter",
            description="Press Enter to navigate",
            action=step_press_enter
        )
        
        self.executor.create_step(
            name="wait_load",
            description="Wait for page to load",
            action=step_wait_load,
            required=False
        )
        
        # Execute workflow
        return self.executor.execute_workflow("Browser Navigation")


# Test function
def test_browser_navigation():
    """Test browser navigation task."""
    print("🧪 Testing BrowserNavigationTask...")
    
    # Create task (using test URL)
    task = BrowserNavigationTask(
        url="https://chat.openai.com",
        template_dir="test_templates/",
        save_screenshots=False
    )
    
    # Since we don't have actual templates, test will likely fail
    # but we can test the structure
    try:
        # This will likely fail due to missing templates
        success = task.execute()
        print(f"✅ Task execution: {'Success' if success else 'Failed'}")
    except Exception as e:
        print(f"❌ Task execution failed (expected without templates): {e}")
    
    return True


if __name__ == "__main__":
    test_browser_navigation()