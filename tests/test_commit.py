"""Tests for Conventional Commit validation."""

import pytest

from commit_buddy.commit import (
    InvalidCommitMessageError,
    validate_commit_message,
)


@pytest.mark.parametrize(
    "message",
    [
        "feat: add user authentication",
        "fix(api): handle missing header",
        "docs: update README",
        "refactor: simplify parser",
        "test(parser): add validation tests",
        "feat(api)!: remove legacy endpoint",
    ],
)
def test_valid_commit_messages(message):
    assert validate_commit_message(message) == message


def test_normalize_backticks():
    result = validate_commit_message("`feat: add validation`")

    assert result == "feat: add validation"


def test_normalize_code_block():
    result = validate_commit_message("```\nfeat: add validation\n```")

    assert result == "feat: add validation"


@pytest.mark.parametrize(
    "message",
    [
        "",
        "Added user authentication",
        "feature: add authentication",
        "Feat: add authentication",
        "feat: Add authentication",
        "feat: add authentication.",
        "feat add authentication",
        "feat: add something\nfix: another change",
        "feat: " + "a" * 80,
    ],
)
def test_invalid_commit_messages(message):
    with pytest.raises(InvalidCommitMessageError):
        validate_commit_message(message)
