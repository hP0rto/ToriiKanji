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
        # show panel
        self.show()