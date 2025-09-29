from tkinter import Tk
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QApplication, QSystemTrayIcon, QMenu, QLabel, QGraphicsOpacityEffect, QMessageBox
from PyQt6.QtCore import Qt, QRect, QThread, QSize
from PyQt6.QtGui import QIcon, QAction, QPixmap

from utils.helpers import run_in_thread
from utils.paths import BACKGROUND_IMG, ICON

from core.workers.db_worker import DbWorker
from core.workers.ocr_worker import OcrWorker
from core.services.kanji_service import KanjiService
from core.services.setting_services import SettingsService
from core.services.capture_service import CaptureService
from core.services.ocr_service import OcrService
from core.services.hotkey_services import CustomHotkeyEvent, config_hotkey

from gui.components.CustomTabWidget import CustomTabWidget



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.threads = []
        self.workers = []
        
        config_hotkey(self)
        self.config_tray()        
        self.panel_settings()
        
        
        
        
        self.ocr_service = OcrService()
        self.capture_service = CaptureService()
        self.setting_service = SettingsService()
        self.kanji_service = KanjiService()
        
        self.custom_tab = CustomTabWidget(self)
        
        overlay = self.custom_tab.overlay_panel  
        overlay.save_requested.connect(self.on_save_requested)
        
        
        layout = QVBoxLayout()
        
        layout.addWidget(self.custom_tab)
        self.setLayout(layout)
        self.show()
   
    
    def initialize_capture(self):
        if self.isVisible():
            self.toggle_visibility()
        
        result = self.capture_service.start_screenshot()
        
        self.process_ocr_thread(result)
        
        self.tray_icon.showMessage("Capture", "Capture initialized!",QSystemTrayIcon.MessageIcon.NoIcon)
    
    
    def on_save_requested(self, result):
        self.save_image_thread(result=result, auto_save=True)
    
    # ----------- Ocr Processor -----------
    def process_ocr_thread(self, result):
        ocr_worker = OcrWorker(self.ocr_service, result.get('screenshot'))
        run_in_thread(self, ocr_worker, on_finished=self.on_ocr_finished, on_error=self.on_ocr_error)
         
    def on_ocr_finished(self, result):
        self.toggle_visibility()
        print("OCR result:", result)

        kanjis = result["kanjis"]
        result['kanjis'] = self.kanji_service.get_all_kanjis(kanjis)
        
        auto_save = self.setting_service.user_settings.get('auto_save', False)
        save_image = self.setting_service.user_settings.get('save_image', False)
        
        if auto_save:
            self.save_image_thread(result, auto_save=True)
        elif save_image:
            self.save_image_thread(result, auto_save=False)
            


        self.custom_tab.show_capture(result)
        
    
    
    def on_ocr_error(self, msg):
        self.toggle_visibility()
        print("Erro OCR:", msg) 
        QMessageBox.critical(self, "Error", f"Error on capture: \n{msg}")
    
    # ----------- Saving Processors -----------
    def save_image_thread(self, result, auto_save=False):
        worker = DbWorker(
            self.capture_service, 
            "save_image",
            result["pixmap"]
        )
        self._thread = QThread()
        
        
        def on_finished(image_path):
            if auto_save:
                self.save_capture_thread(result, image_path)
            else:
                self.tray_icon.showMessage(
                    "Capture",
                    f"Image saved at '{image_path}'!",
                    QSystemTrayIcon.MessageIcon.NoIcon
                )
            
        def on_error(msg):
            QMessageBox.critical(self, "Error", f"Error on capture: \n{msg}")
        
        run_in_thread(self, worker, on_finished=on_finished, on_error=on_error)

    def save_capture_thread(self, result, image_path):
        worker = DbWorker(
            self.capture_service,
            "save_capture",
            result['raw_text'],
            image_path,
            result["kanjis"]
        )
        
        def on_finished(id):
            self.tray_icon.showMessage(
                "Capture", f"Capture {id} saved successfully!"
            )
            self.custom_tab.collection_panel.add_capture_to_grid(id)
        
        
        run_in_thread(self, worker, on_finished=on_finished)
    

    # ----------- Genearal Functions -----------
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

        self.setFixedSize(QSize(panel_width,panel_height))
        
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