#!/usr/bin/env python3
"""
GPT Web Automation Agent

Automates login to ChatGPT, sends a message, and retrieves the response.
This serves as a POC for web automation in tax/invoice processing systems.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from playwright.async_api import async_playwright, Page, Browser, BrowserContext

from config import config


# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GPTAgent:
    """Agent for automating interactions with ChatGPT."""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_logged_in = False
        
        # Create screenshots directory
        self.screenshots_dir = Path(config.screenshots_dir)
        self.screenshots_dir.mkdir(exist_ok=True)
    
    async def __aenter__(self):
        await self.setup()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.teardown()
    
    async def setup(self):
        """Initialize Playwright and browser."""
        logger.info(f"Initializing {config.browser_type} browser...")
        self.playwright = await async_playwright().start()
        
        browser_map = {
            "chromium": self.playwright.chromium,
            "firefox": self.playwright.firefox,
            "webkit": self.playwright.webkit
        }
        
        browser_type = browser_map.get(config.browser_type.lower(), self.playwright.chromium)
        self.browser = await browser_type.launch(headless=config.headless)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        
        # Set default timeout
        self.page.set_default_timeout(config.timeout_ms)
        
        logger.info("Browser initialized successfully")
    
    async def teardown(self):
        """Clean up resources."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser closed")
    
    async def take_screenshot(self, name: str):
        """Take screenshot and save to screenshots directory."""
        if not self.page:
            return
        
        screenshot_path = self.screenshots_dir / f"{name}.png"
        await self.page.screenshot(path=str(screenshot_path))
        logger.debug(f"Screenshot saved: {screenshot_path}")
    
    async def login_to_chatgpt(self) -> bool:
        """
        Login to ChatGPT with provided credentials.
        
        Returns:
            bool: True if login successful, False otherwise
        """
        if not config.chatgpt_username or not config.chatgpt_password:
            logger.error("ChatGPT credentials not provided in config")
            return False
        
        logger.info(f"Navigating to login page: {config.chatgpt_login_url}")
        await self.page.goto(config.chatgpt_login_url)
        await self.take_screenshot("login_page")
        
        try:
            # Click login button
            logger.info("Clicking login button...")
            await self.page.click('button[data-testid="login-button"]')
            await self.page.wait_for_load_state("networkidle")
            await self.take_screenshot("login_form")
            
            # Fill username/email
            logger.info(f"Entering username: {config.chatgpt_username}")
            await self.page.fill('input[name="username"]', config.chatgpt_username)
            await self.page.click('button[type="submit"]')
            await asyncio.sleep(1)  # Wait for password field to appear
            
            # Fill password
            logger.info("Entering password...")
            await self.page.fill('input[name="password"]', config.chatgpt_password)
            await self.page.click('button[type="submit"]')
            
            # Wait for login to complete (redirect to chat page)
            await self.page.wait_for_url(config.chatgpt_chat_url, timeout=config.timeout_ms)
            await self.take_screenshot("logged_in")
            
            # Check for successful login by looking for chat input
            await self.page.wait_for_selector('textarea[data-id="root"]', timeout=config.timeout_ms)
            
            logger.info("Login successful!")
            self.is_logged_in = True
            return True
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            await self.take_screenshot("login_error")
            return False
    
    async def send_message(self, message: Optional[str] = None) -> Optional[str]:
        """
        Send a message to ChatGPT and get response.
        
        Args:
            message: Message to send (uses default from config if None)
            
        Returns:
            Optional[str]: Response text or None if failed
        """
        if not self.is_logged_in:
            logger.error("Not logged in. Please login first.")
            return None
        
        message_text = message or config.default_message
        logger.info(f"Sending message: {message_text}")
        
        try:
            # Find and fill the chat input
            chat_input = self.page.locator('textarea[data-id="root"]')
            await chat_input.fill(message_text)
            await self.take_screenshot("message_entered")
            
            # Send the message (press Enter)
            await chat_input.press("Enter")
            logger.info("Message sent, waiting for response...")
            
            # Wait for response
            await asyncio.sleep(config.wait_for_response_sec)
            
            # Get the latest response
            # ChatGPT responses are in divs with data-message-author-role="assistant"
            response_elements = await self.page.query_selector_all('div[data-message-author-role="assistant"]')
            if response_elements:
                latest_response = response_elements[-1]
                response_text = await latest_response.text_content()
                
                await self.take_screenshot("response_received")
                logger.info(f"Response received ({len(response_text)} chars)")
                return response_text.strip()
            else:
                logger.warning("No response elements found")
                await self.take_screenshot("no_response")
                return None
                
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            await self.take_screenshot("message_error")
            return None
    
    async def run_automation(self) -> Dict[str, Any]:
        """
        Run full automation: login -> send message -> get response.
        
        Returns:
            Dict with results and status
        """
        results = {
            "login_success": False,
            "message_sent": False,
            "response": None,
            "error": None
        }
        
        try:
            # Login
            login_success = await self.login_to_chatgpt()
            results["login_success"] = login_success
            
            if not login_success:
                results["error"] = "Login failed"
                return results
            
            # Send message and get response
            response = await self.send_message()
            results["message_sent"] = True
            results["response"] = response
            
            return results
            
        except Exception as e:
            logger.error(f"Automation failed: {e}")
            results["error"] = str(e)
            return results


async def main():
    """Main entry point for CLI usage."""
    print("GPT Web Automation Agent")
    print("=" * 50)
    
    # Check credentials
    if not config.chatgpt_username or not config.chatgpt_password:
        print("ERROR: ChatGPT credentials not configured.")
        print("Please set CHATGPT_USERNAME and CHATGPT_PASSWORD in .env file")
        print("See .env.example for template")
        sys.exit(1)
    
    print(f"Username: {config.chatgpt_username}")
    print(f"Browser: {config.browser_type} (headless: {config.headless})")
    print(f"Default message: {config.default_message}")
    print()
    
    async with GPTAgent() as agent:
        print("Starting automation...")
        results = await agent.run_automation()
        
        print("\nResults:")
        print(f"  Login successful: {results['login_success']}")
        print(f"  Message sent: {results['message_sent']}")
        
        if results.get('error'):
            print(f"  Error: {results['error']}")
        
        if results['response']:
            print(f"  Response preview: {results['response'][:200]}...")
            print(f"  Full response saved to log")
        
        return results


if __name__ == "__main__":
    try:
        results = asyncio.run(main())
        sys.exit(0 if results['login_success'] else 1)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)