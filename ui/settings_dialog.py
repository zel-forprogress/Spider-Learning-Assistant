from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QComboBox, QPushButton, QCheckBox,
    QSlider, QFormLayout,
)
from PyQt6.QtCore import Qt, pyqtSignal

from core.config import Config, save_config
from core.i18n import t, set_language, get_available_languages
from ui.styles import COLORS, SETTINGS_QSS


class SettingsDialog(QDialog):
    config_changed = pyqtSignal()

    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self._config = config
        self._setup_ui()
        self._retranslate()

    def _setup_ui(self):
        self.setMinimumSize(450, 350)
        self.setStyleSheet(SETTINGS_QSS)

        layout = QVBoxLayout(self)

        tabs = QTabWidget()
        tabs.addTab(self._create_general_tab(), "general")
        tabs.addTab(self._create_ai_tab(), "ai")
        tabs.addTab(self._create_capture_tab(), "capture")
        self._tabs = tabs
        layout.addWidget(tabs)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self._save_btn = QPushButton("save")
        self._save_btn.setFixedWidth(80)
        self._save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(self._save_btn)

        self._cancel_btn = QPushButton("cancel")
        self._cancel_btn.setFixedWidth(80)
        self._cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self._cancel_btn)

        layout.addLayout(btn_layout)

    def _create_general_tab(self) -> QWidget:
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(12)

        # 语言选择
        self._lang_combo = QComboBox()
        for lang in get_available_languages():
            self._lang_combo.addItem(lang["name"], lang["code"])
        # 设置当前语言
        for i, lang in enumerate(get_available_languages()):
            if lang["code"] == self._config.ui.language:
                self._lang_combo.setCurrentIndex(i)
                break
        self._lang_combo.currentIndexChanged.connect(self._on_language_changed)
        layout.addRow("language:", self._lang_combo)

        self._opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self._opacity_slider.setRange(30, 100)
        self._opacity_slider.setValue(int(self._config.ui.opacity * 100))
        self._opacity_slider.setTickPosition(QSlider.TickPosition.NoTicks)
        layout.addRow("opacity:", self._opacity_slider)

        self._start_collapsed_check = QCheckBox()
        self._start_collapsed_check.setChecked(self._config.ui.start_collapsed)
        layout.addRow("start_collapsed:", self._start_collapsed_check)

        return widget

    def _create_ai_tab(self) -> QWidget:
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(12)

        self._provider_combo = QComboBox()
        self._provider_combo.addItems(["openai", "claude", "ollama"])
        self._provider_combo.setCurrentText(self._config.ai.provider)
        self._provider_combo.currentTextChanged.connect(self._on_provider_changed)
        layout.addRow("provider:", self._provider_combo)

        self._api_key_input = QLineEdit()
        self._api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        provider_cfg = self._config.providers.get(self._config.ai.provider, {})
        self._api_key_input.setText(provider_cfg.get("api_key", "") if isinstance(provider_cfg, dict) else "")
        layout.addRow("api_key:", self._api_key_input)

        self._model_combo = QComboBox()
        self._populate_models(self._config.ai.provider)
        self._model_combo.setCurrentText(self._config.ai.model)
        layout.addRow("model:", self._model_combo)

        return widget

    def _create_capture_tab(self) -> QWidget:
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(12)

        self._info_label = QLabel()
        self._info_label.setWordWrap(True)
        self._info_label.setStyleSheet("color: #94a3b8; font-size: 12px; padding: 8px;")
        layout.addRow("", self._info_label)

        self._auto_crawl_check = QCheckBox()
        self._auto_crawl_check.setChecked(self._config.browser.auto_crawl)
        layout.addRow("auto_capture:", self._auto_crawl_check)

        return widget

    def _on_language_changed(self, index: int):
        lang_code = self._lang_combo.currentData()
        set_language(lang_code)
        self._config.ui.language = lang_code
        self._retranslate()

    def _retranslate(self):
        """更新所有文本为当前语言"""
        self.setWindowTitle(t("app_name") + " - " + t("settings"))

        # 更新标签页标题
        self._tabs.setTabText(0, t("tab_general"))
        self._tabs.setTabText(1, t("tab_ai"))
        self._tabs.setTabText(2, t("tab_capture"))

        # 更新按钮
        self._save_btn.setText(t("save"))
        self._cancel_btn.setText(t("cancel"))

        # 更新 General 标签
        general_tab = self._tabs.widget(0)
        general_layout = general_tab.layout()
        if general_layout:
            general_layout.labelForField(self._lang_combo).setText(t("language") + ":")
            general_layout.labelForField(self._opacity_slider).setText(t("window_opacity") + ":")
            general_layout.labelForField(self._start_collapsed_check).setText(t("start_collapsed"))

        # 更新 AI 标签
        ai_tab = self._tabs.widget(1)
        ai_layout = ai_tab.layout()
        if ai_layout:
            ai_layout.labelForField(self._provider_combo).setText(t("provider") + ":")
            ai_layout.labelForField(self._api_key_input).setText(t("api_key") + ":")
            ai_layout.labelForField(self._model_combo).setText(t("model") + ":")
            self._api_key_input.setPlaceholderText(t("api_key_placeholder"))

        # 更新 Capture 标签
        self._info_label.setText(t("capture_mode_info"))
        capture_tab = self._tabs.widget(2)
        capture_layout = capture_tab.layout()
        if capture_layout:
            capture_layout.labelForField(self._auto_crawl_check).setText(t("auto_capture"))

    def _on_provider_changed(self, provider: str):
        self._populate_models(provider)
        provider_cfg = self._config.providers.get(provider, {})
        api_key = provider_cfg.get("api_key", "") if isinstance(provider_cfg, dict) else ""
        self._api_key_input.setText(api_key)
        default_model = provider_cfg.get("default_model", "") if isinstance(provider_cfg, dict) else ""
        self._model_combo.setCurrentText(default_model)

    def _populate_models(self, provider: str):
        self._model_combo.clear()
        provider_cfg = self._config.providers.get(provider, {})
        if isinstance(provider_cfg, dict):
            models = provider_cfg.get("available_models", [])
            self._model_combo.addItems(models)

    def _on_save(self):
        self._config.ai.provider = self._provider_combo.currentText()
        self._config.ai.model = self._model_combo.currentText()
        self._config.browser.auto_crawl = self._auto_crawl_check.isChecked()
        self._config.ui.opacity = self._opacity_slider.value() / 100.0
        self._config.ui.start_collapsed = self._start_collapsed_check.isChecked()

        provider = self._config.ai.provider
        if provider not in self._config.providers:
            self._config.providers[provider] = {}
        if isinstance(self._config.providers[provider], dict):
            self._config.providers[provider]["api_key"] = self._api_key_input.text()

        save_config(self._config)
        self.config_changed.emit()
        self.accept()
