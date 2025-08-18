
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QLabel
from PyQt6.QtCore import Qt
from gui.SettingsPanel import SettingsPanel
from gui.OverlayPanel import OverlayPanel
class CustomTabWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout(self)

        # Barra de navegação (abas)
        self.tab_bar = QHBoxLayout()
        self.tab_bar.setContentsMargins(0,0,0,0)
        self.tab_bar.setSpacing(0)
        
        
        layout.addLayout(self.tab_bar)

        # Conteúdo
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        # Criando abas e páginas
        self.add_tab("Insights", OverlayPanel(self.main_window)) 
        self.add_tab("Collections", QLabel("Conteúdo da aba Collections"))
        self.add_tab("Settings", SettingsPanel(self.main_window))

        self.show_tab(0)  # inicia na primeira aba

    def add_tab(self, title, widget):
        index = self.stack.addWidget(widget)

        button = QPushButton(title)
        button.setStyleSheet('''
                             
                    QPushButton {
                        border: none;
                        background-color: transparent;
                        color: #FFFFFF;
                        padding: 10px;
                        font-size: 14px;
                    }
                    
                    QPushButton:checked {
                        background-color: #C24338;
                        border-radius: 10px;
                        font-weight: bold;
                    }
        ''')
        
        button.setCheckable(True)
        button.clicked.connect(lambda: self.show_tab(index))

        self.tab_bar.addWidget(button)

    def show_tab(self, index):
        self.stack.setCurrentIndex(index)
        # Reset estado dos botões
        for i in range(self.tab_bar.count()):
            btn = self.tab_bar.itemAt(i).widget()
            btn.setChecked(i == index)