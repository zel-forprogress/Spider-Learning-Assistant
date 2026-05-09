from pathlib import Path

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap, QPainter

from ui.styles import COLORS

ASSETS_DIR = Path(__file__).parent.parent / "assets"

STATES = {
    "idle": "spider_idle.svg",
    "crawling": "spider_crawling.svg",
    "thinking": "spider_thinking.svg",
    "happy": "spider_happy.svg",
}


class SpiderWidget(QLabel):
    clicked = pyqtSignal()

    def __init__(self, size=100, parent=None):
        super().__init__(parent)
        self._size = size
        self._state = "idle"
        self._pixmap_cache = {}
        self._opacity = 1.0

        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background: transparent;")

        self._load_pixmaps()
        self._set_state_image("idle")

        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._on_anim_tick)
        self._anim_tick = 0
        self._anim_timer.start(3000)

    def _load_pixmaps(self):
        for state, filename in STATES.items():
            path = ASSETS_DIR / filename
            if path.exists():
                pixmap = QPixmap(str(path))
                self._pixmap_cache[state] = pixmap.scaled(
                    self._size, self._size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            else:
                self._pixmap_cache[state] = None

    def _set_state_image(self, state: str):
        pixmap = self._pixmap_cache.get(state)
        if pixmap:
            self.setPixmap(pixmap)
        else:
            self.setText("🕷")

    def set_state(self, state: str):
        if state == self._state:
            return
        self._state = state
        self._anim_tick = 0
        self._set_state_image(state)

        if state == "idle":
            self._anim_timer.start(3000)
        elif state == "crawling":
            self._anim_timer.start(200)
        elif state == "thinking":
            self._anim_timer.start(150)
        elif state == "happy":
            self._anim_timer.start(200)
            QTimer.singleShot(2000, lambda: self.set_state("idle"))

    def _on_anim_tick(self):
        self._anim_tick += 1
        if self._state == "crawling":
            alt = "idle" if self._anim_tick % 2 == 0 else "crawling"
            self._set_state_image(alt)
        elif self._state == "thinking":
            opacity = 0.5 if self._anim_tick % 2 == 0 else 1.0
            self._set_thinking_opacity(opacity)
        elif self._state == "happy":
            if self._anim_tick % 2 == 0:
                self._set_state_image("happy")
            else:
                self._set_state_image("idle")
        elif self._state == "idle":
            # Breathing effect: subtle opacity pulse
            opacity = 0.85 if self._anim_tick % 2 == 0 else 1.0
            self._set_idle_opacity(opacity)

    def _set_thinking_opacity(self, opacity: float):
        pixmap = self._pixmap_cache.get("thinking")
        if pixmap:
            from PyQt6.QtGui import QPixmap as QPix
            faded = QPix(pixmap.size())
            faded.fill(Qt.GlobalColor.transparent)
            painter = QPainter(faded)
            painter.setOpacity(opacity)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
            self.setPixmap(faded)

    def _set_idle_opacity(self, opacity: float):
        pixmap = self._pixmap_cache.get("idle")
        if pixmap:
            from PyQt6.QtGui import QPixmap as QPix
            faded = QPix(pixmap.size())
            faded.fill(Qt.GlobalColor.transparent)
            painter = QPainter(faded)
            painter.setOpacity(opacity)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
            self.setPixmap(faded)

    def mousePressEvent(self, event):
        # 不阻止事件传播，让主窗口处理拖拽和点击
        super().mousePressEvent(event)
