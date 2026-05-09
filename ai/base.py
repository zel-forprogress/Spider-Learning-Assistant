from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generator


@dataclass
class ChatMessage:
    role: str  # "system" | "user" | "assistant"
    content: str


SYSTEM_PROMPT_TEMPLATE = """You are Spider, a helpful learning assistant. You help the user understand the content of web pages they are browsing.

CURRENT PAGE:
Title: {title}
URL: {url}

PAGE CONTENT:
{page_content}

PREVIOUS PAGES VISITED:
{history_summary}

Answer the user's questions based on the page content above. If the question is not related to the current page, answer normally. Be concise and helpful. When referencing specific parts of the page, quote relevant text."""


class AIProvider(ABC):
    @abstractmethod
    def chat_stream(self, messages: list[ChatMessage]) -> Generator[str, None, None]:
        ...

    @abstractmethod
    def chat_sync(self, messages: list[ChatMessage]) -> str:
        ...

    @abstractmethod
    def list_models(self) -> list[str]:
        ...

    @abstractmethod
    def validate_config(self) -> bool:
        ...


def build_system_prompt(title: str, url: str, page_content: str,
                        history_summary: str = "None") -> str:
    return SYSTEM_PROMPT_TEMPLATE.format(
        title=title,
        url=url,
        page_content=page_content[:6000],
        history_summary=history_summary or "None",
    )
