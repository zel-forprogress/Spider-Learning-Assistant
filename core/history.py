import json
from collections import deque
from pathlib import Path
from dataclasses import dataclass, field, asdict

from core.content_structurer import StructuredPage


@dataclass
class ConversationEntry:
    user_message: str = ""
    ai_response: str = ""


@dataclass
class PageHistory:
    structured_page: StructuredPage = field(default_factory=StructuredPage)
    conversations: list = field(default_factory=list)


class HistoryManager:
    def __init__(self, max_pages: int = 10, persist_to_disk: bool = True):
        self._max_pages = max_pages
        self._persist = persist_to_disk
        self._pages: deque = deque(maxlen=max_pages)
        self._current_page: StructuredPage | None = None

    def add_page(self, page: StructuredPage):
        self._current_page = page
        entry = PageHistory(structured_page=page)
        self._pages.append(entry)

    def add_conversation(self, user_msg: str, ai_response: str):
        if self._pages:
            self._pages[-1].conversations.append(
                ConversationEntry(user_message=user_msg, ai_response=ai_response)
            )

    def get_current_page(self) -> StructuredPage | None:
        return self._current_page

    def get_history_summary(self, max_chars: int = 2000) -> str:
        parts = []
        for entry in self._pages:
            page = entry.structured_page
            if page.title:
                parts.append(f"- {page.title} ({page.url})")

        result = "\n".join(parts)
        if len(result) > max_chars:
            result = result[:max_chars] + "..."
        return result

    def get_recent_conversations(self, n: int = 5) -> list[ConversationEntry]:
        if not self._pages:
            return []
        all_convos = []
        for entry in self._pages:
            all_convos.extend(entry.conversations)
        return all_convos[-n:]

    def clear(self):
        self._pages.clear()
        self._current_page = None
