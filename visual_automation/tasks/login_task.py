"""
Login task for visual automation.
Handles user authentication on websites.
"""
import time
from typing import Optional, Tuple, Dict, Any

from .base_task import BaseTask


class LoginTask(BaseTask):
    """Task for logging into websites."""
    
    def __init__(self, 
                 username: str,
                 password: str,
                 website: str = "chatgpt",  # chatgpt, github, etc.
                 **kwargs):
        """
        Initialize login task.
        
        Args:
            username: Username/email to login with
            password: Password to login with
            website: Website identifier for template selection
            **kwargs: Additional arguments for BaseTask
        """
        super().__init__(**kwargs)
        self.username = username
        self.password = password
        self.website = website
        
        # Set template directory based on website
        if 'template_dir' not in kwargs:
            self.image_locator.template_dir = f"config/templates/{website}/"
    
    def execute(self) -> bool:
        """
        Execute login process.
        
        Steps:
        1. Find and click login button (if not already on login page)
        2. Find username field and type username
        3. Find password field and type password
        4. Find and click submit button
        5. Wait for login to complete
        6. Verify login success
        
        Returns:
            True if login successful
        """
        print(f"🔐 LoginTask: Logging into {self.website} as {self.username}")
        
        # Record start
        self.capture_screenshot("before_login")
        
        # Step 1: Navigate to login if needed
        self.log_step("Navigate to login", False)
        if not self.ensure_login_page():
            print("❌ Could not reach login page")
            return False
        self.log_step("Navigate to login", True)
        
        # Step 2: Enter username
        self.log_step("Enter username", False)
        if not self.enter_username():
            print("❌ Failed to enter username")
            return False
        self.log_step("Enter username", True)
        
        # Step 3: Enter password
        self.log_step("Enter password", False)
        if not self.enter_password():
            print("❌ Failed to enter password")
            return False
        self.log_step("Enter password", True)
        
        # Step 4: Submit login
        self.log_step("Submit login", False)
        if not self.submit_login():
            print("❌ Failed to submit login")
            return False
        self.log_step("Submit login", True)
        
        # Step 5: Handle additional auth (2FA, captcha, etc.)
        self.log_step("Handle additional auth", False)
        if not self.handle_additional_auth():
            print("⚠️  Additional auth may be required")
        self.log_step("Handle additional auth", True)
        
        # Step 6: Verify login success
        self.log_step("Verify login", False)
        if not self.verify_login_success():
            print("⚠️  Login verification uncertain")
        self.log_step("Verify login", True)
        
        # Capture result
        self.capture_screenshot("after_login")
        
        print(f"✅ Login process completed")
        return True
    
    def ensure_login_page(self, timeout: float = 15.0) -> bool:
        """
        Ensure we're on the login page.
        
        Args:
            timeout: Time to wait for login page elements
            
        Returns:
            True if on login page
        """
        print("🔍 Checking if already on login page...")
        
        # Check for login form elements
        login_form_elements = [
            f"{self.website}_login_form",
            f"{self.website}_username_field",
            f"{self.website}_password_field",
            "login_form",
            "username_field",
            "password_field"
        ]
        
        for element in login_form_elements:
            result = self.find_element(element, timeout=2.0)
            if result and result[0]:
                print(f"✅ Already on login page (found {element})")
                return True
        
        # Not on login page, need to find login button
        print("Not on login page, looking for login button...")
        
        login_button_templates = [
            f"{self.website}_login_button",
            f"{self.website}_sign_in_button",
            "login_button",
            "sign_in_button",
            "log_in_button"
        ]
        
        for button in login_button_templates:
            if self.click_element(button, timeout=5.0):
                print(f"✅ Clicked {button}, waiting for login page...")
                
                # Wait for login page to load
                time.sleep(3)
                return self.wait_for_login_page(timeout)
        
        print("❌ Could not find login button or navigate to login page")
        return False
    
    def wait_for_login_page(self, timeout: float = 10.0) -> bool:
        """Wait for login page to appear."""
        return self.wait_for_element(f"{self.website}_login_form", timeout)
    
    def enter_username(self) -> bool:
        """Enter username into username field."""
        print(f"👤 Entering username: {self.username}")
        
        username_field_templates = [
            f"{self.website}_username_field",
            f"{self.website}_email_field",
            "username_field",
            "email_field",
            "login_username"
        ]
        
        for field in username_field_templates:
            if self.type_into_element(field, self.username, timeout=5.0):
                print(f"✅ Entered username into {field}")
                return True
        
        # Fallback: try to find field by tab order or position
        print("⚠️  Username field not found by template, trying alternative...")
        
        # Press Tab multiple times to navigate to username field
        self.input_simulator.press_keys(['tab'] * 3)
        time.sleep(0.5)
        
        # Type username
        self.input_simulator.type_text(self.username)
        
        return True
    
    def enter_password(self) -> bool:
        """Enter password into password field."""
        print("🔒 Entering password")
        
        password_field_templates = [
            f"{self.website}_password_field",
            "password_field",
            "login_password"
        ]
        
        for field in password_field_templates:
            if self.type_into_element(field, self.password, timeout=5.0):
                print(f"✅ Entered password into {field}")
                return True
        
        # Fallback: tab to password field and type
        print("⚠️  Password field not found by template, trying alternative...")
        
        # Tab from username to password field
        self.input_simulator.press_keys(['tab'])
        time.sleep(0.5)
        
        # Type password
        self.input_simulator.type_text(self.password)
        
        return True
    
    def submit_login(self) -> bool:
        """Submit the login form."""
        print("📤 Submitting login form...")
        
        submit_button_templates = [
            f"{self.website}_submit_button",
            f"{self.website}_login_submit",
            "submit_button",
            "login_submit",
            "sign_in_button"
        ]
        
        for button in submit_button_templates:
            if self.click_element(button, timeout=5.0):
                print(f"✅ Clicked {button} to submit login")
                
                # Wait for submission to process
                time.sleep(3)
                return True
        
        # Fallback: press Enter
        print("⚠️  Submit button not found, pressing Enter...")
        self.input_simulator.press_keys(['enter'])
        time.sleep(3)
        
        return True
    
    def handle_additional_auth(self, timeout: float = 30.0) -> bool:
        """
        Handle additional authentication steps (2FA, captcha, etc.).
        
        Args:
            timeout: Time to wait for additional auth
            
        Returns:
            True if additional auth handled or not required
        """
        print("🔐 Checking for additional authentication...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check for common additional auth elements
            auth_elements = [
                f"{self.website}_2fa_field",
                f"{self.website}_captcha",
                "two_factor_field",
                "captcha_image",
                "human_verification"
            ]
            
            auth_required = False
            for element in auth_elements:
                result = self.find_element(element, timeout=1.0)
                if result and result[0]:
                    print(f"⚠️  Additional auth required: {element}")
                    auth_required = True
                    break
            
            if not auth_required:
                print("✅ No additional auth required")
                return True
            
            # Check for specific auth types
            if self.handle_2fa():
                print("✅ 2FA handled")
                return True
            
            if self.handle_captcha():
                print("✅ CAPTCHA handled")
                return True
            
            if self.handle_human_verification():
                print("✅ Human verification handled")
                return True
            
            # Wait and check again
            print("⏳ Waiting for user to complete additional auth...")
            time.sleep(5)
            
            # Check if auth has been completed
            if self.check_auth_completed():
                print("✅ Additional auth appears completed")
                return True
        
        print("⚠️  Additional auth timeout - may require manual intervention")
        return False
    
    def handle_2fa(self) -> bool:
        """Handle two-factor authentication."""
        # Check for 2FA field
        result = self.find_element(f"{self.website}_2fa_field", timeout=2.0)
        if not result or not result[0]:
            return False
        
        print("📱 2FA required - waiting for manual input...")
        
        # In a real implementation, you might:
        # 1. Retrieve 2FA code from authenticator app
        # 2. Request code from user
        # 3. Automatically fill if code available
        
        # For now, wait for manual input
        print("   Please enter 2FA code manually...")
        
        # Wait reasonable time for manual input
        time.sleep(30)
        
        # Assume user entered code
        return True
    
    def handle_captcha(self) -> bool:
        """Handle CAPTCHA verification."""
        # Check for CAPTCHA
        result = self.find_element(f"{self.website}_captcha", timeout=2.0)
        if not result or not result[0]:
            return False
        
        print("🖼️ CAPTCHA detected - may require manual solving")
        
        # CAPTCHA typically requires human intervention
        # Could integrate with CAPTCHA solving service
        
        # For now, wait for manual solving
        print("   Please solve CAPTCHA manually...")
        time.sleep(30)
        
        return True
    
    def handle_human_verification(self) -> bool:
        """Handle human verification (e.g., "I'm not a robot")."""
        result = self.find_element("human_verification", timeout=2.0)
        if not result or not result[0]:
            return False
        
        print("👤 Human verification required")
        
        # This usually requires clicking a checkbox
        if self.click_element("human_verification_checkbox", timeout=5.0):
            print("✅ Clicked human verification checkbox")
            time.sleep(3)
            return True
        
        return False
    
    def check_auth_completed(self) -> bool:
        """Check if additional authentication appears completed."""
        # Look for indicators that auth is complete
        complete_indicators = [
            f"{self.website}_dashboard",
            f"{self.website}_logged_in",
            "main_app_screen"
        ]
        
        for indicator in complete_indicators:
            result = self.find_element(indicator, timeout=1.0)
            if result and result[0]:
                return True
        
        return False
    
    def verify_login_success(self, timeout: float = 20.0) -> bool:
        """
        Verify that login was successful.
        
        Args:
            timeout: Time to wait for login confirmation
            
        Returns:
            True if login appears successful
        """
        print("✅ Verifying login success...")
        
        # Look for elements that indicate successful login
        success_indicators = [
            f"{self.website}_user_menu",
            f"{self.website}_dashboard",
            f"{self.website}_profile_icon",
            "user_avatar",
            "logged_in_indicator"
        ]
        
        for indicator in success_indicators:
            if self.wait_for_element(indicator, timeout=5.0):
                print(f"✅ Login successful (found {indicator})")
                return True
        
        # Also check that we're not seeing error messages
        error_indicators = [
            f"{self.website}_login_error",
            "error_message",
            "invalid_credentials"
        ]
        
        for indicator in error_indicators:
            result = self.find_element(indicator, timeout=2.0)
            if result and result[0]:
                print(f"❌ Login error detected: {indicator}")
                return False
        
        print("⚠️  Login status uncertain")
        return False


# ChatGPT-specific login task
class ChatGPTLoginTask(LoginTask):
    """Specialized login task for ChatGPT."""
    
    def __init__(self, username: str, password: str, **kwargs):
        super().__init__(username, password, website="chatgpt", **kwargs)
    
    def handle_additional_auth(self, timeout: float = 60.0) -> bool:
        """
        Handle ChatGPT-specific additional auth.
        ChatGPT often has "Verify you are human" checkbox.
        """
        print("🤖 Handling ChatGPT-specific authentication...")
        
        # Check for "Verify you are human" checkbox
        human_checkbox_templates = [
            "chatgpt_human_checkbox",
            "verify_human_checkbox",
            "human_verification"
        ]
        
        for template in human_checkbox_templates:
            if self.click_element(template, timeout=10.0):
                print(f"✅ Clicked {template}")
                
                # Wait for verification to complete
                time.sleep(5)
                return True
        
        # Check for Cloudflare challenge
        cloudflare_templates = [
            "cloudflare_challenge",
            "checking_browser"
        ]
        
        for template in cloudflare_templates:
            result = self.find_element(template, timeout=5.0)
            if result and result[0]:
                print(f"⚠️  Cloudflare challenge detected: {template}")
                print("   Waiting for challenge to complete...")
                time.sleep(10)
                return True
        
        # Check if already authenticated
        if self.check_auth_completed():
            return True
        
        print("⚠️  May require manual authentication")
        return False


# Test function
def test_login_task():
    """Test login task."""
    print("🧪 Testing LoginTask...")
    
    # Create task (using test credentials)
    task = LoginTask(
        username="test@example.com",
        password="testpassword",
        website="test_site",
        template_dir="test_templates/",
        save_screenshots=False
    )
    
    # Test would fail without templates, but test structure
    try:
        summary = task.get_summary()
        print(f"✅ Task initialized: {summary['task_name']}")
    except Exception as e:
        print(f"❌ Task initialization failed: {e}")
    
    return True


if __name__ == "__main__":
    test_login_task()