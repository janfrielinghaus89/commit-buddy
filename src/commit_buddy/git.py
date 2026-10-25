"""Utilities for reading staged Git changes."""

import subprocess


class GitDiffError(Exception):
    """Raised when Git changes cannot be read."""


class NoStagedChangesError(GitDiffError):
    """Raised when no staged changes are available."""


def get_staged_diff() -> str:
    """
    Return the staged Git diff from the current working directory.

    Raises:
        GitDiffError: If Git is unavailable or the command fails.
        NoStagedChangesError: If no staged changes are found.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )

    except FileNotFoundError as exc:
        raise GitDiffError("Git is not installed or cannot be found.") from exc

    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or "").strip()

        raise GitDiffError(f"Failed to read staged Git changes: {detail}") from exc

    diff = result.stdout

    if not diff.strip():
        raise NoStagedChangesError(
            "No staged changes found. Use 'git add <file>' to stage your changes."
        )

    return diff
