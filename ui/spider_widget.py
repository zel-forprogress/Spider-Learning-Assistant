from pathlib import Path
import random

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
    "wave": "spider_wave.gif",
    "jump": "spider_jump.gif",
    "spin": "spider_spin.gif",
    "nod": "spider_nod.gif",
}

INTERACTION_STATES = ["wave", "jump", "spin", "nod"]


class SpiderWidget(QLabel):
    clicked = pyqtSignal()
    interaction_done = pyqtSignal()

    def __init__(self, size=100, parent=None):
        super().__init__(parent)
        self._size = size
        self._state = "idle"
        self._movie = None
        self._is_interacting = False

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

        # Auto-return to idle after interaction animation finishes
        if state in INTERACTION_STATES:
            self._is_interacting = True
            duration = self._movie.frameRect().width() * self._movie.frameCount()
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(max(duration, 800), self._on_interaction_done)

    def _on_interaction_done(self):
        self._is_interacting = False
        self._state = "idle"
        self._load_movie("idle")
        self.interaction_done.emit()

    def set_state(self, state: str):
        if self._is_interacting:
            return
        if state == self._state:
            return
        self._state = state
        self._load_movie(state)

    def play_interaction(self, state: str = None):
        """Play a random or specified interaction animation."""
        if self._is_interacting:
            return
        if state is None:
            state = random.choice(INTERACTION_STATES)
        self._state = state
        self._load_movie(state)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
