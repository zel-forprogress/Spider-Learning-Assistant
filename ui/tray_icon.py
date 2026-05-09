from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import pyqtSignal, QObject
from pathlib import Path

from core.i18n import t

ASSETS_DIR = Path(__file__).parent.parent / "assets"


class TrayIcon(QSystemTrayIcon):
    show_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    def __init__(self, window, config, parent=None):
        super().__init__(parent)
        self._window = window
        self._config = config

        icon_path = ASSETS_DIR / "tray_icon.svg"
        if icon_path.exists():
            self.setIcon(QIcon(str(icon_path)))
        else:
            self.setIcon(QIcon.fromTheme("help-browser"))

        self.setToolTip(t("app_name"))
        self._setup_menu()
        self.activated.connect(self._on_activated)

    def _setup_menu(self):
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #1e293b;
                color: #e2e8f0;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 4px;
            }
            QMenu::item:selected {
                background-color: #2563EB;
                border-radius: 2px;
            }
        """)

        self._show_action = menu.addAction(t("show_window"))
        self._show_action.triggered.connect(self._on_show)

        self._settings_action = menu.addAction(t("settings") + "...")
        self._settings_action.triggered.connect(self._on_settings)

        menu.addSeparator()

        self._page_action = menu.addAction(t("no_page"))
        self._page_action.setEnabled(False)

        menu.addSeparator()

        self._quit_action = menu.addAction(t("quit"))
        self._quit_action.triggered.connect(self._on_quit)

        self.setContextMenu(menu)
        self._menu = menu

    def retranslate(self):
        """更新翻译"""
        self.setToolTip(t("app_name"))
        self._show_action.setText(t("show_window"))
        self._settings_action.setText(t("settings") + "...")
        self._quit_action.setText(t("quit"))
        if not self._page_action.isEnabled():
            self._page_action.setText(t("no_page"))

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._on_show()

    def _on_show(self):
        if self._window.isVisible():
            self._window.hide()
        else:
            self._window.show()
            self._window.raise_()
            self._window.activateWindow()

    def _on_settings(self):
        self.settings_requested.emit()

    def _on_quit(self):
        self.quit_requested.emit()

    def update_page_title(self, title: str):
        display = title[:30] + "..." if len(title) > 30 else title
        self._page_action.setText(t("browsing", title=display))
