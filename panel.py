from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QRect

def panel_settings(self):
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