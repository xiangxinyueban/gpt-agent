"""
Workflow executor for visual automation.
Coordinates screen capture, image recognition, and input simulation.
"""
import time
import json
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum

from .screen_capturer import ScreenCapturer
from .image_locator import ImageLocator
from .input_simulator import HumanizedInputSimulator


class StepStatus(Enum):
    """Status of a workflow step."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """Represents a single step in a workflow."""
    name: str
    description: str
    action: Callable  # Function to execute
    timeout: float = 30.0
    retries: int = 3
    required: bool = True
    status: StepStatus = field(default=StepStatus.PENDING)
    result: Optional[dict] = None
    error: Optional[str] = None


@dataclass
class WorkflowContext:
    """Context data passed between workflow steps."""
    data: Dict = field(default_factory=dict)
    screenshots: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)


class WorkflowExecutor:
    """Execute visual automation workflows."""
    
    def __init__(self, 
                 template_dir: str = "config/templates/chatgpt/",
                 confidence_threshold: float = 0.85,
                 save_screenshots: bool = True):
        """
        Initialize workflow executor.
        
        Args:
            template_dir: Directory for template images
            confidence_threshold: Minimum confidence for image matching
            save_screenshots: Whether to save screenshots during execution
        """
        self.screen_capturer = ScreenCapturer()
        self.image_locator = ImageLocator(template_dir, confidence_threshold)
        self.input_simulator = HumanizedInputSimulator()
        self.save_screenshots = save_screenshots
        
        # Workflow state
        self.current_step: Optional[WorkflowStep] = None
        self.context: Optional[WorkflowContext] = None
        self.steps: List[WorkflowStep] = []
        
        print("🔄 Workflow executor initialized")
    
    def add_step(self, step: WorkflowStep):
        """Add a step to the workflow."""
        self.steps.append(step)
    
    def create_step(self, name: str, description: str, action: Callable,
                   timeout: float = 30.0, retries: int = 3, required: bool = True) -> WorkflowStep:
        """Create and add a workflow step."""
        step = WorkflowStep(
            name=name,
            description=description,
            action=action,
            timeout=timeout,
            retries=retries,
            required=required
        )
        self.add_step(step)
        return step
    
    def execute_workflow(self, workflow_name: str) -> bool:
        """
        Execute the entire workflow.
        
        Args:
            workflow_name: Name of the workflow for logging
            
        Returns:
            True if all required steps succeeded, False otherwise
        """
        print(f"🚀 Starting workflow: {workflow_name}")
        print(f"📋 Steps to execute: {len(self.steps)}")
        
        # Initialize context
        self.context = WorkflowContext()
        self.context.data['workflow_name'] = workflow_name
        self.context.data['start_time'] = time.time()
        
        success_count = 0
        failed_count = 0
        skipped_count = 0
        
        for i, step in enumerate(self.steps):
            self.current_step = step
            step_num = i + 1
            
            print(f"\n{'='*60}")
            print(f"Step {step_num}/{len(self.steps)}: {step.name}")
            print(f"Description: {step.description}")
            print(f"{'='*60}")
            
            # Check if previous required step failed
            if step.required and i > 0:
                prev_step = self.steps[i - 1]
                if prev_step.required and prev_step.status == StepStatus.FAILED:
                    step.status = StepStatus.SKIPPED
                    step.error = f"Skipped because previous required step '{prev_step.name}' failed"
                    skipped_count += 1
                    print(f"⏭️  Skipped: {step.error}")
                    continue
            
            # Execute step with retries
            step.status = StepStatus.RUNNING
            step_success = False
            
            for attempt in range(step.retries):
                try:
                    print(f"  Attempt {attempt + 1}/{step.retries}...")
                    
                    # Execute the step action
                    result = step.action(self)  # Pass executor instance
                    
                    step.status = StepStatus.SUCCESS
                    step.result = result if isinstance(result, dict) else {'result': result}
                    step_success = True
                    
                    print(f"  ✅ {step.name} completed successfully")
                    break
                    
                except Exception as e:
                    step.error = str(e)
                    print(f"  ❌ Attempt {attempt + 1} failed: {e}")
                    
                    if attempt < step.retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff
                        print(f"  ⏳ Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
            
            if step_success:
                success_count += 1
            else:
                step.status = StepStatus.FAILED
                failed_count += 1
                print(f"  ❌ {step.name} failed after {step.retries} attempts")
                
                # If this is a required step, we might want to stop
                if step.required:
                    print(f"  ⚠️  Required step failed, workflow may be incomplete")
        
        # Final summary
        print(f"\n{'='*60}")
        print(f"Workflow '{workflow_name}' completed")
        print(f"⏱️  Duration: {time.time() - self.context.data['start_time']:.1f}s")
        print(f"✅ Success: {success_count}")
        print(f"❌ Failed: {failed_count}")
        print(f"⏭️  Skipped: {skipped_count}")
        
        # Check overall success
        all_required_success = all(
            step.status == StepStatus.SUCCESS or not step.required
            for step in self.steps
        )
        
        if all_required_success:
            print(f"🎉 Workflow completed successfully!")
        else:
            print(f"⚠️  Workflow completed with failures")
        
        return all_required_success
    
    def capture_step_screenshot(self, step_name: str) -> str:
        """
        Capture and save a screenshot for the current step.
        
        Args:
            step_name: Name of the step for filename
            
        Returns:
            Path to saved screenshot
        """
        if not self.save_screenshots:
            return ""
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/{step_name}_{timestamp}.png"
        
        screenshot = self.screen_capturer.capture_screen(save_path=filename)
        self.context.screenshots.append(filename)
        
        return filename
    
    def find_element(self, template_name: str, 
                    timeout: float = 10.0,
                    save_match_image: bool = True) -> Optional[Tuple[Tuple[int, int, int, int], float]]:
        """
        Find an element on screen with timeout.
        
        Args:
            template_name: Name of template to find
            timeout: Maximum time to wait
            save_match_image: Whether to save visualization
            
        Returns:
            (region, confidence) or None
        """
        print(f"🔍 Looking for '{template_name}'...")
        
        def get_screenshot():
            return self.screen_capturer.capture_screen()
        
        region, confidence = self.image_locator.wait_for_element(
            get_screenshot, template_name, timeout=timeout
        )
        
        if region and save_match_image:
            # Capture and visualize match
            screenshot = get_screenshot()
            visualized = self.image_locator.visualize_match(
                screenshot, region, confidence, template_name
            )
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshots/match_{template_name}_{timestamp}.png"
            import cv2
            cv2.imwrite(filename, visualized)
            print(f"  💾 Saved match visualization: {filename}")
        
        return region, confidence
    
    def click_element(self, template_name: str, 
                     offset_ratio: Tuple[float, float] = (0.5, 0.5),
                     timeout: float = 10.0) -> bool:
        """
        Find and click an element.
        
        Args:
            template_name: Template to find and click
            offset_ratio: Where to click within the element
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


