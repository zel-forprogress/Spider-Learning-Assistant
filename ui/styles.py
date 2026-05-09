from dataclasses import dataclass


@dataclass(frozen=True)
class Colors:
    BG_PRIMARY = "#1a1a2e"
    BG_SECONDARY = "#16213e"
    BG_CHAT = "#0f3460"
    ACCENT = "#2563EB"
    ACCENT_HOVER = "#1d4ed8"
    TEXT_PRIMARY = "#e2e8f0"
    TEXT_SECONDARY = "#94a3b8"
    TEXT_MUTED = "#64748b"
    USER_BUBBLE = "#2563EB"
    AI_BUBBLE = "#1e293b"
    BORDER = "#334155"
    INPUT_BG = "#1e293b"
    SPIDER_BG = "#0f172a"
    ERROR = "#ef4444"
    SUCCESS = "#22c55e"


COLORS = Colors()

MAIN_WINDOW_QSS = f"""
QWidget {{
    background-color: {COLORS.BG_PRIMARY};
    color: {COLORS.TEXT_PRIMARY};
    font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
    font-size: 13px;
}}
"""

SPIDER_WIDGET_QSS = f"""
QLabel {{
    background-color: transparent;
}}
"""

CHAT_AREA_QSS = f"""
QScrollArea {{
    border: none;
    background-color: transparent;
}}
QScrollBar:vertical {{
    width: 6px;
    background: transparent;
}}
QScrollBar::handle:vertical {{
    background: {COLORS.BORDER};
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
"""

INPUT_QSS = f"""
QLineEdit {{
    background-color: {COLORS.INPUT_BG};
    color: {COLORS.TEXT_PRIMARY};
    border: 1px solid {COLORS.BORDER};
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
}}
QLineEdit:focus {{
    border-color: {COLORS.ACCENT};
}}
"""

SEND_BUTTON_QSS = f"""
QPushButton {{
    background-color: {COLORS.ACCENT};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: bold;
}}
QPushButton:hover {{
    background-color: {COLORS.ACCENT_HOVER};
}}
QPushButton:pressed {{
    background-color: #1e40af;
}}
QPushButton:disabled {{
    background-color: {COLORS.TEXT_MUTED};
    color: {COLORS.TEXT_SECONDARY};
}}
"""

USER_BUBBLE_QSS = f"""
QFrame {{
    background-color: {COLORS.USER_BUBBLE};
    border-radius: 12px;
    padding: 8px 12px;
}}
QLabel {{
    color: white;
    background-color: transparent;
}}
"""

AI_BUBBLE_QSS = f"""
QFrame {{
    background-color: {COLORS.AI_BUBBLE};
    border-radius: 12px;
    padding: 8px 12px;
}}
QLabel {{
    color: {COLORS.TEXT_PRIMARY};
    background-color: transparent;
}}
"""

SETTINGS_QSS = f"""
QDialog {{
    background-color: {COLORS.BG_PRIMARY};
    color: {COLORS.TEXT_PRIMARY};
}}
QTabWidget::pane {{
    border: 1px solid {COLORS.BORDER};
    background-color: {COLORS.BG_SECONDARY};
    border-radius: 4px;
}}
QTabBar::tab {{
    background-color: {COLORS.BG_SECONDARY};
    color: {COLORS.TEXT_SECONDARY};
    padding: 8px 20px;
    border: 1px solid {COLORS.BORDER};
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}}
QTabBar::tab:selected {{
    background-color: {COLORS.BG_PRIMARY};
    color: {COLORS.TEXT_PRIMARY};
}}
QLabel {{
    color: {COLORS.TEXT_PRIMARY};
}}
QLineEdit {{
    background-color: {COLORS.INPUT_BG};
    color: {COLORS.TEXT_PRIMARY};
    border: 1px solid {COLORS.BORDER};
    border-radius: 4px;
    padding: 6px 10px;
}}
QComboBox {{
    background-color: {COLORS.INPUT_BG};
    color: {COLORS.TEXT_PRIMARY};
    border: 1px solid {COLORS.BORDER};
    border-radius: 4px;
    padding: 6px 10px;
}}
QCheckBox {{
    color: {COLORS.TEXT_PRIMARY};
}}
"""

PAGE_INDICATOR_QSS = f"""
QLabel {{
    color: {COLORS.TEXT_MUTED};
    font-size: 11px;
    padding: 4px 0px;
}}
"""

TYPING_INDICATOR_QSS = f"""
QLabel {{
    color: {COLORS.TEXT_MUTED};
    font-style: italic;
    font-size: 12px;
    padding: 4px 8px;
}}
"""
