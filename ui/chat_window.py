from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal

from ui.chat_widget import ChatWidget
from ui.styles import COLORS, MAIN_WINDOW_QSS


class ChatWindow(QWidget):
    message_submitted = pyqtSignal(str)

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self._config = config
        self._drag_pos = None

        self.setWindowTitle("Spider Chat")
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(MAIN_WINDOW_QSS)
        self.setMinimumSize(360, 480)
        self.resize(380, 520)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._chat = ChatWidget()
        self._chat.message_sent.connect(self.message_submitted.emit)
        layout.addWidget(self._chat)

    def add_user_message(self, text: str):
        self._chat.add_message("user", text)

    def add_ai_message(self, text: str):
        self._chat.add_message("assistant", text)

    def start_ai_streaming(self):
        self._chat.start_streaming()

    def append_ai_chunk(self, chunk: str):
        self._chat.append_chunk(chunk)

    def finish_ai_streaming(self):
        self._chat.finish_streaming()

    def show_typing_indicator(self):
        self._chat.show_typing_indicator()

    def hide_typing_indicator(self):
        self._chat.hide_typing_indicator()

    def add_error_message(self, text: str):
        self._chat.add_error_message(text)

    def show_page_indicator(self, title: str):
        self._chat.show_page_indicator(title)

    def retranslate(self):
        self._chat.retranslate()

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
