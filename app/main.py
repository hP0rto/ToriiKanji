import sys
from PyQt6.QtWidgets import QApplication
from gui.panel  import OverlayPanel

if __name__ == '__main__':
    app = QApplication(sys.argv)
    panel = OverlayPanel()

    sys.exit(app.exec())