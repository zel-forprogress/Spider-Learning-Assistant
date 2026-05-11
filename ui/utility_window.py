from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from core.i18n import t
from ui.styles import COLORS, MAIN_WINDOW_QSS, CHAT_AREA_QSS


class PageCard(QFrame):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS.AI_BUBBLE};
                border-radius: 8px;
                padding: 4px;
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)

        icon = QLabel("📄")
        icon.setStyleSheet("font-size: 16px; background: transparent;")
        layout.addWidget(icon)

        label = QLabel(title)
        label.setStyleSheet(f"color: {COLORS.TEXT_PRIMARY}; background: transparent; font-size: 12px;")
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(label, 1)


class UtilityWindow(QWidget):
    settings_requested = pyqtSignal()

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self._config = config
        self._drag_pos = None
        self._page_titles = []

        self.setWindowTitle(t("app_name"))
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(MAIN_WINDOW_QSS)
        self.setMinimumSize(300, 350)
        self.resize(320, 400)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        header = QLabel(t("app_name"))
        header.setStyleSheet(f"color: {COLORS.TEXT_PRIMARY}; font-size: 14px; font-weight: bold; padding: 4px 8px;")
        layout.addWidget(header)

        pages_label = QLabel(t("browsing_history") if hasattr(t, '__call__') else "Browse History")
        pages_label.setStyleSheet(f"color: {COLORS.TEXT_MUTED}; font-size: 11px; padding: 2px 8px;")
        layout.addWidget(pages_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(CHAT_AREA_QSS)

        self._pages_widget = QWidget()
        self._pages_layout = QVBoxLayout(self._pages_widget)
        self._pages_layout.setContentsMargins(4, 4, 4, 4)
        self._pages_layout.setSpacing(4)
        self._pages_layout.addStretch()
        scroll.setWidget(self._pages_widget)
        layout.addWidget(scroll, 1)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self._settings_btn = QPushButton("⚙ " + t("settings"))
        self._settings_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS.BORDER};
                color: {COLORS.TEXT_PRIMARY};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {COLORS.ACCENT};
            }}
        """)
        self._settings_btn.clicked.connect(self.settings_requested.emit)
        btn_layout.addWidget(self._settings_btn)

        layout.addLayout(btn_layout)

    def add_page(self, title: str):
        if title in self._page_titles:
            return
        self._page_titles.insert(0, title)
        card = PageCard(title)
        self._pages_layout.insertWidget(0, card)
        if len(self._page_titles) > 20:
            old = self._pages_layout.itemAt(self._pages_layout.count() - 2).widget()
            if old:
                old.deleteLater()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            new_pos = event.globalPosition().toPoint() - self._drag_pos
            self.move(new_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    def closeEvent(self, event):
        self.hide()
        event.ignore()
