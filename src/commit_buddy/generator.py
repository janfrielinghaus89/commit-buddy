"""Orchestration of AI-powered commit message generation."""

from commit_buddy.commit import validate_commit_message
from commit_buddy.config import Config, load_config
from commit_buddy.git import get_staged_diff
from commit_buddy.prompts import build_commit_prompt
from commit_buddy.providers import create_provider


def generate_commit_message(config: Config | None = None) -> str:
    """Generate a validated commit message from staged changes."""

    if config is None:
        config = load_config()

    # Read staged changes.
    diff = get_staged_diff()

    # Build the AI prompt.
    prompt = build_commit_prompt(diff)

    # Initialize the configured provider.
    provider = create_provider(config)

    # Generate the message.
    response = provider.generate(prompt)

    # Validate the result before returning it.
    return validate_commit_message(response)
