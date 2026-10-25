"""Cloud AI provider using Anthropic."""

from anthropic import Anthropic

from commit_buddy.providers.base import AIProvider, AIProviderError


class AnthropicProvider(AIProvider):
    """Generate text using the Anthropic Messages API."""

    def __init__(self, model: str, api_key: str) -> None:
        self.model = model
        self.client = Anthropic(
            api_key=api_key,
            timeout=60.0,
            max_retries=1,
        )

    def generate(self, prompt: str) -> str:
        """Generate a response using Anthropic."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=128,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

            content = "".join(
                block.text for block in response.content if block.type == "text"
            )

            if not content.strip():
                raise AIProviderError("Anthropic returned an empty response.")

            return content.strip()

        except AIProviderError:
            raise

        except Exception as exc:
            raise AIProviderError(
                f"Anthropic generation failed: {type(exc).__name__}"
            ) from exc
