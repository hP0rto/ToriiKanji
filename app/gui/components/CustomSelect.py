from PyQt6.QtWidgets import QComboBox, QVBoxLayout, QWidget

from gui.theme import BG_HOVER, PRIMARY, TEXT_NORMAL


class CustomSelect(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()

        combo = QComboBox()
        combo.addItems(["Option 1", "Option 2", "Option 3"])

        combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {BG_HOVER};    /* background */
                color: {TEXT_NORMAL};            /* font color */
                border: 2px solid {PRIMARY};     /* primary border */
                border-radius: 12px;             /* rounded corners */
                padding: 6px 12px;               /* inner spacing */
                font-size: 14px;
            }}
            
            /* On mouse hover */
            QComboBox:hover {{
                border: 2px solid {TEXT_NORMAL};
            }}

            /* When the list is open */
            QComboBox QAbstractItemView {{
                background-color: {BG_HOVER};
                color: {TEXT_NORMAL};
                border: 1px solid {PRIMARY};
                selection-background-color: {PRIMARY};
                selection-color: {TEXT_NORMAL};
                border-radius: 8px;
            }}

            /* Dropdown arrow area */
            QComboBox::drop-down {{
                border: none;
                width: 30px;
                background-color: {PRIMARY};
                border-top-right-radius: 12px;
                border-bottom-right-radius: 12px;
            }}

            QComboBox::down-arrow {{
                image: url(assets/arrow_down.svg); /* can use a custom icon */
                width: 14px;
                height: 14px;
            }}
        """)

        layout.addWidget(combo)
        self.setLayout(layout)
