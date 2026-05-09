import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path


CONFIG_DIR = Path(os.environ.get("APPDATA", Path.home())) / "SpiderLearningAssistant"
CONFIG_FILE = CONFIG_DIR / "config.json"
PROJECT_CONFIG = Path(__file__).parent.parent / "config.json"


@dataclass
class AIConfig:
    provider: str = "openai"
    model: str = "gpt-4o"
    max_tokens: int = 2048
    temperature: float = 0.7


@dataclass
class BrowserConfig:
    poll_interval: float = 2.0
    max_content_tokens: int = 8000
    auto_crawl: bool = True


@dataclass
class UIConfig:
    language: str = "en"  # "en" or "zh"
    window_x: int = 100
    window_y: int = 100
    window_width: int = 380
    window_height: int = 520
    collapsed_width: int = 120
    collapsed_height: int = 140
    opacity: float = 0.92
    start_collapsed: bool = False


@dataclass
class ProviderConfig:
    api_key: str = ""
    default_model: str = ""
    available_models: list = field(default_factory=list)
    base_url: str = ""


@dataclass
class HistoryConfig:
    max_pages: int = 10
    max_conversations: int = 50
    persist_to_disk: bool = True


@dataclass
class Config:
    ai: AIConfig = field(default_factory=AIConfig)
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    history: HistoryConfig = field(default_factory=HistoryConfig)
    providers: dict = field(default_factory=lambda: {
        "openai": ProviderConfig(default_model="gpt-4o", available_models=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]),
        "claude": ProviderConfig(default_model="claude-sonnet-4-20250514", available_models=["claude-sonnet-4-20250514", "claude-haiku-4-20250414"]),
        "ollama": ProviderConfig(base_url="http://localhost:11434", default_model="llama3.2"),
    })


def _dict_to_dataclass(cls, data: dict):
    if isinstance(data, dict):
        if cls == Config:
            return Config(
                ai=_dict_to_dataclass(AIConfig, data.get("ai", {})),
                browser=_dict_to_dataclass(BrowserConfig, data.get("browser", {})),
                ui=_dict_to_dataclass(UIConfig, data.get("ui", {})),
                history=_dict_to_dataclass(HistoryConfig, data.get("history", {})),
                providers=data.get("providers", {}),
            )
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    return cls()


def load_config() -> Config:
    for path in [CONFIG_FILE, PROJECT_CONFIG]:
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return _dict_to_dataclass(Config, data)
            except (json.JSONDecodeError, TypeError):
                continue
    return Config()


def save_config(config: Config):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    data = asdict(config)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
