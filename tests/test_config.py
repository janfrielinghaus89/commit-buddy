"""Tests for environment-based configuration."""

import pytest

from commit_buddy.config import (
    ConfigurationError,
    load_config,
    resolve_provider,
)


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch, tmp_path):
    """Isolate tests from real environment variables and .env files."""

    monkeypatch.chdir(tmp_path)

    variables = [
        "AI_PROVIDER",
        "OPENAI_API_KEY",
        "OPENAI_MODEL",
        "ANTHROPIC_API_KEY",
        "ANTHROPIC_MODEL",
        "OLLAMA_HOST",
        "OLLAMA_MODEL",
    ]

    for variable in variables:
        monkeypatch.delenv(variable, raising=False)


def test_auto_falls_back_to_ollama():
    """Use Ollama when no API keys are configured."""

    assert resolve_provider() == "ollama"


def test_auto_prefers_openai(monkeypatch):
    """Prefer OpenAI when both API keys are present."""

    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")

    assert resolve_provider() == "openai"


def test_auto_uses_anthropic(monkeypatch):
    """Use Anthropic when only its API key exists."""

    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    assert resolve_provider() == "anthropic"


def test_explicit_ollama_overrides_api_keys(monkeypatch):
    """Allow explicitly selecting the local provider."""

    monkeypatch.setenv("AI_PROVIDER", "ollama")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    assert resolve_provider() == "ollama"


def test_missing_openai_key_falls_back(monkeypatch):
    """Use Ollama if OpenAI was selected without a key."""

    monkeypatch.setenv("AI_PROVIDER", "openai")

    assert resolve_provider() == "ollama"


def test_missing_anthropic_key_falls_back(monkeypatch):
    """Use Ollama if Anthropic was selected without a key."""

    monkeypatch.setenv("AI_PROVIDER", "anthropic")

    assert resolve_provider() == "ollama"


def test_invalid_provider(monkeypatch):
    """Reject unsupported provider names."""

    monkeypatch.setenv("AI_PROVIDER", "unknown")

    with pytest.raises(ConfigurationError, match="Invalid AI_PROVIDER"):
        resolve_provider()


def test_load_config_defaults():
    """Load default Ollama configuration."""

    config = load_config()

    assert config.provider == "ollama"
    assert config.model == "llama3.2"
    assert config.api_key is None
    assert config.ollama_host == "http://localhost:11434"


def test_load_config_openai(monkeypatch):
    """Load the OpenAI model and API key."""

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")

    config = load_config()

    assert config.provider == "openai"
    assert config.model == "gpt-4o-mini"
    assert config.api_key == "test-key"


def test_load_config_anthropic(monkeypatch):
    """Load Anthropic configuration."""

    monkeypatch.setenv("AI_PROVIDER", "anthropic")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("ANTHROPIC_MODEL", "test-model")

    config = load_config()

    assert config.provider == "anthropic"
    assert config.model == "test-model"
    assert config.api_key == "test-key"


def test_anthropic_requires_model(monkeypatch):
    """Require an explicit model name for Anthropic."""

    monkeypatch.setenv("AI_PROVIDER", "anthropic")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    with pytest.raises(ConfigurationError, match="ANTHROPIC_MODEL"):
        load_config()


def test_load_config_from_dotenv(tmp_path):
    """Read configuration from the current directory's .env file."""

    env_file = tmp_path / ".env"
    env_file.write_text(
        "AI_PROVIDER=ollama\nOLLAMA_MODEL=qwen2.5-coder:14b\n",
        encoding="utf-8",
    )

    config = load_config()

    assert config.provider == "ollama"
    assert config.model == "qwen2.5-coder:14b"


def test_environment_overrides_dotenv(monkeypatch, tmp_path):
    """Existing environment variables take precedence over .env."""

    (tmp_path / ".env").write_text(
        "OLLAMA_MODEL=llama3.2\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("OLLAMA_MODEL", "qwen2.5-coder:14b")

    config = load_config()

    assert config.model == "qwen2.5-coder:14b"


def test_api_key_whitespace_is_ignored(monkeypatch):
    """Treat whitespace-only API keys as missing."""

    monkeypatch.setenv("OPENAI_API_KEY", "   ")

    assert resolve_provider() == "ollama"
