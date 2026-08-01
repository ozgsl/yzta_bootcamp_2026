from abc import ABC, abstractmethod
from typing import Any


class AIProvider(ABC):
    @abstractmethod
    def classify_image(self, image_path: str = None, image_b64: str = None) -> dict[str, Any]:
        """Analyzes an image and returns clothing attributes."""
        
    @abstractmethod
    def get_chat_response(self, history: list[dict[str, str]], user_message: str) -> dict[str, Any]:
        """Gets a chat response from an AI model (e.g. LLM)."""
        
    @abstractmethod
    def generate_outfit_recommendation(self, context: dict[str, Any], clothes: list[dict[str, Any]]) -> dict[str, Any]:
        """Generates an outfit recommendation based on context and wardrobe."""

class OllamaProvider(AIProvider):
    """
    Ollama implementation for AI Provider.
    For classification, it might delegate to FashionClassifier if Ollama is purely LLM.
    """
    def __init__(self):
        # We can dynamically import to avoid loading heavy models unnecessarily
        pass
        
    def classify_image(self, image_path: str = None, image_b64: str = None) -> dict[str, Any]:
        from app.core.ai.fashion_classifier import FashionClassifier
        classifier = FashionClassifier()
        if image_path:
            return classifier.classify_image(image_path=image_path)
        return classifier.classify_image(image_b64=image_b64)
        
    def get_chat_response(self, history: list[dict[str, str]], user_message: str) -> dict[str, Any]:
        from app.core.ai.ollama_client import OllamaClient
        client = OllamaClient()
        return client.get_chat_response(history, user_message)
        
    def generate_outfit_recommendation(self, context: dict[str, Any], clothes: list[dict[str, Any]]) -> dict[str, Any]:
        from app.core.ai.ollama_client import OllamaClient
        client = OllamaClient()
        return client.generate_outfit_recommendation(context, clothes)
