# core/handlers/capture_handler.py
from datetime import datetime
import os
from core.services.setting_services import SettingsService

class CaptureHandler:
    def __init__(self, capture_repo):
        self.capture_repo = capture_repo
        
        self.settings_service = SettingsService()
        
        self.save_dir = "captures"
        os.makedirs("captures", exist_ok=True)

    def save_capture(self, image, kanjis, media_id=None):
        image_path = None
        
        save_image = self.settings_service.user_settings.get('save_image')
        auto_save = self.settings_service.user_settings.get('auto_save')
        
        if save_image:
            filename = f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            image_path = os.path.join(self.save_dir, filename)
            image.save(image_path)
            
        if auto_save:
            capture_id = self.capture_repo.insert_capture(image_path, media_id)

            for k in kanjis:
                self.capture_repo.insert_capture_kanji(capture_id, k['kanji'])
                
            return capture_id
           
