from datetime import datetime
import os
from tkinter import Tk

from utils.helpers import get_app_name
from core.services.setting_services import SettingsService
from ocr.ScreenCapture import ScreenCapture

from db.repositories.capture_repository import CaptureRepository


class CaptureService():
    def __init__(self):
        self.capture_repo = CaptureRepository()
        
        self.settings_service = SettingsService()
        
        self.save_dir = "captures"
        os.makedirs("captures", exist_ok=True)

    def save_capture(self,raw_text, image_path, kanjis, media_id=None):
        capture_id = self.capture_repo.insert_capture(raw_text, image_path, media_id)

        for k in kanjis:
            self.capture_repo.insert_capture_kanji(capture_id, k['kanji'])
            
        return capture_id
            
        
    def save_image(self, image):
        image_path = None
        
        filename = f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        image_path = os.path.join(self.save_dir, filename)
        image.save(image_path)
        
        return image_path
    
    def get_captures(self):
        return self.capture_repo.select_captures()
    
    def remove_capture(self, capture):
        self.capture_repo.delete_capture(capture['id'])
        image_path = capture['image_path']
        
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
        
    def find_by_id_capture(self, id):
        return self.capture_repo.select_capture_by_id(id)
    
    def start_screenshot(self):
        root = Tk()
        app = ScreenCapture(root)
        root.mainloop()
        
        get_app_name()
        
        screencapture_result = {}
        
        screencapture_result['file_name'] = app.file_name
        screencapture_result['screenshot'] = app.screenshot
        
        return screencapture_result
    
    

