import sys
from PyQt6.QtWidgets import QApplication, QWidget
from panel  import panel_settings
from pynput import keyboard
from PIL import ImageGrab

class OverlayPanel(QWidget):

    def __init__(self):
        super().__init__()

        panel_settings(self)
        # show panel
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    panel = OverlayPanel()
    sys.exit(app.exec())