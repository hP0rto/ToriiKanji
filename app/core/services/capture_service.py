from tkinter import Tk

from ocr.ScreenCapture import ScreenCapture
from ocr.ocr_processor import OcrProcessor

from utils.converters import pil_to_qpixmap

from PyQt6.QtWidgets import QMessageBox, QSystemTrayIcon
from PyQt6.QtGui import QPixmap

class CaptureService():
    def __init__(self):
        self.ocr_processor = OcrProcessor()
    
    def capture_image(self):
        result = {}
        
        screencapture_result = self.start_screenshot()
        
        pixmap = pil_to_qpixmap(screencapture_result.get('screenshot'))
        # pixmap = QPixmap(f'./images/{screencapture_result.get('file_name')}.png') 
        
        result['pixmap'] = pixmap
        result['text'] = self.ocr_processor.extract_text(pixmap)
        
        return result

    
    def start_screenshot(self):
        root = Tk()
        app = ScreenCapture(root)
        root.mainloop()
        
        screencapture_result = {}
        
        screencapture_result['file_name'] = app.file_name
        screencapture_result['screenshot'] = app.screenshot
        
        return screencapture_result
