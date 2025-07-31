from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from core.services.hotkey_services import update_hotkey
from gui.components.HotkeyLineEdit import HotkeyLineEdit
from gui.components.buttons_factory import create_text_button
from core.services.setting_services import SettingsService

class SettingsPanel(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window # dependency injection 👍    
        
        self.setWindowTitle("Configurações")
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)  # Travar tela anterior

        self.setStyleSheet("""
            QWidget {
                background-color: #1f1f1f;
                color: white;
                padding: 16px;
                border-radius: 12px;
            }
            QLabel {
                font-size: 14px;
            }
        """)
        
        self.setting_service = SettingsService()

        layout = QVBoxLayout()
        
        self.save_button = create_text_button('Save Hotkey Config', on_click=self.change_key)
        self.hotkey_input = HotkeyLineEdit()

        # Exemplo: Exibir a tecla de atalho atual salva
        self.label_hotkey = QLabel(f"Tecla de atalho atual: {self.setting_service.user_settings.get('exit_key')}")
        layout.addWidget(self.label_hotkey)

        layout.addWidget(self.hotkey_input)
        layout.addWidget(self.save_button)
        
        # Botão para fechar o painel
        close_button = create_text_button("Fechar", self.main_window.show_overlay_panel)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignRight)

        self.setLayout(layout)
        
    def change_key(self):
        if self.hotkey_input.text():
            self.setting_service.edit_settings_file('exit_key', self.hotkey_input.text())
            self.label_hotkey.setText(f'Tecla de atalho atual: {self.setting_service.user_settings.get('exit_key')}')
            update_hotkey(self.main_window)    
            
       