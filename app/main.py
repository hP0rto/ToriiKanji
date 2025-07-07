import sys
from PyQt6.QtWidgets import QApplication, QWidget
from gui.hotkey_services import CustomHotkeyEvent, config_hotkey
from gui.panel  import panel_settings
from core.setting_services import setting_services



class OverlayPanel(QWidget):

    def __init__(self):
        super().__init__()

        # panel settings
        panel_settings(self)
        config_hotkey(self)
        
        # show panel
        self.show()

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    panel = OverlayPanel()

    usersettings = setting_services()
    usersettings.create_hotkey_file()

    usersettings.edit_hotkey_file()

    sys.exit(app.exec())