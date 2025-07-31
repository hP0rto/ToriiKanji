from PyQt6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QApplication
from PyQt6.QtCore import Qt, QRect

from core.services.hotkey_services import CustomHotkeyEvent, config_hotkey
from gui.OverlayPanel import OverlayPanel
from gui.SettingsPanel import SettingsPanel

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # Conigura hotkeys ao iniciar
        config_hotkey(self)
        
        self.panel_settings()

        self.overlay_panel = OverlayPanel(main_window=self)
        self.settings_panel = SettingsPanel(main_window=self)

        # Stack para alternar entre as telas
        self.stack = QStackedWidget()
        self.stack.addWidget(self.overlay_panel)   # index 0
        self.stack.addWidget(self.settings_panel)  # index 1

        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

        self.show()
        
    def event(self, event):
        print(f'Main: {event}')
        
        if isinstance(event, CustomHotkeyEvent):       
            if event.tipo == "exit":
                QApplication.exit()
            # elif event.tipo == "toggle":
            #    self.toggle_visibility() 
            # elif event.tipo == "capture":
            #    self.capture_button()
            return True
        return super().event(event)

    def show_overlay_panel(self):
        self.stack.setCurrentIndex(0)

    def show_settings_panel(self):
        self.stack.setCurrentIndex(1)
        
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
        
        self.setWindowOpacity(0.92)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #1f1f1f;
                border-radius: 16px;
            }
        """)
    