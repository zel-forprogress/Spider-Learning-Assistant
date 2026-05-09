import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


class UIAExtractor:
    """通过 Windows UI Automation 读取浏览器可见文本内容"""

    def __init__(self):
        self._last_content = ""
        self._last_window_title = ""

    def get_foreground_info(self) -> dict:
        """获取当前前台窗口信息"""
        try:
            import uiautomation as auto
            window = auto.GetForegroundControl()
            if not window:
                return {}

            return {
                "title": window.Name or "",
                "class_name": window.ClassName or "",
                "process_id": window.ProcessId,
                "control_type": window.ControlTypeName,
            }
        except Exception as e:
            logger.error(f"Failed to get foreground info: {e}")
            return {}

    def extract_text_from_browser(self) -> tuple[str, str]:
        """从当前浏览器窗口提取文本内容

        Returns:
            (title, content) 元组
        """
        try:
            import uiautomation as auto

            window = auto.GetForegroundControl()
            if not window:
                return "", ""

            title = window.Name or ""

            # 收集所有文本元素
            texts = []
            self._collect_text_elements(window, texts, depth=0, max_depth=15)

            content = "\n".join(texts)

            # 去重和过滤
            content = self._clean_content(content)

            return title, content

        except ImportError:
            logger.error("uiautomation not installed")
            return "", ""
        except Exception as e:
            logger.error(f"UIA extraction failed: {e}")
            return "", ""

    def _collect_text_elements(self, element, texts: list, depth: int, max_depth: int):
        """递归收集文本元素"""
        if depth > max_depth:
            return

        try:
            # 读取当前元素的文本
            name = element.Name
            if name and len(name.strip()) > 2:
                # 过滤掉一些无用的UI文本
                if not self._is_ui_noise(name):
                    texts.append(name.strip())

            # 读取 Value（用于输入框等）
            try:
                value = element.GetValuePattern().Value if element.GetValuePattern() else ""
                if value and len(value.strip()) > 2 and value.strip() != name:
                    texts.append(value.strip())
            except Exception:
                pass

            # 递归子元素
            for child in element.GetChildren():
                self._collect_text_elements(child, texts, depth + 1, max_depth)

        except Exception:
            pass

    def _is_ui_noise(self, text: str) -> bool:
        """判断是否为UI噪音文本"""
        noise_patterns = [
            "菜单", "Menu", "关闭", "Close", "最小化", "Minimize",
            "最大化", "Maximize", "还原", "Restore", "文件", "File",
            "编辑", "Edit", "查看", "View", "帮助", "Help",
            "前进", "后退", "刷新", "Reload", "停止", "Stop",
            "⭐", "☆", "🔍", "⚙", "▼", "▶", "◀", "▲",
        ]
        text_lower = text.lower().strip()
        if len(text_lower) < 3:
            return True
        for pattern in noise_patterns:
            if pattern.lower() in text_lower:
                return True
        return False

    def _clean_content(self, content: str) -> str:
        """清理提取的文本内容"""
        lines = content.split("\n")
        cleaned = []
        seen = set()

        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue
            # 去重
            if line not in seen:
                seen.add(line)
                cleaned.append(line)

        return "\n".join(cleaned)

    def has_content_changed(self, new_content: str) -> bool:
        """检查内容是否发生变化"""
        if new_content != self._last_content:
            self._last_content = new_content
            return True
        return False


class ScreenCapture:
    """屏幕截图和OCR（可选增强）"""

    def __init__(self):
        self._ocr_available = False
        try:
            import pytesseract
            self._ocr_available = True
        except ImportError:
            logger.info("pytesseract not installed, OCR disabled")

    def capture_and_ocr(self, region: Optional[tuple] = None) -> str:
        """截取屏幕区域并进行OCR识别

        Args:
            region: (x, y, width, height) 截图区域，None表示全屏
        """
        if not self._ocr_available:
            return ""

        try:
            from PIL import ImageGrab
            import pytesseract

            screenshot = ImageGrab.grab(bbox=region)
            text = pytesseract.image_to_string(screenshot, lang="chi_sim+eng")
            return text.strip()
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return ""
