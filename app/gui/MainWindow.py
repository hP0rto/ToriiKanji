from tkinter import Tk
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QApplication, QSystemTrayIcon, QMenu, QLabel, QGraphicsOpacityEffect, QMessageBox
from PyQt6.QtCore import Qt, QRect, QThread
from PyQt6.QtGui import QIcon, QAction, QPixmap

from db.repositories.kanji_repository import KanjiRepository
from db.repositories.capture_repository import CaptureRepository
from db.handlers.capture_handler import CaptureHandler

from core.services.setting_services import SettingsService
from core.workers.ocr_worker import OcrWorker
from core.services.capture_service import CaptureService
from core.services.ocr_service import OcrService
from core.services.hotkey_services import CustomHotkeyEvent, config_hotkey

from gui.components.CustomTabWidget import CustomTabWidget

from utils.paths import BACKGROUND_IMG, ICON

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        config_hotkey(self)
        self.config_tray()        
        self.panel_settings()
        
        self.ocr_service = OcrService()
        self.capture_service = CaptureService()
        self.setting_service = SettingsService()
        
        
        self.kanji_repo = KanjiRepository()
        self.capture_repository = CaptureRepository()
        self.capture_handler = CaptureHandler(self.capture_repository)
        
        self.custom_tab = CustomTabWidget(self)
        layout = QVBoxLayout()
        
        layout.addWidget(self.custom_tab)
        self.setLayout(layout)
        self.show()
   
   
    def config_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(str(BACKGROUND_IMG)))
        self.tray_menu = QMenu()
        
        show_action = QAction("Mostrar", self)
        show_action.triggered.connect(self.show)
        self.tray_menu.addAction(show_action)
    
        
        quit_action = QAction("Sair", self)
        quit_action.triggered.connect(QApplication.exit)
        self.tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(self.tray_menu)

        self.tray_icon.show()
   
    def event(self, event):
           
        if isinstance(event, CustomHotkeyEvent):       
            if event.tipo == "exit":
                QApplication.exit()
            elif event.tipo == "toggle":
                self.toggle_visibility() 
            elif event.tipo == "capture":
                self.initialize_capture()
                    
            return True
        return super().event(event)
    
    
    def process_capture(self, image):
        self.thread = QThread()
        self.worker = OcrWorker(self.ocr_service, image)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_ocr_finished)
        self.worker.error.connect(self.on_ocr_error)

        # limpa quando terminar
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()
            
    def on_ocr_finished(self, result):
        self.toggle_visibility()
        print("OCR result:", result)
        #image = result["screenshot"]
        
        
        kanjis = result["kanjis"]
        result['kanjis'] = self.kanji_repo.find_many(kanjis)

        self.custom_tab.show_capture(result)
        
        #if self.capture_handler.auto_save:
        self.save_capture_async(result)
        

    def on_ocr_error(self, msg):
        self.toggle_visibility()
        print("Erro OCR:", msg) 
        QMessageBox.critical(self, "Error", f"Error on capture: \n{msg}")
    
    def initialize_capture(self):
        if self.isVisible():
            self.toggle_visibility()
        
        result = self.capture_service.start_screenshot()
        
        self.process_capture(result.get('screenshot'))
        
        self.tray_icon.showMessage("Capture", "Capture initialized!",QSystemTrayIcon.MessageIcon.NoIcon)
    

    def save_capture_async(self, result):
        """Roda insert no banco em thread separada"""
        from core.workers.db_worker import DbWorker
        self.db_thread = QThread()
        self.db_worker = DbWorker(
            self.capture_handler, 
            "save_capture", 
            result["pixmap"], 
            result["kanjis"]
        )
        self.db_worker.moveToThread(self.db_thread)

        self.db_thread.started.connect(self.db_worker.run)
        self.db_worker.finished.connect(lambda id: self.tray_icon.showMessage("Capture", f"Capture {id} saved successfully!",QSystemTrayIcon.MessageIcon.NoIcon))
        self.db_worker.error.connect(lambda e: QMessageBox.critical(self, "Error", f"Error on saving capture: \n{e}"))

        self.db_worker.finished.connect(self.db_thread.quit)
        self.db_worker.finished.connect(self.db_worker.deleteLater)
        self.db_thread.finished.connect(self.db_thread.deleteLater)

        self.db_thread.start()
    
    
    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()  # Garante que apareça em frente às outras janelas
            self.activateWindow()
    
    def panel_settings(self):
        '''Define Panel visibility settings '''
        # Finding screen resolution
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
    
        # Finding 30% of width
        panel_width = int(screen_width * 0.3)
        panel_height = screen_height
        # Finding pos
        panel_x = screen_width - panel_width
        panel_y = 0

        # Setting panel pos and dimensions
        self.setGeometry(QRect(panel_x, panel_y, panel_width, panel_height))

        # Customizing panel
        self.setWindowTitle('ToriiKanji')
        self.setWindowFlag (Qt.WindowType.FramelessWindowHint |  # Sem bordas
                            Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowIcon(QIcon(str(ICON)))
        self.setWindowOpacity(0.92)
        self.setObjectName('main_panel')
        
        label_width = 477
        label_height = 477

        # Posição centralizada no painel
        pos_x = (panel_width - label_width) // 2
        pos_y = (panel_height - label_height) // 2
    
        self.background_label = QLabel(self)
        self.background_label.setGeometry(QRect(pos_x,pos_y,label_width,label_height))
        
        pixmap = QPixmap(str(BACKGROUND_IMG)).scaled(
        label_width,label_height,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation)
        

        
        self.background_label.setPixmap(pixmap)
        # Create an opacity effect
        self.opacity_effect = QGraphicsOpacityEffect(self)

        # Set the desired opacity (e.g., 0.5 for 50% transparency)
        self.opacity_effect.setOpacity(0.1) 

        # Apply the effect to the QLabel
        self.background_label.setGraphicsEffect(self.opacity_effect)
        
        self.background_label.lower()
        self.background_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
    
