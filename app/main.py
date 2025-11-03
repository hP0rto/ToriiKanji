import sys
from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtGui import QPixmap, QColor
from gui.MainWindow import MainWindow
from PyQt6.QtCore import Qt, QTimer
from utils.paths import BACKGROUND_IMG

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Force dark palette to ensure consistent colors regardless of Windows theme
    from PyQt6.QtGui import QPalette, QColor
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
    dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(44, 44, 44))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(30, 30, 30))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(44, 44, 44))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
    app.setPalette(dark_palette)
    
    splash_pix = QPixmap(str(BACKGROUND_IMG)).scaled(
        400,300,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation)
    
    splash = QSplashScreen(splash_pix, Qt.WindowType.FramelessWindowHint)
    splash.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
    splash.setEnabled(False)
    splash.show()

    progress = {"value": 0}

    def update_progress():
        progress["value"] += 5
        splash.showMessage(
            'ToriiKanji',
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
            QColor('black')
        )
        splash.showMessage(
            f"ToriiKanji\n{progress['value']}%",
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