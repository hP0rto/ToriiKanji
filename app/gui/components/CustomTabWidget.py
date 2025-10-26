
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QLabel


from gui.components.AnalyticsPanel import AnalyticsPanel
from gui.CollectionPanel import CollectionPanel
from gui.SettingsPanel import SettingsPanel
from gui.OverlayPanel import OverlayPanel
class CustomTabWidget(QWidget):
    def __init__(self, main_window, capture_service, media_service, kanji_service, analitycs_service):
        super().__init__()
        self.main_window = main_window
        self.capture_service = capture_service
        self.media_service = media_service
        self.kanji_service = kanji_service
        self.analitycs_service = analitycs_service
        
        layout = QVBoxLayout(self)

        self.overlay_panel = OverlayPanel(self.main_window)
        self.settings_panel = SettingsPanel(self.main_window)
        self.collection_panel = CollectionPanel(self.main_window, self.capture_service, self.media_service, self.kanji_service)
        self.analytics_panel = AnalyticsPanel(self.analitycs_service, self.kanji_service, parent=self.main_window)
        self.settings_panel.settings_saved.connect(self.overlay_panel.update_ui_from_settings)
        
        self.tab_bar = QHBoxLayout()
        self.tab_bar.setContentsMargins(0,0,0,0)
        self.tab_bar.setSpacing(0)
                
        layout.addLayout(self.tab_bar)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        self.add_tab("Capture", self.overlay_panel) 
        self.add_tab("Collections", self.collection_panel)
        self.add_tab("Analytics", self.analytics_panel)
        self.add_tab("Settings", self.settings_panel)

        self.show_tab(0)

    def show_capture(self, result):
        self.overlay_panel.show_capture(result)

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
                        border-radius: 10px;
                    }
                    
                    QPushButton:checked {
                        background-color: #C24338;
                        
                        font-weight: bold;
                    }
                    
                    QPushButton:checked:hover {
                        
                    }
                    
                    QPushButton:hover {
                        background-color: #303030
                    }
                    
        ''')
        
        button.setCheckable(True)
        button.clicked.connect(lambda: self.show_tab(index))

        self.tab_bar.addWidget(button)

    def show_tab(self, index):
        self.stack.setCurrentIndex(index)
        
        if index == 2:
            self.analytics_panel.refresh_analytics()
            
        # Reset estado dos botões
        for i in range(self.tab_bar.count()):
            btn = self.tab_bar.itemAt(i).widget()
            btn.setChecked(i == index)