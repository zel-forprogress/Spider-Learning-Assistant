from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QMouseEvent

from ui.spider_widget import SpiderWidget
from ui.styles import COLORS, MAIN_WINDOW_QSS


class MainWindow(QWidget):
    left_clicked = pyqtSignal()
    right_clicked = pyqtSignal()

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
                self.right_clicked.emit()

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
