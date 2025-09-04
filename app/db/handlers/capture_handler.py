# core/handlers/capture_handler.py
from datetime import datetime
import os

class CaptureHandler:
    def __init__(self, capture_repo, auto_save: bool = False, save_dir="captures"):
        self.capture_repo = capture_repo
        self.auto_save = auto_save
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)

    def save_capture(self, image, kanjis: list[str], media_id=None):
        image_path = None
        if self.auto_save:
            filename = f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            image_path = os.path.join(self.save_dir, filename)
            image.save(image_path)

        capture_id = self.capture_repo.insert_capture(image_path, media_id)

        for k in kanjis:
            self.capture_repo.insert_capture_kanji(capture_id, k)

        return capture_id
