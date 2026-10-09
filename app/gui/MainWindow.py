"""
Main window for ToriiKanji.
Acts as the application shell, connecting services to the UI.
"""

from PyQt6.QtCore import QRect, QSize, Qt, pyqtSlot
from PyQt6.QtGui import QAction, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QGraphicsOpacityEffect,
    QLabel,
    QMenu,
    QMessageBox,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from core.services.analytics_service import AnalyticsService
from core.services.capture_service import CaptureService
from core.services.hotkey_services import CustomHotkeyEvent, config_hotkey
from core.services.kanji_service import KanjiService
from core.services.media_service import MediaService
from core.services.ocr_service import OcrService
from core.services.setting_services import SettingsService
from gui.components.CustomTabWidget import CustomTabWidget
from gui.components.MediaConfirmationDialog import MediaConfirmationDialog
from utils.i18n import t
from utils.paths import BACKGROUND_IMG, ICON


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.threads = []
        self.workers = []

        # Initialize services (single instances shared across the app)
        self.ocr_service = OcrService()
        self.kanji_service = KanjiService()
        self.capture_service = CaptureService(self.kanji_service, self.ocr_service)
        self.setting_service = SettingsService()
        self.media_service = MediaService()
        self.analytics_service = AnalyticsService()

        # Setup hotkeys and system tray
        config_hotkey(self)
        self.config_tray()
        self.apply_display_mode()

        # Connect capture service signals (decoupled — no direct window reference)
        self.capture_service.ocr_finished.connect(self.on_ocr_finished)
        self.capture_service.capture_saved.connect(self.on_capture_saved)
        self.capture_service.error_occurred.connect(self.on_error)
        self.capture_service.media_confirmation_required.connect(self.initiate_media_confirmation)
        self.capture_service.hide_window.connect(self.hide)
        self.capture_service.show_window.connect(self._show_and_raise)

        # Build the tab widget
        self.custom_tab = CustomTabWidget(
            self, self.capture_service, self.media_service,
            self.kanji_service, self.analytics_service
        )
        self.custom_tab.overlay_panel.save_requested.connect(self.on_manual_save_requested)

        # Connect capture_saved to overlay for button state updates
        try:
            self.capture_service.capture_saved.connect(self.custom_tab.overlay_panel.on_capture_saved)
        except Exception:
            pass

        layout = QVBoxLayout()
        layout.addWidget(self.custom_tab)
        self.setLayout(layout)
        self.show()

    # ─── Capture Flow Handlers ───────────────────────────────────────────────

    def initialize_capture(self):
        """Start the capture flow, passing current visibility state."""
        self.capture_service.start_full_capture_flow(
            window_visible=self.isVisible()
        )

    @pyqtSlot(dict)
    def on_ocr_finished(self, result):
        """Handle OCR completion — show window and display results."""
        self._show_and_raise()
        print("OCR result received:", result)
        self.custom_tab.show_capture(result)

    @pyqtSlot(int)
    def on_capture_saved(self, capture_id):
        """Handle capture saved — show tray notification and refresh collection."""
        self.tray_icon.showMessage("Capture", t('capture_saved', id=capture_id))
        self.custom_tab.collection_panel.load_captures()

    @pyqtSlot(str)
    def on_error(self, msg):
        """Handle errors from the capture service."""
        self._show_and_raise()
        print("Service error:", msg)
        QMessageBox.critical(self, "Error", f"An error occurred:\n{msg}")

    @pyqtSlot(dict)
    def on_manual_save_requested(self, result):
        """Handle manual save button click from the OverlayPanel."""
        print(f"MainWindow: Manual save requested. result: {result}")
        media_id = result.get('media_id')
        if media_id is not None:
            print("Manual save authorized. Calling service.")
            self.capture_service.start_save_flow(result, media_id, is_manual=True)
        else:
            print("Error: Manual save attempted without media_id.")

    def initiate_media_confirmation(self, ocr_result, detected_media_name):
        """
        Open the media confirmation dialog.
        Central entry point for any save that requires media selection.
        """
        all_media = self.media_service.get_all_media()

        dialog = MediaConfirmationDialog(detected_media_name, all_media, self.media_service, self)

        dialog.accepted.connect(
            lambda media_id: self.capture_service.start_save_flow(ocr_result, media_id)
        )

        if dialog.exec() == QDialog.DialogCode.Rejected:
            # If user cancelled but we have a previous media, use it
            if self.capture_service.last_confirmed_media_id is not None:
                last_id = self.capture_service.last_confirmed_media_id
                media = self.media_service.get_media_by_id(last_id)
                if media:
                    self.custom_tab.overlay_panel.update_displayed_media(media['title'], last_id)
                self.capture_service.start_save_flow(ocr_result, last_id)

    # ─── Display Mode ────────────────────────────────────────────────────────

    def apply_display_mode(self):
        """Apply the current display mode from settings."""
        mode = self.setting_service.get('display_mode', 'overlay')
        opacity = self.setting_service.get('window_opacity', 92)

        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        if mode == 'overlay':
            self._setup_overlay_mode(screen_width, screen_height, opacity)
        elif mode == 'windowed':
            self._setup_windowed_mode(screen_width, screen_height)
        elif mode == 'compact':
            self._setup_compact_mode(screen_width, screen_height, opacity)
        else:
            # Default to overlay
            self._setup_overlay_mode(screen_width, screen_height, opacity)

        self.setWindowTitle('ToriiKanji')
        self.setWindowIcon(QIcon(str(ICON)))
        self.setObjectName('main_panel')
        self._setup_background(screen_width, screen_height)

    def _setup_overlay_mode(self, screen_width, screen_height, opacity):
        """30% side panel, frameless, stays on top."""
        panel_width = max(int(screen_width * 0.3), 400)
        panel_height = screen_height
        panel_x = screen_width - panel_width
        panel_y = 0

        self.setGeometry(QRect(panel_x, panel_y, panel_width, panel_height))
        self.setFixedSize(QSize(panel_width, panel_height))
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setWindowOpacity(opacity / 100)

    def _setup_windowed_mode(self, screen_width, screen_height):
        """Normal resizable window with title bar."""
        win_width = max(int(screen_width * 0.35), 500)
        win_height = max(int(screen_height * 0.75), 600)
        win_x = (screen_width - win_width) // 2
        win_y = (screen_height - win_height) // 2

        self.setGeometry(QRect(win_x, win_y, win_width, win_height))
        self.setMinimumSize(QSize(400, 500))
        self.setMaximumSize(QSize(screen_width, screen_height))
        # Clear fixed size constraints
        self.setMinimumSize(QSize(400, 500))
        self.setWindowFlags(Qt.WindowType.Window)
        self.setWindowOpacity(1.0)

    def _setup_compact_mode(self, screen_width, screen_height, opacity):
        """Small floating popup for minimal footprint."""
        panel_width = max(int(screen_width * 0.22), 350)
        panel_height = max(int(screen_height * 0.6), 450)
        panel_x = screen_width - panel_width - 20
        panel_y = screen_height - panel_height - 60

        self.setGeometry(QRect(panel_x, panel_y, panel_width, panel_height))
        self.setFixedSize(QSize(panel_width, panel_height))
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setWindowOpacity(opacity / 100)

    def _setup_background(self, screen_width, screen_height):
        """Setup the background watermark image."""
        # Use percentage-based sizing
        label_size = min(int(min(screen_width, screen_height) * 0.25), 477)
        panel_width = self.width()
        panel_height = self.height()

        pos_x = (panel_width - label_size) // 2
        pos_y = (panel_height - label_size) // 2

        self.background_label = QLabel(self)
        self.background_label.setGeometry(QRect(pos_x, pos_y, label_size, label_size))

        pixmap = QPixmap(str(BACKGROUND_IMG)).scaled(
            label_size, label_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.background_label.setPixmap(pixmap)

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0.1)
        self.background_label.setGraphicsEffect(self.opacity_effect)
        self.background_label.lower()
        self.background_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
        )

    # ─── Window Helpers ──────────────────────────────────────────────────────

    def _show_and_raise(self):
        """Show the window and bring it to the front."""
        self.show()
        self.raise_()
        self.activateWindow()

    def toggle_visibility(self):
        """Toggle window visibility."""
        if self.isVisible():
            self.hide()
        else:
            self._show_and_raise()

    # ─── System Tray ─────────────────────────────────────────────────────────

    def config_tray(self):
        """Configure the system tray icon and context menu."""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(str(BACKGROUND_IMG)))
        self.tray_menu = QMenu()

        show_action = QAction(t('show'), self)
        show_action.triggered.connect(self.show)
        self.tray_menu.addAction(show_action)

        quit_action = QAction(t('exit'), self)
        quit_action.triggered.connect(QApplication.exit)
        self.tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()

    # ─── Event Handling ──────────────────────────────────────────────────────

    def event(self, event):
        """Handle custom hotkey events."""
        if isinstance(event, CustomHotkeyEvent):
            if event.action_type == "exit":
                QApplication.exit()
            elif event.action_type == "toggle":
                self.toggle_visibility()
            elif event.action_type == "capture":
                self.initialize_capture()
            return True
        return super().event(event)
