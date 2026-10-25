"""Tests for commit message generation."""

from unittest.mock import Mock, patch

import pytest

from commit_buddy.commit import InvalidCommitMessageError
from commit_buddy.config import Config
from commit_buddy.generator import generate_commit_message
from commit_buddy.prompts import DiffTooLargeError


@pytest.fixture
def test_config():
    return Config(
        provider="ollama",
        model="llama3.2",
        api_key=None,
        ollama_host="http://localhost:11434",
    )


def test_generate_commit_message(test_config):
    provider = Mock()
    provider.generate.return_value = "feat: add validation"

    with (
        patch(
            "commit_buddy.generator.get_staged_diff",
            return_value="+def validate(): pass",
        ),
        patch(
            "commit_buddy.generator.create_provider",
            return_value=provider,
        ) as factory,
    ):
        result = generate_commit_message(test_config)

    assert result == "feat: add validation"
    factory.assert_called_once_with(test_config)
    provider.generate.assert_called_once()

    prompt = provider.generate.call_args.args[0]
    assert "+def validate(): pass" in prompt


def test_invalid_ai_response(test_config):
    provider = Mock()
    provider.generate.return_value = "Here is your commit message!"

    with (
        patch(
            "commit_buddy.generator.get_staged_diff",
            return_value="+print('test')",
        ),
        patch(
            "commit_buddy.generator.create_provider",
            return_value=provider,
        ),
        pytest.raises(InvalidCommitMessageError),
    ):
        generate_commit_message(test_config)


def test_large_diff_rejected_before_api_call(test_config):
    with (
        patch(
            "commit_buddy.generator.get_staged_diff",
            return_value="x" * 30_001,
        ),
        patch("commit_buddy.generator.create_provider") as factory,
        pytest.raises(DiffTooLargeError),
    ):
        generate_commit_message(test_config)

    factory.assert_not_called()


def test_automatic_config_loading():
    config = Config(
        provider="ollama",
        model="llama3.2",
        api_key=None,
        ollama_host="http://localhost:11434",
    )

    provider = Mock()
    provider.generate.return_value = "fix: handle missing input"

    with (
        patch(
            "commit_buddy.generator.load_config",
            return_value=config,
        ) as load,
        patch(
            "commit_buddy.generator.get_staged_diff",
            return_value="+if value is None: return",
        ),
        patch(
            "commit_buddy.generator.create_provider",
            return_value=provider,
        ),
    ):
        result = generate_commit_message()

    load.assert_called_once()
    assert result == "fix: handle missing input"
