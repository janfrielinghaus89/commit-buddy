"""Base interface for AI providers."""

from abc import ABC, abstractmethod


class AIProviderError(Exception):
    """Raised when an AI provider fails to generate a response."""


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate text using the configured AI model."""
