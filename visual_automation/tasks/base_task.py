"""
Base task class for visual automation tasks.
All specific tasks should inherit from this class.
"""
import time
from typing import Dict, Optional, Tuple, Any
from abc import ABC, abstractmethod

from ..core.screen_capturer import ScreenCapturer
from ..core.image_locator import ImageLocator
from ..core.input_simulator import HumanizedInputSimulator
from ..core.workflow_executor import WorkflowExecutor


class BaseTask(ABC):
    """Base class for all visual automation tasks."""
    
    def __init__(self, 
                 template_dir: str = "config/templates/",
                 confidence_threshold: float = 0.85,
                 save_screenshots: bool = True):
        """
        Initialize base task.
        
        Args:
            template_dir: Directory containing template images
            confidence_threshold: Minimum confidence for image matching
            save_screenshots: Whether to save screenshots during execution
        """
        self.screen_capturer = ScreenCapturer()
        self.image_locator = ImageLocator(template_dir, confidence_threshold)
        self.input_simulator = HumanizedInputSimulator()
        self.save_screenshots = save_screenshots
        
        # Task state
        self.executor: Optional[WorkflowExecutor] = None
        self.context: Dict[str, Any] = {}
        
        print(f"📋 {self.__class__.__name__} initialized")
    
    @abstractmethod
    def execute(self) -> bool:
        """
        Execute the main task logic.
        
        Returns:
            True if task completed successfully
        """
        pass
    
    def setup_workflow(self) -> WorkflowExecutor:
        """Setup workflow executor for this task."""
        self.executor = WorkflowExecutor(
            template_dir=self.image_locator.template_dir,
            confidence_threshold=self.image_locator.confidence_threshold,
            save_screenshots=self.save_screenshots
        )
        return self.executor
    
    def capture_screenshot(self, name: str) -> str:
        """
        Capture and save a screenshot.
        
        Args:
            name: Name for the screenshot
            
        Returns:
            Path to saved screenshot
        """
        if not self.save_screenshots:
            return ""
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/{self.__class__.__name__}_{name}_{timestamp}.png"
        
        self.screen_capturer.capture_screen(save_path=filename)
        
        # Add to context
        if 'screenshots' not in self.context:
            self.context['screenshots'] = []
        self.context['screenshots'].append(filename)
        
        return filename
    
    def find_element(self, template_name: str, timeout: float = 10.0) -> Optional[Tuple[Tuple[int, int, int, int], float]]:
        """
        Find an element on screen.
        
        Args:
            template_name: Name of template to find
            timeout: Maximum time to wait
            
        Returns:
            (region, confidence) or None
        """
        def get_screenshot():
            return self.screen_capturer.capture_screen()
        
        return self.image_locator.wait_for_element(get_screenshot, template_name, timeout)
    
    def click_element(self, template_name: str, 
                     offset_ratio: Tuple[float, float] = (0.5, 0.5),
                     timeout: float = 10.0) -> bool:
        """
        Find and click an element.
        
        Args:
            template_name: Template to find and click
            offset_ratio: Where to click within element
            timeout: Time to wait for element
            
        Returns:
            True if clicked successfully
        """
        result = self.find_element(template_name, timeout)
        
        if result is None or result[0] is None:
            print(f"❌ Could not find element '{template_name}' to click")
            return False
        
        region, confidence = result
        print(f"  🖱️  Clicking '{template_name}' at confidence {confidence:.3f}")
        
        self.input_simulator.click_region(region, offset_ratio=offset_ratio)
        return True
    
    def type_into_element(self, template_name: str, text: str,
                         offset_ratio: Tuple[float, float] = (0.5, 0.5),
                         timeout: float = 10.0) -> bool:
        """
        Find an element, click it, and type text.
        
        Args:
            template_name: Template to find (e.g., input field)
            text: Text to type
            offset_ratio: Where to click within element
            timeout: Time to wait for element
            
        Returns:
            True if successfully typed
        """
        result = self.find_element(template_name, timeout)
        
        if result is None or result[0] is None:
            print(f"❌ Could not find element '{template_name}' to type into")
            return False
        
        region, confidence = result
        print(f"  ⌨️  Typing into '{template_name}' at confidence {confidence:.3f}")
        
        self.input_simulator.click_and_type(region, text, offset_ratio)
        return True
    
    def wait_for_element(self, template_name: str, timeout: float = 30.0) -> bool:
        """
        Wait for an element to appear on screen.
        
        Args:
            template_name: Template to wait for
            timeout: Maximum time to wait
            
        Returns:
            True if element appeared within timeout
        """
        print(f"⏳ Waiting for '{template_name}'...")
        result = self.find_element(template_name, timeout)
        
        if result and result[0]:
            print(f"✅ '{template_name}' appeared")
            return True
        else:
            print(f"❌ '{template_name}' did not appear within {timeout}s")
            return False
    
    def human_hesitation(self, min_delay: float = 0.5, max_delay: float = 2.0):
        """Simulate human hesitation/thinking time."""
        delay = time.uniform(min_delay, max_delay)
        print(f"🤔 Simulating human hesitation ({delay:.1f}s)...")
        time.sleep(delay)
    
    def log_step(self, step_name: str, success: bool, details: str = ""):
        """Log a step execution."""
        status = "✅" if success else "❌"
        print(f"{status} Step: {step_name}")
        if details:
            print(f"   Details: {details}")
        
        # Add to context
        if 'steps' not in self.context:
            self.context['steps'] = []
        
        self.context['steps'].append({
            'name': step_name,
            'success': success,
            'timestamp': time.time(),
            'details': details
        })
    
    def get_summary(self) -> Dict[str, Any]:
        """Get task execution summary."""
        summary = {
            'task_name': self.__class__.__name__,
            'context': self.context,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'screenshot_count': len(self.context.get('screenshots', [])),
            'step_count': len(self.context.get('steps', [])),
            'successful_steps': sum(1 for step in self.context.get('steps', []) if step['success']),
            'failed_steps': sum(1 for step in self.context.get('steps', []) if not step['success'])
        }
        return summary