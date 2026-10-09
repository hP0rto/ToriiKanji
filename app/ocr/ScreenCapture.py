"""
Screen capture overlay for ToriiKanji.
Provides a fullscreen overlay for region selection, implemented in pure PyQt6.
"""

from datetime import datetime

import pyautogui
from PyQt6.QtCore import QEventLoop, QRect, Qt, QTimer
from PyQt6.QtGui import QColor, QImage, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QApplication, QWidget

from utils.helpers import get_app_name


class ScreenCapture(QWidget):
    """Fullscreen overlay for selecting a screen region to capture."""

    def __init__(self, background_image):
        super().__init__()
        self._image = background_image  # PIL image of the full primary screen

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setCursor(Qt.CursorShape.CrossCursor)

        rgba = self._image.convert("RGBA")
        qimage = QImage(
            rgba.tobytes("raw", "RGBA"), rgba.width, rgba.height,
            QImage.Format.Format_RGBA8888
        )
        self._background = QPixmap.fromImage(qimage.copy())

        self._start = None
        self._end = None
        self.cancelled = True
        self.screenshot = None
        self._loop = QEventLoop()

    # ─── Public API ──────────────────────────────────────────────────────────

    @staticmethod
    def select_region():
        """
        Show the overlay and block (local event loop) until the user selects
        a region or cancels with Escape.

        Returns:
            dict with 'captured_app_name', 'file_name', 'screenshot' (PIL image),
            or None if cancelled.
        """
        captured_app_name = get_app_name()
        print(f"ScreenCapture: Detected focused app -> {captured_app_name}")

        # Give the main window a moment to actually hide before grabbing the screen
        wait = QEventLoop()
        QTimer.singleShot(150, wait.quit)
        wait.exec()

        overlay = ScreenCapture(pyautogui.screenshot())
        overlay.setGeometry(QApplication.primaryScreen().geometry())
        overlay.showFullScreen()
        overlay.activateWindow()
        overlay.raise_()
        overlay._loop.exec()
        overlay.deleteLater()

        if overlay.cancelled or overlay.screenshot is None:
            return None

        return {
            'captured_app_name': captured_app_name,
            'file_name': datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
            'screenshot': overlay.screenshot,
        }

    # ─── Painting ────────────────────────────────────────────────────────────

    def _selection_rect(self):
        if self._start is None or self._end is None:
            return None
        return QRect(self._start, self._end).normalized()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self._background)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 110))

        sel = self._selection_rect()
        if sel and sel.width() > 0 and sel.height() > 0:
            # Reveal the undimmed screen inside the selection
            scale_x = self._background.width() / self.width()
            scale_y = self._background.height() / self.height()
            source = QRect(
                int(sel.x() * scale_x), int(sel.y() * scale_y),
                int(sel.width() * scale_x), int(sel.height() * scale_y)
            )
            painter.drawPixmap(sel, self._background, source)
            painter.setPen(QPen(QColor("#e53935"), 2))
            painter.drawRect(sel)

    # ─── Input ───────────────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._start = event.position().toPoint()
            self._end = self._start
            self.update()

    def mouseMoveEvent(self, event):
        if self._start is not None:
            self._end = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton or self._start is None:
            return
        self._end = event.position().toPoint()
        sel = self._selection_rect()

        if sel is None or sel.width() < 2 or sel.height() < 2:
            # Ignore accidental clicks; allow a new selection
            self._start = self._end = None
            self.update()
            return

        # Map logical widget coordinates to screenshot pixels (handles DPI scaling)
        scale_x = self._image.width / self.width()
        scale_y = self._image.height / self.height()
        box = (
            int(sel.left() * scale_x), int(sel.top() * scale_y),
            int((sel.right() + 1) * scale_x), int((sel.bottom() + 1) * scale_y),
        )
        self.screenshot = self._image.crop(box)
        self.cancelled = False
        self._finish()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.cancelled = True
            self._finish()

    def _finish(self):
        self.hide()
        self._loop.quit()
