import sys
import logging

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from core.config import load_config, save_config
from core.i18n import set_language
from core.history import HistoryManager
from core.content_structurer import ContentStructurer
from browser.uia_extractor import UIAExtractor
from ai.manager import AIManager
from ui.main_window import MainWindow
from ui.chat_window import ChatWindow
from ui.utility_window import UtilityWindow
from ui.tray_icon import TrayIcon
from ui.settings_dialog import SettingsDialog

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class SpiderApp:
    def __init__(self):
        self._app = QApplication(sys.argv)
        self._app.setQuitOnLastWindowClosed(False)

        self._config = load_config()
        set_language(self._config.ui.language)

        self._window = MainWindow(self._config)
        self._chat_win = ChatWindow(self._config)
        self._utility_win = UtilityWindow(self._config)
        self._tray = TrayIcon(self._window, self._config)

        self._structurer = ContentStructurer()
        self._history = HistoryManager(
            max_pages=self._config.history.max_pages,
            persist_to_disk=self._config.history.persist_to_disk,
        )
        self._ai_manager = AIManager()
        self._uia_extractor = UIAExtractor()

        self._streaming_started = False
        self._last_user_message = ""
        self._last_content = ""

        self._init_ai_provider()
        self._connect_signals()
        self._start_monitoring()

    def run(self):
        self._tray.show()
        self._window.show()
        exit_code = self._app.exec()
        save_config(self._config)
        sys.exit(exit_code)

    def _init_ai_provider(self):
        provider = self._config.ai.provider
        provider_cfg = self._config.providers.get(provider, {})
        if isinstance(provider_cfg, dict):
            self._ai_manager.set_provider(self._config.ai, provider_cfg)

    def _connect_signals(self):
        # Pet window clicks
        self._window.left_clicked.connect(self._toggle_chat)
        self._window.right_clicked.connect(self._toggle_utility)

        # Chat window
        self._chat_win.message_submitted.connect(self._on_user_message)

        # Utility window
        self._utility_win.settings_requested.connect(self._on_settings)

        # Tray
        self._tray.settings_requested.connect(self._on_settings)
        self._tray.quit_requested.connect(self._on_quit)

        # AI manager
        self._ai_manager.response_chunk.connect(self._on_ai_chunk)
        self._ai_manager.response_complete.connect(self._on_ai_complete)
        self._ai_manager.error.connect(self._on_ai_error)

    def _toggle_chat(self):
        if self._chat_win.isVisible():
            self._chat_win.hide()
        else:
            self._chat_win.show()
            self._chat_win.raise_()
            self._chat_win.activateWindow()

    def _toggle_utility(self):
        if self._utility_win.isVisible():
            self._utility_win.hide()
        else:
            self._utility_win.show()
            self._utility_win.raise_()
            self._utility_win.activateWindow()

    def _start_monitoring(self):
        from PyQt6.QtCore import QTimer
        self._monitor_timer = QTimer()
        self._monitor_timer.timeout.connect(self._poll_content)
        self._monitor_timer.start(int(self._config.browser.poll_interval * 1000))

    def _poll_content(self):
        if not self._config.browser.auto_crawl:
            return
        try:
            title, content = self._uia_extractor.extract_text_from_browser()
            if content and content != self._last_content:
                self._last_content = content
                self._on_page_changed(title, content)
        except Exception as e:
            logger.error(f"Content poll error: {e}")

    def _on_page_changed(self, title: str, content: str):
        self._window.set_spider_state("crawling")
        self._tray.update_page_title(title)

        try:
            html = (
                f"<html><head><title>{title}</title></head>"
                f"<body><pre>{content}</pre></body></html>"
            )
            page = self._structurer.structure(html, url="")
            page.title = title
            page.raw_text = content
            page = self._structurer.truncate_to_budget(
                page, self._config.browser.max_content_tokens
            )
            self._history.add_page(page)

            display_title = title or "Unknown Page"
            self._chat_win.show_page_indicator(display_title[:60])
            self._utility_win.add_page(display_title[:80])
            self._window.set_spider_state("happy")
        except Exception as e:
            logger.error(f"Content processing error: {e}")
            self._window.set_spider_state("idle")

    def _on_user_message(self, text: str):
        self._last_user_message = text
        self._chat_win.add_user_message(text)
        self._window.set_spider_state("thinking")
        self._chat_win.show_typing_indicator()

        context = self._history.get_current_page()
        history_summary = self._history.get_history_summary()
        self._ai_manager.send_message(text, context, history_summary)

    def _on_ai_chunk(self, chunk: str):
        if not self._streaming_started:
            self._chat_win.hide_typing_indicator()
            self._chat_win.start_ai_streaming()
            self._streaming_started = True
        self._chat_win.append_ai_chunk(chunk)

    def _on_ai_complete(self, full_response: str):
        self._chat_win.finish_ai_streaming()
        self._window.set_spider_state("happy")
        self._history.add_conversation(self._last_user_message, full_response)
        self._streaming_started = False

    def _on_ai_error(self, msg: str):
        self._chat_win.hide_typing_indicator()
        self._chat_win.add_error_message(msg)
        self._window.set_spider_state("idle")
        self._streaming_started = False

    def _on_settings(self):
        dialog = SettingsDialog(self._config, self._window)
        dialog.config_changed.connect(self._on_config_changed)
        dialog.exec()

    def _on_config_changed(self):
        self._init_ai_provider()
        self._window.setWindowOpacity(self._config.ui.opacity)
        self._monitor_timer.setInterval(int(self._config.browser.poll_interval * 1000))
        self._tray.retranslate()
        self._chat_win.retranslate()

    def _on_quit(self):
        save_config(self._config)
        self._app.quit()


def main():
    spider = SpiderApp()
    spider.run()


if __name__ == "__main__":
    main()
