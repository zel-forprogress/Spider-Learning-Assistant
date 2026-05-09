from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, QPoint, QRect, pyqtSignal
from PyQt6.QtGui import QMouseEvent

from ui.spider_widget import SpiderWidget
from ui.chat_widget import ChatWidget
from ui.styles import COLORS, MAIN_WINDOW_QSS


class MainWindow(QWidget):
    settings_clicked = pyqtSignal()
    message_submitted = pyqtSignal(str)

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self._config = config
        self._collapsed = config.ui.start_collapsed
        self._drag_pos = None
        self._drag_start_pos = None
        self._expanded_geometry = None
        self._is_dragging = False

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(MAIN_WINDOW_QSS)

        self._setup_ui()
        self._restore_geometry()
        self._update_size()

    def _setup_ui(self):
        self._root_layout = QVBoxLayout(self)
        self._root_layout.setContentsMargins(8, 8, 8, 8)
        self._root_layout.setSpacing(0)

        title_bar = QHBoxLayout()
        title_bar.setContentsMargins(4, 0, 4, 0)
        title_bar.setSpacing(4)

        self._settings_btn = QPushButton("⚙")
        self._settings_btn.setFixedSize(28, 28)
        self._settings_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS.TEXT_SECONDARY};
                border: none;
                font-size: 16px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {COLORS.BORDER};
            }}
        """)
        self._settings_btn.clicked.connect(self.settings_clicked.emit)
        title_bar.addWidget(self._settings_btn)

        title_bar.addStretch()

        self._collapse_btn = QPushButton("—")
        self._collapse_btn.setFixedSize(28, 28)
        self._collapse_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS.TEXT_SECONDARY};
                border: none;
                font-size: 14px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {COLORS.BORDER};
            }}
        """)
        self._collapse_btn.clicked.connect(self.toggle_collapse)
        title_bar.addWidget(self._collapse_btn)

        self._root_layout.addLayout(title_bar)

        self._spider = SpiderWidget(size=100)
        self._root_layout.addWidget(self._spider, 0, Qt.AlignmentFlag.AlignCenter)

        self._chat = ChatWidget()
        self._chat.message_sent.connect(self.message_submitted.emit)
        self._root_layout.addWidget(self._chat, 1)

    def toggle_collapse(self):
        self._collapsed = not self._collapsed
        self._update_size()

    def _update_size(self):
        if self._collapsed:
            self._chat.hide()
            self._settings_btn.hide()
            self._collapse_btn.hide()
            w = self._config.ui.collapsed_width
            h = self._config.ui.collapsed_height
        else:
            self._chat.show()
            self._settings_btn.show()
            self._collapse_btn.show()
            w = self._config.ui.window_width
            h = self._config.ui.window_height

        screen = self.screen()
        if screen:
            screen_geo = screen.availableGeometry()
            x = self._config.ui.window_x
            y = self._config.ui.window_y
            if x + w > screen_geo.right():
                x = screen_geo.right() - w
            if y + h > screen_geo.bottom():
                y = screen_geo.bottom() - h
            if x < screen_geo.left():
                x = screen_geo.left()
            if y < screen_geo.top():
                y = screen_geo.top()
            self.move(x, y)

        self.setFixedSize(w, h)

    def _restore_geometry(self):
        self.move(self._config.ui.window_x, self._config.ui.window_y)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._drag_start_pos = event.position().toPoint()
            self._is_dragging = False
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            current_pos = event.position().toPoint()
            if self._drag_start_pos:
                dx = current_pos.x() - self._drag_start_pos.x()
                dy = current_pos.y() - self._drag_start_pos.y()
                if abs(dx) > 5 or abs(dy) > 5:
                    self._is_dragging = True

            if self._is_dragging:
                new_pos = event.globalPosition().toPoint() - self._drag_pos
                self.move(new_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._drag_pos is not None:
            if not self._is_dragging:
                # 没有拖拽，视为点击 - 切换折叠
                self.toggle_collapse()
            else:
                self._config.ui.window_x = self.x()
                self._config.ui.window_y = self.y()
        self._drag_pos = None
        self._drag_start_pos = None
        self._is_dragging = False
        super().mouseReleaseEvent(event)

    def set_spider_state(self, state: str):
        self._spider.set_state(state)

    def retranslate(self):
        """更新翻译"""
        self._chat.retranslate()

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

    def closeEvent(self, event):
        self._config.ui.window_x = self.x()
        self._config.ui.window_y = self.y()
        self._config.ui.window_width = self.width()
        self._config.ui.window_height = self.height()
        self._config.ui.start_collapsed = self._collapsed
        self.hide()
        event.ignore()
