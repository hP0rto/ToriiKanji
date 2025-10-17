from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
                               QLineEdit, QPushButton, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import pyqtSignal
from utils.i18n import t


class MediaConfirmationDialog(QDialog):
    # Sinal que emitirá o ID da mídia confirmada quando o usuário aceitar
    accepted = pyqtSignal(int)

    def __init__(self, detected_media_name, all_media, media_service, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t('confirm_removal_title'))
        self.setModal(True) # Impede interação com a janela principal

        self.media_service = media_service
        self.detected_media_name = detected_media_name
        self.all_media = all_media

        # --- Layout e Widgets ---
        layout = QVBoxLayout(self)
        
        # Seção de Detecção Automática
        detected_layout = QHBoxLayout()
        detected_layout.addWidget(QLabel(f"Detected media: <b>{detected_media_name}</b>"))
        self.confirm_detected_button = QPushButton("✓ Confirm")
        detected_layout.addWidget(self.confirm_detected_button)
        layout.addLayout(detected_layout)

        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Seção de Seleção Manual
        manual_layout = QVBoxLayout()
        manual_layout.addWidget(QLabel("Or select an existing media:"))
            
        self.media_combo = QComboBox()
        self.media_combo.setEditable(True) # Permite que o usuário digite um novo nome
        self.media_combo.setPlaceholderText("Type or select a media...")
        for media in all_media:
            self.media_combo.addItem(media['title'], media['id'])
            
        manual_layout.addWidget(self.media_combo)
            
        self.confirm_manual_button = QPushButton("Save with this Media")
        manual_layout.addWidget(self.confirm_manual_button)
        layout.addLayout(manual_layout)

        # --- Conexões ---
        self.confirm_detected_button.clicked.connect(self.on_confirm_detected)
        self.confirm_manual_button.clicked.connect(self.on_confirm_manual)

    def on_confirm_detected(self):
        """ Usuário aceitou a sugestão automática. """
        media_id = self.media_service.get_or_create_media_id(self.detected_media_name)
        self.accepted.emit(media_id)
        self.accept() # Fecha o diálogo

    def on_confirm_manual(self):
        """ Usuário escolheu/digitou uma mídia manualmente. """
        selected_text = self.media_combo.currentText()
        if not selected_text:
            return # Não faz nada se estiver vazio
        
        media_id = self.media_service.get_or_create_media_id(selected_text)
        self.accepted.emit(media_id)
        self.accept() # Fecha o diálogo