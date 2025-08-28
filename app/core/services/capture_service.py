from tkinter import Tk
from ocr.ScreenCapture import ScreenCapture
from PyQt6.QtWidgets import QMessageBox, QSystemTrayIcon
from PyQt6.QtGui import QPixmap

class CaptureService():
    
    def capture_image(self):
        result = {}
        
        file_name = self.start_screenshot()
        result['pixmap'] = QPixmap(f'./images/{file_name}.png') 
            
        return result

    
    def start_screenshot(self):
        root = Tk()
        app = ScreenCapture(root)
        root.mainloop()
        return app.file_name 
