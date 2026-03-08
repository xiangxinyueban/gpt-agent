"""
Tests for GPT Agent.

Note: These are mostly unit tests since full integration tests
require actual ChatGPT credentials and browser automation.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from gpt_agent import GPTAgent
from config import config


class TestGPTAgent:
    """Test cases for GPTAgent class."""
    
    @pytest.fixture
    def mock_page(self):
        """Create a mock Playwright page."""
        page = AsyncMock()
        page.goto = AsyncMock()
        page.click = AsyncMock()
        page.fill = AsyncMock()
        page.wait_for_url = AsyncMock()
        page.wait_for_selector = AsyncMock()
        page.wait_for_load_state = AsyncMock()
        page.set_default_timeout = AsyncMock()
        page.screenshot = AsyncMock()
        page.locator.return_value = AsyncMock()
        page.query_selector_all = AsyncMock()
        return page
    
    @pytest.fixture
    def mock_context(self, mock_page):
        """Create a mock Playwright context."""
        context = AsyncMock()
        context.new_page = AsyncMock(return_value=mock_page)
        return context
    
    @pytest.fixture
    def mock_browser(self, mock_context):
        """Create a mock Playwright browser."""
        browser = AsyncMock()
        browser.new_context = AsyncMock(return_value=mock_context)
        return browser
    
    @pytest.fixture
    def mock_playwright(self, mock_browser):
        """Create a mock Playwright instance."""
        playwright = AsyncMock()
        playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        playwright.firefox.launch = AsyncMock(return_value=mock_browser)
        playwright.webkit.launch = AsyncMock(return_value=mock_browser)
        playwright.stop = AsyncMock()
        return playwright
    
    @pytest.mark.asyncio
    async def test_agent_setup(self, mock_playwright, mock_browser, mock_context, mock_page):
        """Test agent setup and teardown."""
        with patch('playwright.async_api.async_playwright') as mock_playwright_init:
            mock_playwright_init.return_value.start = AsyncMock(return_value=mock_playwright)
            
            agent = GPTAgent()
            await agent.setup()
            
            # Verify setup
            assert agent.playwright is mock_playwright
            assert agent.browser is mock_browser
            assert agent.context is mock_context
            assert agent.page is mock_page
            
            # Verify browser launch
            mock_playwright.chromium.launch.assert_called_once_with(headless=config.headless)
            
            await agent.teardown()
            mock_browser.close.assert_called_once()
            mock_playwright.stop.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_login_failure_missing_credentials(self, mock_playwright, mock_browser, mock_context, mock_page):
        """Test login fails when credentials are missing."""
        with patch('playwright.async_api.async_playwright') as mock_playwright_init:
            mock_playwright_init.return_value.start = AsyncMock(return_value=mock_playwright)
            
            # Temporarily clear credentials
            original_username = config.chatgpt_username
            original_password = config.chatgpt_password
            config.chatgpt_username = None
            config.chatgpt_password = None
            
            agent = GPTAgent()
            await agent.setup()
            
            login_success = await agent.login_to_chatgpt()
            assert not login_success
            
            await agent.teardown()
            
            # Restore credentials
            config.chatgpt_username = original_username
            config.chatgpt_password = original_password
    
    def test_config_loading(self):
        """Test that configuration loads correctly."""
        assert hasattr(config, 'chatgpt_username')
        assert hasattr(config, 'chatgpt_password')
        assert hasattr(config, 'browser_type')
        assert hasattr(config, 'headless')
        assert hasattr(config, 'default_message')
    
    @pytest.mark.asyncio
    async def test_screenshot_directory_creation(self, tmp_path):
        """Test that screenshot directory is created."""
        # Monkey patch config screenshots_dir
        original_dir = config.screenshots_dir
        test_dir = tmp_path / "test_screenshots"
        config.screenshots_dir = str(test_dir)
        
        agent = GPTAgent()
        assert test_dir.exists()
        
        # Restore
        config.screenshots_dir = original_dir


class TestConfig:
    """Test cases for configuration."""
    
    def test_config_defaults(self):
        """Test default configuration values."""
        assert config.browser_type == "chromium"
        assert config.default_message == "你好gpt"
        assert config.chatgpt_login_url == "https://chat.openai.com/auth/login"
        assert config.chatgpt_chat_url == "https://chat.openai.com/"
    
    def test_config_environment_variables(self, monkeypatch):
        """Test environment variable overrides."""
        monkeypatch.setenv("BROWSER_TYPE", "firefox")
        monkeypatch.setenv("HEADLESS", "true")
        monkeypatch.setenv("DEFAULT_MESSAGE", "Hello GPT")
        
        # Reload config
        from config import load_config
        test_config = load_config()
        
        assert test_config.browser_type == "firefox"
        assert test_config.headless is True
        assert test_config.default_message == "Hello GPT"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])