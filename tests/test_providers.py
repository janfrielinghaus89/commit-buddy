"""Tests for AI provider implementations."""

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from commit_buddy.config import Config
from commit_buddy.providers import create_provider
from commit_buddy.providers.anthropic import AnthropicProvider
from commit_buddy.providers.base import AIProviderError
from commit_buddy.providers.ollama import OllamaProvider
from commit_buddy.providers.openai import OpenAIProvider


@pytest.fixture
def make_config():
    """Return a factory for provider configurations."""

    def factory(
        provider="ollama",
        model="test-model",
        api_key=None,
    ):
        return Config(
            provider=provider,
            model=model,
            api_key=api_key,
            ollama_host="http://localhost:11434",
        )

    return factory


@pytest.mark.parametrize(
    ("provider_name", "api_key", "expected_type"),
    [
        ("ollama", None, OllamaProvider),
        ("openai", "test-key", OpenAIProvider),
        ("anthropic", "test-key", AnthropicProvider),
    ],
)
def test_provider_factory(
    make_config,
    provider_name,
    api_key,
    expected_type,
):
    """Create the correct provider for each configuration."""

    config = make_config(provider_name, api_key=api_key)

    with (
        patch("commit_buddy.providers.ollama.Client"),
        patch("commit_buddy.providers.openai.OpenAI"),
        patch("commit_buddy.providers.anthropic.Anthropic"),
    ):
        provider = create_provider(config)

    assert isinstance(provider, expected_type)
    assert provider.model == "test-model"


@pytest.mark.parametrize("provider_name", ["openai", "anthropic"])
def test_factory_requires_api_key(make_config, provider_name):
    """Reject cloud providers without API credentials."""

    config = make_config(provider_name)

    with pytest.raises(ValueError, match="API key"):
        create_provider(config)


def test_factory_rejects_unknown_provider(make_config):
    """Reject an unsupported provider."""

    config = make_config("unknown")

    with pytest.raises(ValueError, match="Unsupported"):
        create_provider(config)


def test_ollama_generate():
    """Generate text through the mocked Ollama client."""

    with patch("commit_buddy.providers.ollama.Client") as client_class:
        client = client_class.return_value
        client.chat.return_value = SimpleNamespace(
            message=SimpleNamespace(content="feat: add validation")
        )

        provider = OllamaProvider(
            model="llama3.2",
            host="http://localhost:11434",
        )

        result = provider.generate("Test prompt")

    assert result == "feat: add validation"
    client.chat.assert_called_once_with(
        model="llama3.2",
        messages=[{"role": "user", "content": "Test prompt"}],
        options={"temperature": 0.2},
    )


def test_openai_generate():
    """Generate text through the mocked OpenAI client."""

    with patch("commit_buddy.providers.openai.OpenAI") as client_class:
        client = client_class.return_value
        client.responses.create.return_value = SimpleNamespace(
            output_text="fix: handle empty input"
        )

        provider = OpenAIProvider(
            model="gpt-4o-mini",
            api_key="test-key",
        )

        result = provider.generate("Test prompt")

    assert result == "fix: handle empty input"
    client.responses.create.assert_called_once_with(
        model="gpt-4o-mini",
        input="Test prompt",
        max_output_tokens=128,
    )


def test_anthropic_generate():
    """Extract text from the mocked Anthropic response."""

    with patch("commit_buddy.providers.anthropic.Anthropic") as client_class:
        client = client_class.return_value
        client.messages.create.return_value = SimpleNamespace(
            content=[
                SimpleNamespace(
                    type="text",
                    text="refactor: simplify parser",
                )
            ]
        )

        provider = AnthropicProvider(
            model="test-model",
            api_key="test-key",
        )

        result = provider.generate("Test prompt")

    assert result == "refactor: simplify parser"
    client.messages.create.assert_called_once_with(
        model="test-model",
        max_tokens=128,
        messages=[{"role": "user", "content": "Test prompt"}],
    )


@pytest.mark.parametrize(
    ("module", "class_name", "method"),
    [
        ("ollama", "OllamaProvider", "chat"),
        ("openai", "OpenAIProvider", "responses.create"),
        ("anthropic", "AnthropicProvider", "messages.create"),
    ],
)
def test_provider_handles_empty_response(
    module,
    class_name,
    method,
):
    """Reject empty AI responses."""

    provider_class = {
        "OllamaProvider": OllamaProvider,
        "OpenAIProvider": OpenAIProvider,
        "AnthropicProvider": AnthropicProvider,
    }[class_name]

    sdk_class = {
        "ollama": "Client",
        "openai": "OpenAI",
        "anthropic": "Anthropic",
    }[module]

    with patch(f"commit_buddy.providers.{module}.{sdk_class}") as client_class:
        client = client_class.return_value

        if method == "chat":
            client.chat.return_value = SimpleNamespace(
                message=SimpleNamespace(content=" ")
            )

        elif method == "responses.create":
            client.responses.create.return_value = SimpleNamespace(output_text=" ")

        else:
            client.messages.create.return_value = SimpleNamespace(content=[])

        if module == "ollama":
            provider = provider_class(
                model="test-model",
                host="http://localhost:11434",
            )
        else:
            provider = provider_class(
                model="test-model",
                api_key="test-key",
            )

        with pytest.raises(AIProviderError, match="empty response"):
            provider.generate("Test prompt")


@pytest.mark.parametrize(
    ("module", "sdk_class", "provider_class"),
    [
        ("ollama", "Client", OllamaProvider),
        ("openai", "OpenAI", OpenAIProvider),
        ("anthropic", "Anthropic", AnthropicProvider),
    ],
)
def test_provider_handles_api_failure(
    module,
    sdk_class,
    provider_class,
):
    """Wrap SDK errors in an application-specific exception."""

    with patch(f"commit_buddy.providers.{module}.{sdk_class}") as client_class:
        client = client_class.return_value

        if module == "ollama":
            client.chat.side_effect = RuntimeError("API failure")
            provider = provider_class(
                model="test-model",
                host="http://localhost:11434",
            )

        elif module == "openai":
            client.responses.create.side_effect = RuntimeError("API failure")
            provider = provider_class(
                model="test-model",
                api_key="test-key",
            )

        else:
            client.messages.create.side_effect = RuntimeError("API failure")
            provider = provider_class(
                model="test-model",
                api_key="test-key",
            )

        with pytest.raises(AIProviderError, match="generation failed"):
            provider.generate("Test prompt")
