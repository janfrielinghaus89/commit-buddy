"""Tests for the interactive Commit-Buddy CLI."""

import subprocess
from unittest.mock import patch

import pytest

from commit_buddy.cli import (
    confirm_action,
    create_git_commit,
    main,
)
from commit_buddy.config import Config
from commit_buddy.git import GitDiffError, NoStagedChangesError


@pytest.fixture
def ollama_config():
    """Return a local Ollama configuration."""

    return Config(
        provider="ollama",
        model="llama3.2",
        api_key=None,
        ollama_host="http://localhost:11434",
    )


@pytest.fixture
def openai_config():
    """Return a cloud OpenAI configuration."""

    return Config(
        provider="openai",
        model="gpt-4o-mini",
        api_key="test-key",
        ollama_host="http://localhost:11434",
    )


def test_confirm_action_yes():
    """Accept an explicit yes response."""

    with patch(
        "commit_buddy.cli.Prompt.ask",
        return_value="j",
    ):
        assert confirm_action("Continue?") is True


def test_confirm_action_no():
    """Reject an explicit no response."""

    with patch(
        "commit_buddy.cli.Prompt.ask",
        return_value="n",
    ):
        assert confirm_action("Continue?") is False


def test_create_git_commit():
    """Run Git with the generated commit message."""

    with patch("commit_buddy.cli.subprocess.run") as mock_run:
        create_git_commit("feat: add validation")

    mock_run.assert_called_once_with(
        [
            "git",
            "commit",
            "-m",
            "feat: add validation",
        ],
        check=True,
    )


def test_create_git_commit_failure():
    """Handle a failed Git commit command."""

    with patch("commit_buddy.cli.subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=["git", "commit"],
        )

        with pytest.raises(GitDiffError):
            create_git_commit("feat: add validation")


def test_cli_success(ollama_config):
    """Generate and confirm a commit successfully."""

    with (
        patch(
            "commit_buddy.cli.load_config",
            return_value=ollama_config,
        ),
        patch(
            "commit_buddy.cli.generate_commit_message",
            return_value="feat: add validation",
        ),
        patch(
            "commit_buddy.cli.confirm_action",
            return_value=True,
        ),
        patch(
            "commit_buddy.cli.create_git_commit",
        ) as commit,
    ):
        result = main()

    assert result == 0
    commit.assert_called_once_with("feat: add validation")


def test_cli_commit_cancelled(ollama_config):
    """Do not commit if the user rejects the suggestion."""

    with (
        patch(
            "commit_buddy.cli.load_config",
            return_value=ollama_config,
        ),
        patch(
            "commit_buddy.cli.generate_commit_message",
            return_value="feat: add validation",
        ),
        patch(
            "commit_buddy.cli.confirm_action",
            return_value=False,
        ),
        patch("commit_buddy.cli.create_git_commit") as commit,
    ):
        result = main()

    assert result == 0
    commit.assert_not_called()


def test_cli_cloud_request_cancelled(openai_config):
    """Do not send a cloud request without user consent."""

    with (
        patch(
            "commit_buddy.cli.load_config",
            return_value=openai_config,
        ),
        patch(
            "commit_buddy.cli.confirm_action",
            return_value=False,
        ),
        patch("commit_buddy.cli.generate_commit_message") as generate,
    ):
        result = main()

    assert result == 0
    generate.assert_not_called()


def test_cli_cloud_request_approved(openai_config):
    """Generate after cloud consent but do not commit if rejected."""

    with (
        patch(
            "commit_buddy.cli.load_config",
            return_value=openai_config,
        ),
        patch(
            "commit_buddy.cli.confirm_action",
            side_effect=[True, False],
        ) as confirm,
        patch(
            "commit_buddy.cli.generate_commit_message",
            return_value="fix: handle empty input",
        ) as generate,
        patch("commit_buddy.cli.create_git_commit") as commit,
    ):
        result = main()

    assert result == 0
    assert confirm.call_count == 2
    generate.assert_called_once_with(openai_config)
    commit.assert_not_called()


def test_cli_no_staged_changes(ollama_config):
    """Handle an empty Git staging area."""

    with (
        patch(
            "commit_buddy.cli.load_config",
            return_value=ollama_config,
        ),
        patch(
            "commit_buddy.cli.generate_commit_message",
            side_effect=NoStagedChangesError("No staged changes."),
        ),
        patch("commit_buddy.cli.create_git_commit") as commit,
    ):
        result = main()

    assert result == 1
    commit.assert_not_called()


def test_cli_keyboard_interrupt(ollama_config):
    """Handle Ctrl+C without creating a commit."""

    with (
        patch(
            "commit_buddy.cli.load_config",
            return_value=ollama_config,
        ),
        patch(
            "commit_buddy.cli.generate_commit_message",
            side_effect=KeyboardInterrupt,
        ),
        patch("commit_buddy.cli.create_git_commit") as commit,
    ):
        result = main()

    assert result == 130
    commit.assert_not_called()
