from PyQt6.QtWidgets import QApplication, QWidget,  QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, QRect

from gui.components.buttons_factory import create_icon_button
from core.services.hotkey_services import CustomHotkeyEvent
from utils.paths import EXIT_ICON, SETTINGS_ICON

class OverlayPanel(QWidget):

    def __init__(self, main_window):
        super().__init__()
            
        self.main_window = main_window # dependency injection 👍    
        
        # create buttons
        self.exit_button = create_icon_button(EXIT_ICON,'Exit', on_click=lambda:QApplication.postEvent(self,CustomHotkeyEvent('exit')))
        self.settings_button = create_icon_button(SETTINGS_ICON,'Setting', on_click=self.main_window.show_settings_panel)
        
        # create layouts
        main_vertical_layout = QVBoxLayout()
        top_horizontal_layout= QHBoxLayout()

        # sets widget and layouts
        main_vertical_layout.addLayout(top_horizontal_layout)

        top_horizontal_layout.addWidget(self.settings_button)
        top_horizontal_layout.addStretch() # space between exit and setting button
        
        self.setLayout(main_vertical_layout)

        main_vertical_layout.addStretch() # free space beneath  save button        
        
        # show panel
        self.show()

   

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

