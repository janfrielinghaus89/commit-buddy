"""Cloud AI provider using OpenAI."""

from openai import OpenAI

from commit_buddy.providers.base import AIProvider, AIProviderError


class OpenAIProvider(AIProvider):
    """Generate text using the OpenAI Responses API."""

    def __init__(self, model: str, api_key: str) -> None:
        self.model = model
        self.client = OpenAI(
            api_key=api_key,
            timeout=60.0,
            max_retries=1,
        )

    def generate(self, prompt: str) -> str:
        """Generate a response using OpenAI."""

        try:
            response = self.client.responses.create(
                model=self.model,
                input=prompt,
                max_output_tokens=128,
            )

            content = response.output_text

            if not content or not content.strip():
                raise AIProviderError("OpenAI returned an empty response.")

            return content.strip()

        except AIProviderError:
            raise

        except Exception as exc:
            raise AIProviderError(
                f"OpenAI generation failed: {type(exc).__name__}"
            ) from exc
