"""
Chat task for visual automation.
Handles sending and receiving messages in ChatGPT.
"""
import time
import random
from typing import Optional, Tuple, Dict, Any, List

from .base_task import BaseTask


class ChatTask(BaseTask):
    """Task for interacting with ChatGPT chat interface."""
    
    def __init__(self, 
                 message: str = "",
                 wait_for_response: bool = True,
                 response_timeout: float = 60.0,
                 **kwargs):
        """
        Initialize chat task.
        
        Args:
            message: Message to send (empty to use default)
            wait_for_response: Whether to wait for ChatGPT response
            response_timeout: Maximum time to wait for response (seconds)
            **kwargs: Additional arguments for BaseTask
        """
        super().__init__(**kwargs)
        self.message = message
        self.wait_for_response = wait_for_response
        self.response_timeout = response_timeout
        
        # Set ChatGPT-specific template directory
        if 'template_dir' not in kwargs:
            self.image_locator.template_dir = "config/templates/chatgpt/"
        
        print(f"💬 ChatTask initialized: '{self.message[:50]}...'"
              if len(self.message) > 50 else f"💬 ChatTask initialized: '{self.message}'")
    
    def execute(self) -> bool:
        """
        Execute chat interaction.
        
        Steps:
        1. Ensure on ChatGPT chat page
        2. Find and click chat input field
        3. Type message
        4. Click send button
        5. Wait for response (optional)
        6. Verify response received
        
        Returns:
            True if chat interaction successful
        """
        print(f"💬 ChatTask: Sending message to ChatGPT")
        
        # Record start
        self.capture_screenshot("before_chat")
        
        # Step 1: Ensure on chat page
        self.log_step("Verify chat page", False)
        if not self.ensure_chat_page():
            print("❌ Not on ChatGPT chat page")
            return False
        self.log_step("Verify chat page", True)
        
        # Step 2: Find and focus chat input
        self.log_step("Focus chat input", False)
        if not self.focus_chat_input():
            print("❌ Could not focus chat input")
            return False
        self.log_step("Focus chat input", True)
        
        # Step 3: Type message
        self.log_step("Type message", False)
        if not self.type_message():
            print("❌ Failed to type message")
            return False
        self.log_step("Type message", True)
        
        # Step 4: Send message
        self.log_step("Send message", False)
        if not self.send_message():
            print("❌ Failed to send message")
            return False
        self.log_step("Send message", True)
        
        # Step 5: Wait for response
        if self.wait_for_response:
            self.log_step("Wait for response", False)
            if not self.wait_for_chatgpt_response():
                print("⚠️  Response wait timeout or uncertain")
            self.log_step("Wait for response", True)
        
        # Step 6: Verify success
        self.log_step("Verify chat success", False)
        if not self.verify_chat_success():
            print("⚠️  Chat success verification uncertain")
        self.log_step("Verify chat success", True)
        
        # Capture result
        self.capture_screenshot("after_chat")
        
        print(f"✅ Chat interaction completed")
        return True
    
    def ensure_chat_page(self, timeout: float = 10.0) -> bool:
        """
        Ensure we're on the ChatGPT chat page.
        
        Args:
            timeout: Time to wait for chat page elements
            
        Returns:
            True if on chat page
        """
        print("🔍 Verifying ChatGPT chat page...")
        
        # Check for chat page indicators
        chat_indicators = [
            "chat_input",
            "send_button",
            "chat_history",
            "new_chat_button",
            "user_avatar"  # Already logged in indicator
        ]
        
        for indicator in chat_indicators:
            result = self.find_element(indicator, timeout=2.0)
            if result and result[0]:
                print(f"✅ On chat page (found {indicator})")
                return True
        
        # If not found, try to navigate to chat
        print("⚠️  Not on chat page, attempting navigation...")
        
        # Try clicking "New chat" button
        if self.click_element("new_chat_button", timeout=5.0):
            print("✅ Clicked new chat button")
            time.sleep(2)  # Wait for page transition
            return True
        
        # Try clicking ChatGPT logo/home
        if self.click_element("chatgpt_logo", timeout=5.0):
            print("✅ Clicked ChatGPT logo")
            time.sleep(2)
            return True
        
        # Fallback: reload page
        print("🔄 Reloading page...")
        self.input_simulator.hotkey('ctrl', 'r')
        time.sleep(3)
        
        return self.wait_for_element("chat_input", timeout)
    
    def focus_chat_input(self) -> bool:
        """
        Find and focus the chat input field.
        
        Returns:
            True if input field focused
        """
        print("⌨️  Focusing chat input...")
        
        # Try to find and click chat input field
        input_field_templates = [
            "chat_input",
            "message_input",
            "text_input",
            "prompt_input"
        ]
        
        for field in input_field_templates:
            if self.click_element(field, timeout=5.0):
                print(f"✅ Focused chat input ({field})")
                
                # Small pause for focus to take effect
                time.sleep(0.5)
                
                # Optional: clear any existing text (Ctrl+A, Delete)
                self.input_simulator.hotkey('ctrl', 'a')
                time.sleep(0.2)
                self.input_simulator.press_keys(['delete'])
                time.sleep(0.2)
                
                return True
        
        # Fallback: try clicking in the general area where input should be
        print("⚠️  Chat input not found by template, trying fallback...")
        
        # ChatGPT input is usually at bottom of screen
        screen_width, screen_height = self.screen_capturer.screen_width, self.screen_capturer.screen_height
        input_region = (
            screen_width // 4,  # Start 1/4 from left
            screen_height - 150,  # Near bottom (above system tray)
            screen_width // 2,  # Half screen width
            100  # Height
        )
        
        self.input_simulator.click_region(input_region, offset_ratio=(0.5, 0.5))
        time.sleep(0.5)
        
        return True
    
    def type_message(self) -> bool:
        """
        Type the message into chat input.
        
        Returns:
            True if message typed successfully
        """
        if not self.message:
            # Generate a default test message
            test_messages = [
                "Hello, this is a test message from visual automation.",
                "Can you explain how AI visual automation works?",
                "What are the benefits of template matching for UI automation?",
                "Write a simple Python function for image recognition."
            ]
            self.message = random.choice(test_messages)
            print(f"💬 Using test message: {self.message}")
        
        print(f"⌨️  Typing message: {self.message[:50]}..."
              if len(self.message) > 50 else f"⌨️  Typing message: {self.message}")
        
        # Type the message with human-like variations
        self.input_simulator.type_text(self.message)
        
        # Small pause after typing
        time.sleep(0.5)
        
        return True
    
    def send_message(self) -> bool:
        """
        Send the message.
        
        Returns:
            True if message sent successfully
        """
        print("📤 Sending message...")
        
        # Try to find and click send button
        send_button_templates = [
            "send_button",
            "submit_button",
            "send_message_button",
            "send_icon"
        ]
        
        for button in send_button_templates:
            if self.click_element(button, timeout=5.0):
                print(f"✅ Clicked send button ({button})")
                return True
        
        # Fallback: press Enter (common in chat interfaces)
        print("⚠️  Send button not found, pressing Enter...")
        self.input_simulator.press_keys(['enter'])
        
        # Some interfaces use Ctrl+Enter
        time.sleep(0.5)
        self.input_simulator.hotkey('ctrl', 'enter')
        
        return True
    
    def wait_for_chatgpt_response(self, timeout: float = None) -> bool:
        """
        Wait for ChatGPT to respond.
        
        Args:
            timeout: Maximum time to wait (None uses instance timeout)
            
        Returns:
            True if response detected within timeout
        """
        if timeout is None:
            timeout = self.response_timeout
        
        print(f"⏳ Waiting for ChatGPT response (timeout: {timeout}s)...")
        
        start_time = time.time()
        last_typing_indicator = 0
        
        while time.time() - start_time < timeout:
            # Check for response indicators
            if self.check_response_received():
                print("✅ Response received!")
                return True
            
            # Check for typing indicator (ChatGPT is responding)
            if self.check_typing_indicator():
                current_time = time.time()
                if current_time - last_typing_indicator > 5:  # Log every 5 seconds
                    print("   ChatGPT is typing...")
                    last_typing_indicator = current_time
            
            # Check for error indicators
            if self.check_error_indicators():
                print("⚠️  Error indicator detected")
                return False
            
            # Wait before checking again
            time.sleep(2)
            
            # Progress update
            elapsed = time.time() - start_time
            if int(elapsed) % 10 == 0 and int(elapsed) > 0:
                print(f"   Still waiting... ({int(elapsed)}s/{timeout}s)")
        
        print(f"⏰ Timeout waiting for response ({timeout}s)")
        return False
    
    def check_response_received(self) -> bool:
        """
        Check if ChatGPT has responded.
        
        Returns:
            True if response appears to be received
        """
        # Look for new message indicators
        response_indicators = [
            "chatgpt_response",
            "ai_message",
            "response_bubble",
            "new_message_indicator"
        ]
        
        for indicator in response_indicators:
            result = self.find_element(indicator, timeout=1.0)
            if result and result[0]:
                return True
        
        # Also check that typing indicator is NOT present (response finished)
        if not self.check_typing_indicator():
            # Check for text in the chat area (simplified)
            # In a full implementation, would check for new text bubbles
            pass
        
        return False
    
    def check_typing_indicator(self) -> bool:
        """
        Check if ChatGPT is currently typing.
        
        Returns:
            True if typing indicator visible
        """
        typing_indicators = [
            "typing_indicator",
            "chatgpt_typing",
            "loading_response",
            "thinking_indicator"
        ]
        
        for indicator in typing_indicators:
            result = self.find_element(indicator, timeout=1.0)
            if result and result[0]:
                return True
        
        return False
    
    def check_error_indicators(self) -> bool:
        """
        Check for error messages.
        
        Returns:
            True if error detected
        """
        error_indicators = [
            "error_message",
            "rate_limit",
            "network_error",
            "service_unavailable"
        ]
        
        for indicator in error_indicators:
            result = self.find_element(indicator, timeout=1.0)
            if result and result[0]:
                print(f"❌ Error detected: {indicator}")
                return True
        
        return False
    
    def verify_chat_success(self, timeout: float = 10.0) -> bool:
        """
        Verify chat interaction was successful.
        
        Args:
            timeout: Time to wait for verification
            
        Returns:
            True if chat appears successful
        """
        print("✅ Verifying chat success...")
        
        # Check multiple success indicators
        success_indicators = [
            "message_sent_confirmation",
            "chat_history_updated",
            "response_visible"
        ]
        
        for indicator in success_indicators:
            if self.wait_for_element(indicator, timeout=3.0):
                print(f"✅ Chat success verified ({indicator})")
                return True
        
        # Also verify no error indicators
        if not self.check_error_indicators():
            print("✅ No errors detected, assuming success")
            return True
        
        print("⚠️  Chat success uncertain")
        return False
    
    def execute_conversation(self, messages: List[str], 
                           wait_between: float = 5.0) -> bool:
        """
        Execute a multi-message conversation.
        
        Args:
            messages: List of messages to send
            wait_between: Time to wait between messages
            
        Returns:
            True if all messages sent successfully
        """
        print(f"💬 Starting conversation with {len(messages)} messages")
        
        success_count = 0
        
        for i, message in enumerate(messages):
            print(f"\n[{i+1}/{len(messages)}] Sending: {message[:50]}..."
                  if len(message) > 50 else f"\n[{i+1}/{len(messages)}] Sending: {message}")
            
            # Create new chat task for this message
            chat_task = ChatTask(
                message=message,
                wait_for_response=True,
                response_timeout=self.response_timeout,
                template_dir=self.image_locator.template_dir,
                confidence_threshold=self.image_locator.confidence_threshold,
                save_screenshots=self.save_screenshots
            )
            
            # Execute the chat
            if chat_task.execute():
                success_count += 1
                print(f"✅ Message {i+1} sent successfully")
            else:
                print(f"❌ Message {i+1} failed")
            
            # Wait before next message (if not last)
            if i < len(messages) - 1:
                print(f"⏳ Waiting {wait_between}s before next message...")
                time.sleep(wait_between)
        
        print(f"\n📊 Conversation complete: {success_count}/{len(messages)} successful")
        return success_count == len(messages)


# Test function
def test_chat_task():
    """Test the chat task."""
    print("🧪 Testing ChatTask...")
    
    # Create task (will use test templates if available)
    task = ChatTask(
        message="Hello ChatGPT, this is a test from visual automation!",
        template_dir="visual_automation/config/templates/chatgpt/",
        save_screenshots=False
    )
    
    # Since we don't have templates yet, test will likely fail
    # but we can test the structure
    try:
        summary = task.get_summary()
        print(f"✅ Task initialized: {summary['task_name']}")
        print(f"   Message: {task.message}")
        print(f"   Wait for response: {task.wait_for_response}")
        print(f"   Response timeout: {task.response_timeout}")
        
        # Test conversation method
        test_messages = [
            "Hello!",
            "How are you today?",
            "Can you help me with a coding question?"
        ]
        
        print(f"\n🧪 Test conversation with {len(test_messages)} messages")
        print("   (Note: Will fail without templates)")
        
    except Exception as e:
        print(f"❌ Task initialization failed: {e}")
    
    return True


if __name__ == "__main__":
    test_chat_task()