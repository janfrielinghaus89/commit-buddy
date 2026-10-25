"""Tests for staged Git diff handling."""

import subprocess
from unittest.mock import patch

import pytest

from commit_buddy.git import (
    GitDiffError,
    NoStagedChangesError,
    get_staged_diff,
)


def test_get_staged_diff_success():
    """Return staged changes when a diff exists."""

    expected_diff = "diff --git a/test.py b/test.py\n+print('Hello World')\n"

    with patch("commit_buddy.git.subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(
            args=["git", "diff", "--cached"],
            returncode=0,
            stdout=expected_diff,
            stderr="",
        )

        result = get_staged_diff()

    assert result == expected_diff

    mock_run.assert_called_once_with(
        ["git", "diff", "--cached"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )


def test_get_staged_diff_empty():
    """Raise an error when no changes are staged."""

    with patch("commit_buddy.git.subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(
            args=["git", "diff", "--cached"],
            returncode=0,
            stdout="",
            stderr="",
        )

        with pytest.raises(NoStagedChangesError):
            get_staged_diff()


def test_get_staged_diff_whitespace_only():
    """Treat whitespace-only output as an empty diff."""

    with patch("commit_buddy.git.subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(
            args=["git", "diff", "--cached"],
            returncode=0,
            stdout="   \n",
            stderr="",
        )

        with pytest.raises(NoStagedChangesError):
            get_staged_diff()


def test_get_staged_diff_git_not_found():
    """Raise a readable error if Git is unavailable."""

    with patch("commit_buddy.git.subprocess.run") as mock_run:
        mock_run.side_effect = FileNotFoundError()

        with pytest.raises(GitDiffError, match="not installed"):
            get_staged_diff()


def test_get_staged_diff_command_failure():
    """Raise an error when the Git command fails."""

    with patch("commit_buddy.git.subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=128,
            cmd=["git", "diff", "--cached"],
            stderr="Not a git repository",
        )

        with pytest.raises(
            GitDiffError,
            match="Not a git repository",
        ):
            get_staged_diff()
