# 🤖 Commit-Buddy

**AI-powered Conventional Commit messages, right from your terminal.**

Commit-Buddy is a lightweight Python CLI tool that analyzes staged Git changes and generates concise, structured commit messages using either local or cloud-based AI models.

It supports **Ollama, OpenAI, and Anthropic**, allowing developers to choose between local inference and cloud APIs.

## Features

- **AI-powered commits** — Generate commit messages based on staged Git changes.
- **Conventional Commits** — Generate consistent, structured messages.
- **Multiple AI providers** — Support for Ollama, OpenAI, and Anthropic.
- **Local-first support** — Run models locally without sending code to cloud services.
- **Interactive CLI** — Review generated messages before committing.
- **Cloud consent** — Explicit confirmation before sending staged changes to a cloud provider.
- **Validation** — Reject messages that do not match the expected commit format.
- **Automated testing** — Unit tests and cross-platform GitHub Actions CI.

## Requirements

- Python 3.11 or newer
- Git
- Ollama with a downloaded model, or an API key for a supported cloud provider

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/commit-buddy.git
cd commit-buddy
```

Install Commit-Buddy:

```bash
python -m pip install .
```

For development, use:

```bash
python -m pip install -e ".[dev]"
```

## Configuration

Copy the example environment file into the Git repository where you want to use Commit-Buddy:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Choose your preferred provider in `.env`.

### Ollama (local)

```dotenv
AI_PROVIDER=ollama
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.2
```

Make sure Ollama is running and the model is installed:

```bash
ollama pull llama3.2
```

### OpenAI

```dotenv
AI_PROVIDER=openai
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-4o-mini
```

### Anthropic

```dotenv
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-api-key
ANTHROPIC_MODEL=your-supported-model-id
```

### Automatic provider selection

```dotenv
AI_PROVIDER=auto
```

In automatic mode, Commit-Buddy selects OpenAI when its API key is available, otherwise Anthropic when its API key is available, and otherwise Ollama.

An explicitly selected cloud provider also falls back to Ollama when its required API key is missing.

Environment variables take precedence over `.env` values.

## Usage

Navigate to an existing Git repository and stage your changes:

```bash
git add .
```

Run:

```bash
commit-buddy
```

Example:

```text
Commit-Buddy v0.1.0

Provider: ollama
Model: llama3.2

Suggested Commit:
feat(config): add automatic provider selection

Möchtest du diesen Commit-Vorschlag nutzen? [j/n] (n):
```

Enter `j` to create the Git commit, or `n` to cancel.

Commit-Buddy only commits changes already staged in Git. It does not automatically stage additional files.

## Safety and limitations

- AI-generated commit messages must be reviewed before use.
- Cloud providers receive the staged Git diff after explicit confirmation.
- Local Ollama inference does not require uploading source code to a cloud AI provider.
- Staged diffs are limited to 30,000 characters.
- Generated commit messages are validated against a one-line Conventional Commit format with a 72-character limit.
- The tool does not currently redact secrets or sensitive information from Git diffs.
- The staging area should not be modified by another process between generation and commit confirmation.
- API credentials should never be committed to version control.

## Development

Install development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Run the tests:

```bash
python -m pytest -v
```

Check linting:

```bash
python -m ruff check .
```

Check formatting:

```bash
python -m ruff format --check .
```

GitHub Actions runs the test suite on Windows, macOS, and Ubuntu using Python 3.11, 3.12, and 3.13.

## Project Structure

```text
src/commit_buddy/
├── cli.py
├── commit.py
├── config.py
├── generator.py
├── git.py
├── prompts.py
└── providers/
    ├── base.py
    ├── ollama.py
    ├── openai.py
    └── anthropic.py
```

## Future Improvements

- Regenerate or manually edit commit suggestions
- Customizable prompt templates
- Configurable diff size limits
- Additional AI providers
- Improved secret detection and diff sanitization

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.