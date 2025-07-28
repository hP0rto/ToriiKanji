from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, QRect, QSize
from PyQt6.QtGui import QIcon

from gui.components.HotkeyLineEdit import HotkeyLineEdit
from gui.components.buttons_factory import create_icon_button, create_text_button
from gui.hotkey_services import CustomHotkeyEvent, config_hotkey, update_hotkey

from core.setting_services import SettingsService

class OverlayPanel(QWidget):

    def __init__(self):
        super().__init__()

        panel_settings(self)
        config_hotkey(self)
        
        # create buttons
        self.exit_button = create_icon_button('../assets/exit_button.svg','Exit', on_click=lambda:QApplication.postEvent(self,CustomHotkeyEvent('exit')))
        self.settings_button = create_icon_button('../assets/setting_button.svg','Setting', on_click=lambda:QApplication.postEvent(self,CustomHotkeyEvent('exit')))
        self.save_button = create_text_button('Save Hotkey Config', on_click=self.change_key)
        self.hotkey_input = HotkeyLineEdit()
        
        # create layouts
        main_vertical_layout = QVBoxLayout()
        top_horizontal_layout= QHBoxLayout()

        # sets widget and layouts
        main_vertical_layout.addLayout(top_horizontal_layout)

        top_horizontal_layout.addWidget(self.settings_button)
        top_horizontal_layout.addStretch() # space between exit and setting button
        top_horizontal_layout.addWidget(self.exit_button)

        main_vertical_layout.addWidget(self.hotkey_input)
        main_vertical_layout.addWidget(self.save_button)
        
        self.setLayout(main_vertical_layout)

        main_vertical_layout.addStretch() # free space beneath  save button
        
        
        
        # show panel
        self.show()

    def change_key(self):
        usersettings = SettingsService()
        if self.hotkey_input.text():
            usersettings.edit_settings_file('exit_key', self.hotkey_input.text())
        update_hotkey(self)

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
    
    self.setStyleSheet("""
        QWidget {
            background-color: #1f1f1f;
            border-radius: 16px;
        }
    """)

