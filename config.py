"""
Configuration management for GPT Agent.
Uses environment variables for sensitive data.
"""

import os
from typing import Optional
from pydantic import BaseSettings, Field


class GPTConfig(BaseSettings):
    """Configuration for GPT web automation."""
    
    # ChatGPT login credentials
    chatgpt_username: Optional[str] = Field(None, env="CHATGPT_USERNAME")
    chatgpt_password: Optional[str] = Field(None, env="CHATGPT_PASSWORD")
    
    # Browser settings
    browser_type: str = Field("chromium", env="BROWSER_TYPE")  # chromium, firefox, webkit
    headless: bool = Field(False, env="HEADLESS")  # Set to True for headless mode
    timeout_ms: int = Field(30000, env="TIMEOUT_MS")  # Default timeout in milliseconds
    
    # GPT interaction settings
    default_message: str = Field("你好gpt", env="DEFAULT_MESSAGE")
    wait_for_response_sec: int = Field(10, env="WAIT_FOR_RESPONSE_SEC")
    
    # URLs
    chatgpt_login_url: str = Field("https://chat.openai.com/auth/login", env="CHATGPT_LOGIN_URL")
    chatgpt_chat_url: str = Field("https://chat.openai.com/", env="CHATGPT_CHAT_URL")
    
    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    screenshots_dir: str = Field("./screenshots", env="SCREENSHOTS_DIR")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def load_config() -> GPTConfig:
    """Load configuration from environment variables."""
    return GPTConfig()


# Global config instance
config = load_config()