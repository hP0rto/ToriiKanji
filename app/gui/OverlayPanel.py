from PyQt6.QtWidgets import * 
from PyQt6.QtGui import *
from PyQt6.QtCore import *

from gui.components.CustomSelect import CustomSelect

class OverlayPanel(QWidget):

    def __init__(self, main_window):
        super().__init__()
            
        self.main_window = main_window # dependency injection 👍    
        
        select = QComboBox()
        select.addItems(["Opção 1", "Opção 2", "Opção 3"])
        
        # create layouts
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    

        
        # sets widget and layouts
        layout.addWidget(select)
        
        self.setLayout(layout)
        
        
        self.capture_label = QLabel("Nenhuma captura ainda")
        self.capture_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.capture_label)
        
        # show panel
        self.show()
        
    def show_capture(self, pixmap: QPixmap):
        """Exibe a captura no painel"""
        self.capture_label.setPixmap(pixmap.scaled(
            400, 400,  # tamanho máximo de preview
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))