from typing import Generator

from ai.base import AIProvider, ChatMessage


class OllamaProvider(AIProvider):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2"):
        import ollama
        self._client = ollama.Client(host=base_url)
        self._model = model

    def chat_stream(self, messages: list[ChatMessage]) -> Generator[str, None, None]:
        stream = self._client.chat(
            model=self._model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            stream=True,
        )
        for chunk in stream:
            content = chunk.get("message", {}).get("content", "")
            if content:
                yield content

    def chat_sync(self, messages: list[ChatMessage]) -> str:
        response = self._client.chat(
            model=self._model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
        )
        return response["message"]["content"]

    def list_models(self) -> list[str]:
        try:
            models = self._client.list()
            return [m["name"] for m in models.get("models", [])]
        except Exception:
            return [self._model]

    def validate_config(self) -> bool:
        try:
            self._client.list()
            return True
        except Exception:
            return False
