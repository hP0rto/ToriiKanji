from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt, QRect, QSize
from PyQt6.QtGui import QIcon

from gui.components.HotkeyLineEdit import HotkeyLineEdit
from gui.hotkey_services import CustomHotkeyEvent, config_hotkey, update_hotkey
from core.setting_services import SettingsService

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
    
    layout = QVBoxLayout()


    self.hotkey_input = HotkeyLineEdit()
    layout.addWidget(self.hotkey_input)

    self.setLayout(layout)

def button_settings(self):

    exit_button = QPushButton('',self)
    exit_button.setIcon(QIcon('../assets/exit_button.svg'))
    exit_button.move(0, 0)
    exit_button.setFixedSize(48,48)
    exit_button.setIconSize(QSize(48,48))
    exit_button.setStyleSheet("""
    QPushButton {
        background-color: transparent;
        border: none;
    }
    QPushButton:hover {
        background-color: rgba(255, 255, 255, 0.1);
    }
    """)
    exit_button.clicked.connect(lambda: QApplication.postEvent(self, CustomHotkeyEvent("exit")))

class OverlayPanel(QWidget):

    def __init__(self):
        super().__init__()

        # panel settings
        panel_settings(self)
        button_settings(self)
        config_hotkey(self)



        # show panel
        self.show()

    def reload_hotkeys(self):
        '''Reload the hotkey, and updates the values in usersettings.json'''
        usersettings = SettingsService()

        usersettings.edit_settings_file('exit_key', 'f5')
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
    