from tkinter import Tk

from ocr.ScreenCapture import ScreenCapture
from ocr.ocr_processor import OcrProcessor

from utils.converters import pil_to_qpixmap

from PyQt6.QtWidgets import QMessageBox, QSystemTrayIcon
from PyQt6.QtGui import QPixmap

class CaptureService():
    def start_screenshot(self):
        root = Tk()
        app = ScreenCapture(root)
        root.mainloop()
        
        screencapture_result = {}
        
        screencapture_result['file_name'] = app.file_name
        screencapture_result['screenshot'] = app.screenshot
        
        return screencapture_result

