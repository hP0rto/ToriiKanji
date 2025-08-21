from PyQt6.QtWidgets import QWidget, QVBoxLayout, QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QIcon, QAction

from core.services.hotkey_services import CustomHotkeyEvent, config_hotkey
from gui.components.CustomTabWidget import CustomTabWidget
from utils.paths import BACKGROUND_IMG

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        config_hotkey(self)

        self.config_tray()        
        self.panel_settings()
        
        tab = CustomTabWidget(self)


        layout = QVBoxLayout()

        layout.addWidget(tab)
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
            # elif event.tipo == "toggle":
            #    self.toggle_visibility() 
            # elif event.tipo == "capture":
            #    self.capture_button()
            return True
        return super().event(event)
        
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
        self.setObjectName('main_panel')

        self.setStyleSheet(f"""
            MainWindow {{
                background-image: url('{BACKGROUND_IMG.as_posix()}');
                background-repeat: no-repeat;
                background-position: center;
                background-color: #1f1f1f;
                border-radius: 16px;
            }}
        """)
        
