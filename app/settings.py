from pydantic_settings import BaseSettings
from typing import Dict, Any

class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GATEWAY_AUTH_TOKEN: str = "local-dev-token"
    
    # Routing Table
    ROUTES: Dict[str, Dict[str, Any]] = {
        "codex": {
            "provider": "openai",
            "model": "gpt-5.3-codex",
            "reasoning_effort": "medium",
        },
        "codex-low": {
            "provider": "openai",
            "model": "gpt-5.3-codex",
            "reasoning_effort": "low",
        },
        "codex-high": {
            "provider": "openai",
            "model": "gpt-5.3-codex",
            "reasoning_effort": "high",
        },
        "gemini": {
            "provider": "google",
            "model": "gemini-3.1-pro-preview",
        },
        "gemini-flash": {
            "provider": "google",
            "model": "gemini-3-flash-preview",
        },
        "gemini-flash-lite": {
            "provider": "google",
            "model": "gemini-3-flash-lite-preview",
        },
        # Standard Claude Models (Proxy to Anthropic)
        "claude-3-5-sonnet-latest": {"provider": "anthropic"},
        "claude-3-5-sonnet-20241022": {"provider": "anthropic"},
        "claude-3-5-haiku-latest": {"provider": "anthropic"},
        "claude-3-5-haiku-20241022": {"provider": "anthropic"},
        "claude-3-opus-latest": {"provider": "anthropic"},
        "claude-3-opus-20240229": {"provider": "anthropic"},
    }

    class Config:
        env_file = ".env"

settings = Settings()
