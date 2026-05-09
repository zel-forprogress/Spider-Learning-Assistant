import json
from pathlib import Path

# 翻译文件目录
LOCALES_DIR = Path(__file__).parent.parent / "locales"

# 默认语言
_current_lang = "en"

# 翻译字典
_translations = {}


def set_language(lang: str):
    """设置当前语言"""
    global _current_lang, _translations
    _current_lang = lang
    _translations = _load_translations(lang)


def get_language() -> str:
    """获取当前语言"""
    return _current_lang


def t(key: str, **kwargs) -> str:
    """翻译文本，支持参数插值"""
    text = _translations.get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text


def _load_translations(lang: str) -> dict:
    """加载翻译文件"""
    if lang == "en":
        return {}

    path = LOCALES_DIR / f"{lang}.json"
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def get_available_languages() -> list[dict]:
    """获取可用语言列表"""
    return [
        {"code": "en", "name": "English"},
        {"code": "zh", "name": "中文"},
    ]
