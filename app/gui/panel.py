from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, QRect, QSize
from PyQt6.QtGui import QIcon, QPainter, QColor
import ctypes
import ctypes.wintypes
from gui.components.HotkeyLineEdit import HotkeyLineEdit
from gui.hotkey_services import CustomHotkeyEvent, config_hotkey, update_hotkey
from core.setting_services import SettingsService

class OverlayPanel(QWidget):

    def __init__(self):
        super().__init__()

        # panel settings
        panel_settings(self)
        set_exit_button(self)
        set_settings_button(self)
        config_hotkey(self)
        main_vertical_layout = QVBoxLayout()
        top_horizontal_layout= QHBoxLayout()

        main_vertical_layout.addLayout(top_horizontal_layout)
        

        top_horizontal_layout.addWidget(self.setting_button)
        top_horizontal_layout.addStretch()
        top_horizontal_layout.addWidget(self.exit_button)

        self.hotkey_input = HotkeyLineEdit()
        main_vertical_layout.addWidget(self.hotkey_input)

        self.botao = QPushButton("Save Hotkey Config", self)
        self.botao.clicked.connect(self.change_key)
        main_vertical_layout.addWidget(self.botao)
        
        self.setLayout(main_vertical_layout)

        main_vertical_layout.addStretch()
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

def set_exit_button(self):

    self.exit_button = QPushButton('',self)
    self.exit_button.setIcon(QIcon('../assets/exit_button.svg'))
    self.exit_button.setFixedSize(48,48)
    self.exit_button.setIconSize(QSize(48,48))
    self.exit_button.setStyleSheet("""
    QPushButton {
        background-color: transparent;
        border: none;
    }
    QPushButton:hover {
        background-color: rgba(255, 255, 255, 0.1);
    }
    """)
    self.exit_button.clicked.connect(lambda: QApplication.postEvent(self, CustomHotkeyEvent("exit")))

def set_settings_button(self):

    self.setting_button = QPushButton('',self)
    self.setting_button.setIcon(QIcon('../assets/setting_button.svg'))
    self.setting_button.setFixedSize(48,48)
    self.setting_button.setIconSize(QSize(48,48))
    self.setting_button.setStyleSheet("""
    QPushButton {
        background-color: transparent;
        border: none;
    }
    QPushButton:hover {
        background-color: rgba(255, 255, 255, 0.1);
    }
    """)
    self.setting_button.clicked.connect(lambda: QApplication.postEvent(self, CustomHotkeyEvent("exit")))

