from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox

class CustomSelect(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()

        combo = QComboBox()
        combo.addItems(["Opção 1", "Opção 2", "Opção 3"])

        combo.setStyleSheet("""
            QComboBox {
                background-color: #3C3C3C;       /* cor de fundo */
                color: #FFFFFF;                  /* cor da fonte */
                border: 2px solid #C24338;       /* borda primária */
                border-radius: 12px;             /* cantos arredondados */
                padding: 6px 12px;               /* espaçamento interno */
                font-size: 14px;
            }
            
            /* Quando passa o mouse */
            QComboBox:hover {
                border: 2px solid #FFFFFF;
            }

            /* Quando abre a lista */
            QComboBox QAbstractItemView {
                background-color: #3C3C3C;
                color: #FFFFFF;
                border: 1px solid #C24338;
                selection-background-color: #C24338;
                selection-color: #FFFFFF;
                border-radius: 8px;
            }

            /* Setinha do lado */
            QComboBox::drop-down {
                border: none;
                width: 30px;
                background-color: #C24338;
                border-top-right-radius: 12px;
                border-bottom-right-radius: 12px;
            }

            QComboBox::down-arrow {
                image: url(assets/arrow_down.svg); /* pode usar um ícone seu */
                width: 14px;
                height: 14px;
            }
        """)

        layout.addWidget(combo)
        self.setLayout(layout)