from pathlib import Path

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap

ASSETS_DIR = Path(__file__).parent.parent / "assets"


class SpiderWidget(QLabel):
    clicked = pyqtSignal()

    def __init__(self, size=100, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background: transparent;")

        path = ASSETS_DIR / "spider_source.jpg"
        if path.exists():
            pixmap = QPixmap(str(path))
            self.setPixmap(pixmap.scaled(
                size, size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            ))
        else:
            self.setText("🕷")

    def set_state(self, state: str):
        pass

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
