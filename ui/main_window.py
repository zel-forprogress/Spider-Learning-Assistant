from PyQt6.QtWidgets import QWidget, QMenu
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QMouseEvent

from core.i18n import t
from ui.spider_widget import SpiderWidget
from ui.styles import COLORS, MAIN_WINDOW_QSS


class MainWindow(QWidget):
    chat_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self._config = config
        self._drag_pos = None
        self._drag_start_pos = None
        self._is_dragging = False

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(MAIN_WINDOW_QSS)

        size = config.ui.collapsed_width
        self.setFixedSize(size, size)

        layout = self.layout() or __import__("PyQt6.QtWidgets", fromlist=["QVBoxLayout"]).QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._spider = SpiderWidget(size=size - 16)
        layout.addWidget(self._spider, 0, Qt.AlignmentFlag.AlignCenter)

        screen = self.screen()
        if screen:
            geo = screen.availableGeometry()
            x = self._config.ui.window_x
            y = self._config.ui.window_y
            if x + size > geo.right():
                x = geo.right() - size
            if y + size > geo.bottom():
                y = geo.bottom() - size
            if x < geo.left():
                x = geo.left()
            if y < geo.top():
                y = geo.top()
            self.move(x, y)

    def set_spider_state(self, state: str):
        self._spider.set_state(state)

    def _show_context_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {COLORS.BG_SECONDARY};
                color: {COLORS.TEXT_PRIMARY};
                border: 1px solid {COLORS.BORDER};
                border-radius: 6px;
                padding: 4px;
                font-size: 13px;
            }}
            QMenu::item {{
                padding: 8px 24px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {COLORS.ACCENT};
            }}
        """)

        chat_action = menu.addAction("💬 " + t("chat"))
        chat_action.triggered.connect(self.chat_requested.emit)

        settings_action = menu.addAction("⚙ " + t("settings"))
        settings_action.triggered.connect(self.settings_requested.emit)

        menu.addSeparator()

        quit_action = menu.addAction("🚪 " + t("quit"))
        quit_action.triggered.connect(self.quit_requested.emit)

        menu.exec(self.mapToGlobal(pos))

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton):
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._drag_start_pos = event.position().toPoint()
            self._is_dragging = False
            self._click_button = event.button()
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
        if self._drag_pos is not None and not self._is_dragging:
            if self._click_button == Qt.MouseButton.LeftButton:
                self.left_clicked.emit()
            elif self._click_button == Qt.MouseButton.RightButton:
                self._show_context_menu(event.position().toPoint())

        if not self._is_dragging and self._drag_pos is not None:
            self._config.ui.window_x = self.x()
            self._config.ui.window_y = self.y()

        self._drag_pos = None
        self._drag_start_pos = None
        self._is_dragging = False
        super().mouseReleaseEvent(event)

    def closeEvent(self, event):
        self._config.ui.window_x = self.x()
        self._config.ui.window_y = self.y()
        self.hide()
        event.ignore()
