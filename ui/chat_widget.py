from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QLineEdit, QPushButton, QFrame, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from core.i18n import t
from ui.styles import COLORS, CHAT_AREA_QSS, INPUT_QSS, SEND_BUTTON_QSS, USER_BUBBLE_QSS, AI_BUBBLE_QSS, TYPING_INDICATOR_QSS


class ChatBubble(QFrame):
    def __init__(self, text: str, is_user: bool, parent=None):
        super().__init__(parent)
        self._is_user = is_user
        self._setup_ui(text)

    def _setup_ui(self, text: str):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        bubble = QFrame()
        bubble.setStyleSheet(USER_BUBBLE_QSS if self._is_user else AI_BUBBLE_QSS)
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(10, 8, 10, 8)
        bubble_layout.setSpacing(2)

        label = QLabel(text)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label.setFont(QFont("Segoe UI", 12))
        bubble_layout.addWidget(label)

        max_width = 280
        bubble.setMaximumWidth(max_width)
        bubble.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)

        if self._is_user:
            layout.addStretch()
            layout.addWidget(bubble)
        else:
            layout.addWidget(bubble)
            layout.addStretch()

        self.setStyleSheet("background: transparent;")


class TypingIndicator(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        self._label = QLabel(t("thinking"))
        self._label.setStyleSheet(TYPING_INDICATOR_QSS)
        layout.addWidget(self._label)
        layout.addStretch()

        self._dot_count = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(500)

    def _animate(self):
        self._dot_count = (self._dot_count + 1) % 4
        dots = "." * self._dot_count
        self._label.setText(t("thinking") + dots)

    def stop(self):
        self._timer.stop()


class ChatWidget(QWidget):
    message_sent = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._streaming_label = None
        self._typing_indicator = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet(CHAT_AREA_QSS)

        self._messages_widget = QWidget()
        self._messages_layout = QVBoxLayout(self._messages_widget)
        self._messages_layout.setContentsMargins(4, 8, 4, 8)
        self._messages_layout.setSpacing(4)
        self._messages_layout.addStretch()

        self._scroll.setWidget(self._messages_widget)
        layout.addWidget(self._scroll, 1)

        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(8, 8, 8, 8)
        input_layout.setSpacing(8)

        self._input = QLineEdit()
        self._input.setPlaceholderText(t("ask_placeholder"))
        self._input.setStyleSheet(INPUT_QSS)
        self._input.returnPressed.connect(self._on_send)
        input_layout.addWidget(self._input, 1)

        self._send_btn = QPushButton(t("send"))
        self._send_btn.setStyleSheet(SEND_BUTTON_QSS)
        self._send_btn.setFixedWidth(70)
        self._send_btn.clicked.connect(self._on_send)
        input_layout.addWidget(self._send_btn)

        layout.addLayout(input_layout)

    def retranslate(self):
        """更新翻译"""
        self._input.setPlaceholderText(t("ask_placeholder"))
        self._send_btn.setText(t("send"))

    def _on_send(self):
        text = self._input.text().strip()
        if not text:
            return
        self._input.clear()
        self.message_sent.emit(text)

    def add_message(self, role: str, content: str):
        bubble = ChatBubble(content, is_user=(role == "user"))
        self._messages_layout.insertWidget(self._messages_layout.count() - 1, bubble)
        self._scroll_to_bottom()

    def show_typing_indicator(self):
        self._typing_indicator = TypingIndicator()
        self._messages_layout.insertWidget(self._messages_layout.count() - 1, self._typing_indicator)
        self._scroll_to_bottom()

    def hide_typing_indicator(self):
        if self._typing_indicator:
            self._typing_indicator.stop()
            self._typing_indicator.deleteLater()
            self._typing_indicator = None

    def start_streaming(self, role: str = "assistant"):
        self.hide_typing_indicator()
        bubble = ChatBubble("", is_user=False)
        self._streaming_label = bubble.findChild(QLabel)
        self._messages_layout.insertWidget(self._messages_layout.count() - 1, bubble)
        self._scroll_to_bottom()

    def append_chunk(self, chunk: str):
        if self._streaming_label:
            current = self._streaming_label.text()
            self._streaming_label.setText(current + chunk)
            self._scroll_to_bottom()

    def finish_streaming(self):
        self._streaming_label = None

    def add_error_message(self, text: str):
        label = QLabel(t("error_prefix", message=text))
        label.setStyleSheet(f"color: {COLORS.ERROR}; padding: 4px 8px; font-size: 11px;")
        label.setWordWrap(True)
        self._messages_layout.insertWidget(self._messages_layout.count() - 1, label)
        self._scroll_to_bottom()

    def show_page_indicator(self, title: str):
        label = QLabel(t("browsing", title=title))
        label.setStyleSheet(f"color: {COLORS.TEXT_MUTED}; font-size: 11px; padding: 2px 8px;")
        label.setWordWrap(True)
        self._messages_layout.insertWidget(0, label)

    def _scroll_to_bottom(self):
        QTimer.singleShot(10, lambda: self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum()
        ))

    def set_enabled(self, enabled: bool):
        self._input.setEnabled(enabled)
        self._send_btn.setEnabled(enabled)
