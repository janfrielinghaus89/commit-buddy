"""Environment-based configuration for Commit-Buddy."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

AIProvider = Literal["openai", "anthropic", "ollama"]

SUPPORTED_PROVIDERS = {
    "auto",
    "openai",
    "anthropic",
    "ollama",
}


class ConfigurationError(Exception):
    """Raised when the application configuration is invalid."""


@dataclass(frozen=True)
class Config:
    """Resolved application configuration."""

    provider: AIProvider
    model: str
    api_key: str | None
    ollama_host: str


def get_env(name: str, default: str = "") -> str:
    """Return a stripped environment variable."""

    return os.getenv(name, default).strip()


def resolve_provider() -> AIProvider:
    """Determine which AI provider should be used."""

    requested_provider = get_env("AI_PROVIDER", "auto").lower()

    if requested_provider not in SUPPORTED_PROVIDERS:
        raise ConfigurationError(
            f"Invalid AI_PROVIDER '{requested_provider}'. "
            "Supported values: auto, openai, anthropic, ollama."
        )

    openai_key = get_env("OPENAI_API_KEY")
    anthropic_key = get_env("ANTHROPIC_API_KEY")

    if requested_provider == "ollama":
        return "ollama"

    if requested_provider == "openai":
        return "openai" if openai_key else "ollama"

    if requested_provider == "anthropic":
        return "anthropic" if anthropic_key else "ollama"

    # Automatic provider selection.
    if openai_key:
        return "openai"

    if anthropic_key:
        return "anthropic"

    return "ollama"


def load_config() -> Config:
    """Load environment variables and resolve the AI configuration."""

    load_dotenv(
        dotenv_path=Path.cwd() / ".env",
        override=False,
    )

    provider = resolve_provider()

    if provider == "openai":
        model = get_env("OPENAI_MODEL", "gpt-4o-mini")
        api_key = get_env("OPENAI_API_KEY")

    elif provider == "anthropic":
        model = get_env("ANTHROPIC_MODEL")
        api_key = get_env("ANTHROPIC_API_KEY")

        if not model:
            raise ConfigurationError(
                "ANTHROPIC_MODEL must be configured when using Anthropic."
            )

    else:
        model = get_env("OLLAMA_MODEL", "llama3.2")
        api_key = None

    if not model:
        raise ConfigurationError(f"No model configured for provider '{provider}'.")

    ollama_host = get_env(
        "OLLAMA_HOST",
        "http://localhost:11434",
    )

    if not ollama_host:
        raise ConfigurationError("OLLAMA_HOST cannot be empty.")

    return Config(
        provider=provider,
        model=model,
        api_key=api_key,
        ollama_host=ollama_host,
    )
