"""Local AI provider using Ollama."""

from ollama import Client

from commit_buddy.providers.base import AIProvider, AIProviderError


class OllamaProvider(AIProvider):
    """Generate text using a local Ollama model."""

    def __init__(self, model: str, host: str) -> None:
        self.model = model
        self.client = Client(host=host, timeout=60.0)

    def generate(self, prompt: str) -> str:
        """Generate a response using Ollama."""

        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                options={"temperature": 0.2},
            )

            content = response.message.content

            if not content or not content.strip():
                raise AIProviderError("Ollama returned an empty response.")

            return content.strip()

        except AIProviderError:
            raise

        except Exception as exc:
            raise AIProviderError(
                f"Ollama generation failed: {type(exc).__name__}"
            ) from exc
