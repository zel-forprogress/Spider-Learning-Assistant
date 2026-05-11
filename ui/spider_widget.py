from pathlib import Path

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QMovie

from ui.styles import COLORS

ASSETS_DIR = Path(__file__).parent.parent / "assets"

GIF_STATES = {
    "idle": "spider_idle.gif",
    "crawling": "spider_crawling.gif",
    "thinking": "spider_thinking.gif",
    "happy": "spider_happy.gif",
}


class SpiderWidget(QLabel):
    clicked = pyqtSignal()

    def __init__(self, size=100, parent=None):
        super().__init__(parent)
        self._size = size
        self._state = "idle"
        self._movie = None

        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background: transparent;")

        self._load_movie("idle")

    def _load_movie(self, state: str):
        filename = GIF_STATES.get(state)
        if not filename:
            return
        path = ASSETS_DIR / filename
        if not path.exists():
            self.setText("🕷")
            return

        if self._movie:
            self._movie.stop()

        self._movie = QMovie(str(path))
        self._movie.setScaledSize(QSize(self._size, self._size))
        self.setMovie(self._movie)
        self._movie.start()

    def set_state(self, state: str):
        if state == self._state:
            return
        self._state = state
        self._load_movie(state)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
