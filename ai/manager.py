import logging

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from ai.base import AIProvider, ChatMessage, build_system_prompt
from core.config import AIConfig
from core.content_structurer import StructuredPage

logger = logging.getLogger(__name__)


class AISendWorker(QThread):
    chunk_received = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, provider: AIProvider, messages: list[ChatMessage], parent=None):
        super().__init__(parent)
        self._provider = provider
        self._messages = messages

    def run(self):
        try:
            full = ""
            for chunk in self._provider.chat_stream(self._messages):
                full += chunk
                self.chunk_received.emit(chunk)
            self.finished.emit(full)
        except Exception as e:
            logger.error(f"AI stream error: {e}")
            self.error.emit(str(e))


class AIManager(QObject):
    response_chunk = pyqtSignal(str)
    response_complete = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._provider: AIProvider | None = None
        self._worker: AISendWorker | None = None

    def set_provider(self, config: AIConfig, provider_cfg: dict):
        try:
            provider_name = config.provider
            api_key = provider_cfg.get("api_key", "")

            if not api_key and provider_name != "ollama":
                logger.info(f"No API key for {provider_name}, provider not configured")
                self._provider = None
                return

            if provider_name == "openai":
                from ai.openai_provider import OpenAIProvider
                self._provider = OpenAIProvider(
                    api_key=api_key,
                    model=config.model,
                    base_url=provider_cfg.get("base_url"),
                )
            elif provider_name == "claude":
                from ai.claude_provider import ClaudeProvider
                self._provider = ClaudeProvider(
                    api_key=api_key,
                    model=config.model,
                )
            elif provider_name == "ollama":
                from ai.ollama_provider import OllamaProvider
                self._provider = OllamaProvider(
                    base_url=provider_cfg.get("base_url", "http://localhost:11434"),
                    model=config.model,
                )
            else:
                self._provider = None
        except Exception as e:
            logger.debug(f"Provider not available: {e}")
            self._provider = None

    def send_message(self, user_message: str, context: StructuredPage | None,
                     history_summary: str = ""):
        if not self._provider:
            self.error.emit("No AI provider configured. Please set up a provider in Settings.")
            return

        if self._worker and self._worker.isRunning():
            self.error.emit("Still processing the previous question...")
            return

        system_content = ""
        if context:
            system_content = build_system_prompt(
                title=context.title,
                url=context.url,
                page_content=context.raw_text,
                history_summary=history_summary,
            )

        messages = []
        if system_content:
            messages.append(ChatMessage(role="system", content=system_content))
        messages.append(ChatMessage(role="user", content=user_message))

        self._worker = AISendWorker(self._provider, messages)
        self._worker.chunk_received.connect(self.response_chunk.emit)
        self._worker.finished.connect(self.response_complete.emit)
        self._worker.error.connect(self.error.emit)
        self._worker.start()
