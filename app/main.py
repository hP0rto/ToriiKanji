import sys
from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtGui import QPixmap, QColor
from gui.MainWindow import MainWindow
from PyQt6.QtCore import Qt, QTimer
from utils.paths import BACKGROUND_IMG

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    splash_pix = QPixmap(str(BACKGROUND_IMG)) 
    splash = QSplashScreen(splash_pix, Qt.WindowType.FramelessWindowHint)
    splash.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
    splash.setEnabled(False)
    splash.show()

    progress = {"value": 0}

    def update_progress():
        progress["value"] += 5
        splash.showMessage(
            f"Loading... {progress['value']}%",
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
            QColor("white")
        )
        if progress["value"] >= 100:
            timer.stop()
            main = MainWindow()
            main.show()
            splash.finish(main)  

    timer = QTimer()
    timer.timeout.connect(update_progress)
    timer.start(50)
    
    sys.exit(app.exec())