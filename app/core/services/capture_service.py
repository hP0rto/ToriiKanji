"""
Capture service for ToriiKanji.
Handles the full capture flow: screenshot → OCR → save.
Communicates with the UI exclusively through Qt signals (no direct window references).
"""

import os
from datetime import datetime

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from core.services.setting_services import SettingsService
from core.workers.db_worker import DbWorker
from core.workers.ocr_worker import OcrWorker
from db.repositories.capture_repository import CaptureRepository
from ocr.ScreenCapture import ScreenCapture
from utils.helpers import run_in_thread
from utils.paths import base_dir


class CaptureService(QObject):
    """
    Manages the capture lifecycle: screenshot → OCR → database storage.
    
    Signals:
        ocr_finished(dict): Emitted when OCR processing completes
        capture_saved(int): Emitted when a capture is saved (with capture ID)
        image_saved(str): Emitted when an image is saved to disk (with path)
        error_occurred(str): Emitted when an error occurs
        media_confirmation_required(dict, str): Emitted when media needs user confirmation
        hide_window(): Emitted when the main window should hide
        show_window(): Emitted when the main window should show
    """

    # Signals for UI communication (replaces direct main_window access)
    ocr_finished = pyqtSignal(dict)
    capture_saved = pyqtSignal(int)
    image_saved = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    media_confirmation_required = pyqtSignal(dict, str)
    hide_window = pyqtSignal()
    show_window = pyqtSignal()

    def __init__(self, kanji_service, ocr_service):
        super().__init__()
        self.kanji_service = kanji_service
        self.ocr_service = ocr_service
        self.capture_repo = CaptureRepository()
        self.settings_service = SettingsService()

        self.last_confirmed_media_id = None

        # Determine save directory from settings or default
        self._update_save_dir()

        self.threads = []
        self.workers = []

    def _update_save_dir(self):
        """Update the capture save directory from settings."""
        custom_dir = self.settings_service.get('capture_save_dir', '')
        if custom_dir and os.path.isdir(custom_dir):
            self.save_dir = custom_dir
        else:
            self.save_dir = os.path.join(base_dir, "captures")
        os.makedirs(self.save_dir, exist_ok=True)

    def set_window_visible(self, is_visible):
        """Request the main window to show or hide via signals."""
        if is_visible:
            self.show_window.emit()
        else:
            self.hide_window.emit()

    # ─── Capture Flow ────────────────────────────────────────────────────────

    def start_full_capture_flow(self, window_visible=True):
        """
        Start the full capture flow: screenshot → OCR → (auto-save if enabled).
        
        Args:
            window_visible: Whether the main window is currently visible
        """
        if window_visible:
            self.hide_window.emit()

        screenshot_result = self._start_screenshot()
        if screenshot_result and screenshot_result.get('screenshot'):
            self._run_ocr_in_thread(
                screenshot_result.get('screenshot'),
                screenshot_result.get('captured_app_name')
            )
        else:
            # Screenshot was cancelled, restore window
            if window_visible:
                self.show_window.emit()

    def _start_screenshot(self):
        """Open the PyQt6 screen capture overlay and wait for user selection."""
        return ScreenCapture.select_region()

    def _run_ocr_in_thread(self, image, captured_app_name):
        """Run OCR processing in a background thread."""
        worker = OcrWorker(self.ocr_service, image)

        on_finished_callback = lambda ocr_result: self._handle_ocr_result(
            ocr_result, captured_app_name
        )

        thread = run_in_thread(
            worker=worker,
            on_finished=on_finished_callback,
            on_error=self._handle_error
        )

        # Keep references to prevent garbage collection
        self.threads.append(thread)
        self.workers.append(worker)

    def _handle_ocr_result(self, result, captured_app_name):
        """
        Called when OCR finishes. Emits result and handles auto-save logic.
        Delegates media confirmation to the UI layer via signals.
        """
        kanjis = result["kanjis"]
        result['kanjis'] = self.kanji_service.get_all_kanjis(kanjis)
        result['media_name'] = captured_app_name or 'Unknown'

        self.ocr_finished.emit(result)

        if self.settings_service.get('auto_save', False):
            show_media_dialog = self.settings_service.get('show_media_dialog', True)

            if show_media_dialog:
                # Ask UI to confirm media before saving
                self.media_confirmation_required.emit(result, result['media_name'])
            else:
                # Save directly without media confirmation
                print("Auto-save: Media dialog disabled. Saving directly.")
                self.media_confirmation_required.emit(result, result['media_name'])
        else:
            # Auto-save disabled: wait for manual save from user
            print("Auto-save disabled. Waiting for manual save action.")

    def _handle_error(self, msg):
        """Propagate errors to the UI via signal."""
        self.error_occurred.emit(msg)

    # ─── Save Flow ───────────────────────────────────────────────────────────

    @pyqtSlot(dict, int)
    def start_save_flow(self, result_data, media_id, is_manual=False):
        """
        Start saving a capture to disk and database.
        
        Args:
            result_data: OCR result dictionary
            media_id: ID of the associated media
            is_manual: Whether this is a manual save (user clicked Save)
        """
        print(f"Service: Starting save flow with media_id: {media_id}")

        # Guard against duplicate saves
        if result_data is None:
            return
        if result_data.get('_saving_in_progress'):
            print("Service: Save already in progress. Ignoring.")
            return
        if result_data.get('_saved'):
            print("Service: Already saved. Ignoring.")
            return

        result_data['media_id'] = media_id
        result_data['_saving_in_progress'] = True
        self.last_confirmed_media_id = media_id

        # Refresh save directory in case it changed
        self._update_save_dir()

        auto_save = self.settings_service.get('auto_save', False)
        save_image = self.settings_service.get('save_image', False)

        # Pre-save image if save_image enabled but not auto-saving yet
        if not auto_save and save_image and not is_manual:
            print("Service: Pre-saving image to disk.")
            image_path = self.save_image_to_disk(result_data['pixmap'])
            result_data['image_path'] = image_path
            return

        if is_manual:
            print("Service: Starting manual save flow.")
            if 'image_path' in result_data and result_data['image_path']:
                print("Image already saved, saving metadata only.")
                self._run_save_capture_data_in_thread(result_data, result_data['image_path'])
            else:
                self._run_full_save_in_thread(result_data)
        else:
            if auto_save:
                print("Service: Starting auto-save flow.")
                self._run_full_save_in_thread(result_data)

    def _run_full_save_in_thread(self, result):
        """Step 1: Save image to disk, then chain to metadata save."""
        worker = DbWorker(self, 'save_image_to_disk', result['pixmap'])

        thread = run_in_thread(
            worker=worker,
            on_finished=lambda image_path: self._run_save_capture_data_in_thread(result, image_path),
            on_error=self._handle_error
        )

        self.threads.append(thread)
        self.workers.append(worker)

    def _run_save_capture_data_in_thread(self, result, image_path):
        """Step 2: Save capture metadata to the database."""
        capture_worker = DbWorker(
            self,
            "save_capture_to_db",
            result['raw_text'],
            image_path,
            result["kanjis"],
            result['media_id']
        )

        def on_finished(capture_id):
            # Mark as saved to prevent duplicate saves
            try:
                result['_saved'] = True
                result.pop('_saving_in_progress', None)
            except Exception:
                pass

            # Notify UI
            try:
                self.capture_saved.emit(capture_id)
            except Exception:
                pass

        thread = run_in_thread(
            worker=capture_worker,
            on_finished=on_finished,
            on_error=self._handle_error
        )

        self.threads.append(thread)
        self.workers.append(capture_worker)

    # ─── Database Operations ─────────────────────────────────────────────────

    def save_capture_to_db(self, raw_text, image_path, kanjis, media_id=None):
        """Save capture record and associated kanji to the database."""
        capture_id = self.capture_repo.insert_capture(raw_text, image_path, media_id)

        for k in kanjis:
            self.capture_repo.insert_capture_kanji(capture_id, k['kanji'])

        return capture_id

    def save_image_to_disk(self, image):
        """Save a QPixmap image to disk and return the file path."""
        filename = f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        image_path = os.path.join(self.save_dir, filename)
        image.save(image_path)
        return image_path

    # ─── Query Operations ────────────────────────────────────────────────────

    def get_captures(self):
        """Get all captures ordered by most recent."""
        return self.capture_repo.select_captures_ordered('DESC')

    def get_captures_ordered(self, order='DESC'):
        """Get all captures with specified order."""
        return self.capture_repo.select_captures_ordered(order)

    def get_captures_by_kanji(self, kanji, order='DESC'):
        """Get captures containing a specific kanji."""
        return self.capture_repo.get_captures_by_kanji(kanji, order)

    def get_captures_by_media(self, media_id, order='DESC'):
        """Get captures filtered by media source."""
        return self.capture_repo.select_captures_by_media(media_id, order)

    def remove_capture(self, capture):
        """Delete a capture and its associated image file."""
        self.capture_repo.delete_capture(capture['id'])
        image_path = capture['image_path']

        if image_path and os.path.exists(image_path):
            os.remove(image_path)

    def find_by_id_capture(self, capture_id):
        """Find a capture by its ID."""
        return self.capture_repo.select_capture_by_id(capture_id)

    def update_capture_media(self, capture_id, media_id):
        """Update the media association for a capture."""
        self.capture_repo.update_media_id(capture_id, media_id)
        print(f"Capture {capture_id} media updated to {media_id}")

    def remove_captures_by_kanji(self, kanji):
        """Remove all captures that contain a specific kanji."""
        captures = self.get_captures_by_kanji(kanji)
        for capture in captures:
            self.remove_capture(capture)