# Example workflow steps
def example_workflow_steps(executor: WorkflowExecutor):
    """Create example workflow steps for testing."""
    
    def step_initial_screenshot(exec):
        """Take initial screenshot."""
        filename = exec.capture_step_screenshot("initial")
        return {"screenshot": filename}
    
    def step_find_and_click_button(exec):
        """Find and click a button."""
        success = exec.click_element("login_button", timeout=15.0)
        if not success:
            raise Exception("Login button not found")
        return {"clicked": True}
    
    def step_type_credentials(exec):
        """Type username and password."""
        # First find and click username field
        exec.click_element("username_field")
        exec.input_simulator.type_text("test_user")
        
        # Tab to password field (or find it)
        exec.input_simulator.press_keys(['tab'])
        exec.input_simulator.type_text("test_password")
        
        return {"typed_credentials": True}
    
    def step_submit_login(exec):
        """Submit login form."""
        success = exec.click_element("submit_button")
        if not success:
            raise Exception("Submit button not found")
        
        # Wait for login to complete
        time.sleep(3)
        return {"submitted": True}
    
    def step_verify_login_success(exec):
        """Verify login was successful."""
        # Look for element that indicates successful login
        result = exec.find_element("user_avatar", timeout=10.0)
        if result[0] is None:
            raise Exception("Login verification failed - user avatar not found")
        
        filename = exec.capture_step_screenshot("login_success")
        return {"verified": True, "screenshot": filename}
    
    # Add steps to executor
    executor.create_step(
        name="initial_screenshot",
        description="Capture initial screen state",
        action=step_initial_screenshot
    )
    
    executor.create_step(
        name="click_login_button",
        description="Find and click login button",
        action=step_find_and_click_button,
        retries=2
    )
    
    executor.create_step(
        name="enter_credentials",
        description="Type username and password",
        action=step_type_credentials
    )
    
    executor.create_step(
        name="submit_login",
        description="Submit login form",
        action=step_submit_login
    )
    
    executor.create_step(
        name="verify_login",
        description="Verify login was successful",
        action=step_verify_login_success,
        required=False  # Optional step
    )


# Test function
def test_workflow_executor():
    """Test the workflow executor."""
    print("🧪 Testing WorkflowExecutor...")
    
    # Create executor
    executor = WorkflowExecutor(
        template_dir="test_templates/",
        confidence_threshold=0.7,
        save_screenshots=False  # Don't save during test
    )
    
    # Create test directory
    import os
    os.makedirs("test_templates", exist_ok=True)
    
    # Add example steps (simplified for test)
    def test_step(exec):
        print("  Test step executed")
        return {"test": "success"}
    
    executor.create_step(
        name="test_step",
        description="Test step",
        action=test_step
    )
    
    # Execute workflow
    success = executor.execute_workflow("Test Workflow")
    
    # Cleanup
    import shutil
    if os.path.exists("test_templates"):
        shutil.rmtree("test_templates")
    
    print(f"✅ WorkflowExecutor test completed: {'Success' if success else 'Failed'}")
    return success


if __name__ == "__main__":
    test_workflow_executor()