import re
from dataclasses import dataclass, field

from bs4 import BeautifulSoup, Tag


@dataclass
class StructuredPage:
    url: str = ""
    title: str = ""
    headings: list = field(default_factory=list)
    paragraphs: list = field(default_factory=list)
    code_blocks: list = field(default_factory=list)
    lists: list = field(default_factory=list)
    links: list = field(default_factory=list)
    raw_text: str = ""
    token_count: int = 0
    content_hash: str = ""

    def to_context_string(self) -> str:
        parts = []
        if self.title:
            parts.append(f"Page Title: {self.title}")
        if self.url:
            parts.append(f"URL: {self.url}")

        for h in self.headings:
            level = h.get("level", 1)
            prefix = "#" * level
            parts.append(f"{prefix} {h.get('text', '')}")

        for p in self.paragraphs:
            parts.append(p)

        for code in self.code_blocks:
            parts.append(f"```\n{code}\n```")

        for lst in self.lists:
            items = lst.get("items", [])
            for i, item in enumerate(items):
                parts.append(f"- {item}" if lst.get("type") == "ul" else f"{i+1}. {item}")

        return "\n\n".join(parts)


class ContentStructurer:
    TAGS_TO_REMOVE = [
        "script", "style", "noscript", "nav", "footer",
        "header", "aside", "iframe", "svg", "form",
        "button", "input", "select", "textarea",
    ]

    def structure(self, html: str, url: str = "") -> StructuredPage:
        soup = BeautifulSoup(html, "lxml")

        for tag_name in self.TAGS_TO_REMOVE:
            for tag in soup.find_all(tag_name):
                tag.decompose()

        title = ""
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text(strip=True)

        if not title:
            h1 = soup.find("h1")
            if h1:
                title = h1.get_text(strip=True)

        headings = []
        for level in range(1, 7):
            for h in soup.find_all(f"h{level}"):
                text = h.get_text(strip=True)
                if text:
                    headings.append({"level": level, "text": text})

        paragraphs = []
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if text and len(text) > 10:
                paragraphs.append(text)

        code_blocks = []
        for pre in soup.find_all("pre"):
            code = pre.get_text()
            if code.strip():
                code_blocks.append(code.strip())

        lists = []
        for ul in soup.find_all(["ul", "ol"]):
            items = []
            for li in ul.find_all("li", recursive=False):
                text = li.get_text(strip=True)
                if text:
                    items.append(text)
            if items:
                lists.append({
                    "type": ul.name,
                    "items": items,
                })

        links = []
        for a in soup.find_all("a", href=True):
            text = a.get_text(strip=True)
            href = a["href"]
            if text and href:
                links.append({"text": text[:100], "href": href})

        raw_text = self._extract_clean_text(soup)
        token_count = int(len(raw_text.split()) * 1.3)

        return StructuredPage(
            url=url,
            title=title,
            headings=headings,
            paragraphs=paragraphs,
            code_blocks=code_blocks,
            lists=lists,
            links=links,
            raw_text=raw_text,
            token_count=token_count,
        )

    def truncate_to_budget(self, page: StructuredPage, max_tokens: int) -> StructuredPage:
        if page.token_count <= max_tokens:
            return page

        context_str = page.to_context_string()
        words = context_str.split()
        budget_words = int(max_tokens / 1.3)
        truncated = " ".join(words[:budget_words])

        page.raw_text = truncated
        page.token_count = max_tokens
        return page

    def _extract_clean_text(self, soup: BeautifulSoup) -> str:
        text = soup.get_text(separator="\n", strip=True)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)
