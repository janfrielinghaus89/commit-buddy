"""Factory for creating configured AI providers."""

from commit_buddy.config import Config
from commit_buddy.providers.anthropic import AnthropicProvider
from commit_buddy.providers.base import AIProvider
from commit_buddy.providers.ollama import OllamaProvider
from commit_buddy.providers.openai import OpenAIProvider


def create_provider(config: Config) -> AIProvider:
    """Create the AI provider selected by the configuration."""

    if config.provider == "ollama":
        return OllamaProvider(
            model=config.model,
            host=config.ollama_host,
        )

    if config.provider == "openai":
        if not config.api_key:
            raise ValueError("OpenAI requires an API key.")

        return OpenAIProvider(
            model=config.model,
            api_key=config.api_key,
        )

    if config.provider == "anthropic":
        if not config.api_key:
            raise ValueError("Anthropic requires an API key.")

        return AnthropicProvider(
            model=config.model,
            api_key=config.api_key,
        )

    raise ValueError(f"Unsupported AI provider: {config.provider}")
