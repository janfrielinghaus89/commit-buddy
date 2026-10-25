"""Validation and normalization of Conventional Commit messages."""

import re


class InvalidCommitMessageError(ValueError):
    """Raised when an AI-generated commit message is invalid."""


COMMIT_PATTERN = re.compile(
    r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
    r"(\([a-z0-9][a-z0-9._/-]*\))?"
    r"!?: "
    r"([a-z][^\r\n]*)$"
)

MAX_COMMIT_LENGTH = 72


def normalize_commit_message(message: str) -> str:
    """Remove harmless surrounding formatting from a model response."""

    message = message.strip()

    if message.startswith("```") and message.endswith("```"):
        lines = message.splitlines()

        if len(lines) == 3:
            message = lines[1].strip()

    if message.startswith("`") and message.endswith("`"):
        message = message[1:-1].strip()

    return message.strip()


def validate_commit_message(message: str) -> str:
    """Validate and return a Conventional Commit message."""

    message = normalize_commit_message(message)

    if not message:
        raise InvalidCommitMessageError(
            "The AI provider returned an empty commit message."
        )

    if "\n" in message or "\r" in message:
        raise InvalidCommitMessageError(
            "Commit messages must contain exactly one line."
        )

    if len(message) > MAX_COMMIT_LENGTH:
        raise InvalidCommitMessageError(
            f"Commit message exceeds {MAX_COMMIT_LENGTH} characters."
        )

    match = COMMIT_PATTERN.fullmatch(message)

    if match is None:
        raise InvalidCommitMessageError(
            "The generated message does not follow Conventional Commits."
        )

    description = match.group(3)

    if description.endswith("."):
        raise InvalidCommitMessageError(
            "Commit descriptions must not end with a period."
        )

    return message
