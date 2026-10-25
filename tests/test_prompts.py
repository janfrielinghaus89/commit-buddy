"""Tests for commit prompt generation."""

import pytest

from commit_buddy.prompts import (
    MAX_DIFF_CHARS,
    DiffTooLargeError,
    build_commit_prompt,
)


def test_prompt_contains_diff():
    diff = "+print('Hello World')"

    prompt = build_commit_prompt(diff)

    assert diff in prompt
    assert "Conventional Commit" in prompt
    assert "untrusted data" in prompt


def test_prompt_requires_english():
    prompt = build_commit_prompt("+new_function()")

    assert "in English" in prompt
    assert "exactly one line" in prompt


def test_empty_diff():
    with pytest.raises(ValueError, match="empty diff"):
        build_commit_prompt("")


def test_whitespace_diff():
    with pytest.raises(ValueError, match="empty diff"):
        build_commit_prompt("   \n")


def test_diff_too_large():
    diff = "x" * (MAX_DIFF_CHARS + 1)

    with pytest.raises(DiffTooLargeError):
        build_commit_prompt(diff)


def test_diff_at_size_limit():
    diff = "x" * MAX_DIFF_CHARS

    assert diff in build_commit_prompt(diff)
