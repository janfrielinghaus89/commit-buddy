"""Interactive command-line interface for Commit-Buddy."""

import subprocess
import sys

from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.prompt import Prompt

from commit_buddy import __version__
from commit_buddy.commit import InvalidCommitMessageError
from commit_buddy.config import ConfigurationError, load_config
from commit_buddy.generator import generate_commit_message
from commit_buddy.git import GitDiffError, NoStagedChangesError
from commit_buddy.prompts import DiffTooLargeError
from commit_buddy.providers.base import AIProviderError

console = Console()

CLOUD_PROVIDERS = {"openai", "anthropic"}


def confirm_action(message: str) -> bool:
    """Ask for explicit user confirmation."""

    answer = Prompt.ask(
        message,
        choices=["j", "n"],
        default="n",
        console=console,
    )

    return answer.lower() == "j"


def create_git_commit(message: str) -> None:
    """Create a Git commit using the generated message."""

    try:
        subprocess.run(
            ["git", "commit", "-m", message],
            check=True,
        )

    except FileNotFoundError as exc:
        raise GitDiffError("Git is not installed or cannot be found.") from exc

    except subprocess.CalledProcessError as exc:
        raise GitDiffError(
            "Git could not create the commit. Check the output above for details."
        ) from exc


def main() -> int:
    """Run the interactive Commit-Buddy workflow."""

    console.print()
    console.print(f"[bold cyan]🤖 Commit-Buddy v{__version__}[/bold cyan]")
    console.print()

    try:
        # Load provider configuration.
        config = load_config()

        console.print(f"DEBUG Ollama host: {config.ollama_host!r}")

        console.print(f"Provider: [bold cyan]{config.provider}[/bold cyan]")
        console.print(f"Model: [bold]{escape(config.model)}[/bold]")
        console.print()

        # Explicit consent before sending code to cloud APIs.
        if config.provider in CLOUD_PROVIDERS:
            console.print(
                "[yellow]⚠ Your staged Git changes will be "
                "sent to an external AI provider.[/yellow]"
            )

            if not confirm_action(
                "Möchtest du den Git-Diff an diesen Anbieter senden?"
            ):
                console.print("[yellow]Cloud request cancelled.[/yellow]")
                return 0

        # Generate the message.
        with console.status(
            "[cyan]Generating commit message...[/cyan]",
            spinner="dots",
        ):
            commit_message = generate_commit_message(config)

        # Display the suggestion.
        console.print()
        console.print(
            Panel(
                f"[bold green]{escape(commit_message)}[/bold green]",
                title="Suggested Commit",
                border_style="green",
                padding=(1, 2),
            )
        )

        console.print()

        # Require confirmation before committing.
        if not confirm_action("Möchtest du diesen Commit-Vorschlag nutzen?"):
            console.print("[yellow]Commit cancelled. No changes committed.[/yellow]")
            return 0

        console.print()
        console.print("[cyan]Creating Git commit...[/cyan]")

        create_git_commit(commit_message)

        console.print()
        console.print("[bold green]✓ Commit successfully created![/bold green]")

        return 0

    except NoStagedChangesError as exc:
        console.print("⚠", str(exc), style="yellow")
        return 1

    except (
        ConfigurationError,
        GitDiffError,
        DiffTooLargeError,
        InvalidCommitMessageError,
        AIProviderError,
    ) as exc:
        console.print("Error:", str(exc), style="bold red")
        return 1

    except (KeyboardInterrupt, EOFError):
        console.print("\n[yellow]Operation cancelled.[/yellow]")
        return 130


if __name__ == "__main__":
    sys.exit(main())
