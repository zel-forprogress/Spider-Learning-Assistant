from typing import Generator

from ai.base import AIProvider, ChatMessage


class ClaudeProvider(AIProvider):
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        import anthropic
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def chat_stream(self, messages: list[ChatMessage]) -> Generator[str, None, None]:
        system_msg = ""
        user_msgs = []
        for m in messages:
            if m.role == "system":
                system_msg = m.content
            else:
                user_msgs.append({"role": m.role, "content": m.content})

        with self._client.messages.stream(
            model=self._model,
            max_tokens=4096,
            system=system_msg,
            messages=user_msgs,
        ) as stream:
            for text in stream.text_stream:
                yield text

    def chat_sync(self, messages: list[ChatMessage]) -> str:
        system_msg = ""
        user_msgs = []
        for m in messages:
            if m.role == "system":
                system_msg = m.content
            else:
                user_msgs.append({"role": m.role, "content": m.content})

        response = self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            system=system_msg,
            messages=user_msgs,
        )
        return response.content[0].text

    def list_models(self) -> list[str]:
        return [
            "claude-sonnet-4-20250514",
            "claude-haiku-4-20250414",
            "claude-opus-4-20250514",
        ]

    def validate_config(self) -> bool:
        try:
            self._client.messages.create(
                model=self._model,
                max_tokens=10,
                messages=[{"role": "user", "content": "hi"}],
            )
            return True
        except Exception:
            return False
