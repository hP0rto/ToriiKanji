import sys
from PyQt6.QtWidgets import QApplication,QStackedWidget
from gui.MainWindow import MainWindow
from gui.OverlayPanel import OverlayPanel
from gui.SettingsPanel import SettingsPanel

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()

    sys.exit(app.exec())