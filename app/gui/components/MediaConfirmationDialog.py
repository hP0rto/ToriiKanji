from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QComboBox, QDialog, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout

from utils.i18n import t


class MediaConfirmationDialog(QDialog):
    # Signal emitting the confirmed media ID when the user accepts
    accepted = pyqtSignal(int)

    def __init__(self, detected_media_name, all_media, media_service, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t('confirm_removal_title'))
        self.setModal(True) # Blocks interaction with the main window

        self.media_service = media_service
        self.detected_media_name = detected_media_name
        self.all_media = all_media

        # --- Layout and Widgets ---
        layout = QVBoxLayout(self)
        
        # Automatic detection section
        detected_layout = QHBoxLayout()
        detected_layout.addWidget(QLabel(f"Detected media: <b>{detected_media_name}</b>"))
        self.confirm_detected_button = QPushButton("✓ Confirm")
        detected_layout.addWidget(self.confirm_detected_button)
        layout.addLayout(detected_layout)

        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Manual selection section
        manual_layout = QVBoxLayout()
        manual_layout.addWidget(QLabel("Or select an existing media:"))
            
        self.media_combo = QComboBox()
        self.media_combo.setEditable(True) # Lets the user type a new name
        self.media_combo.setPlaceholderText("Type or select a media...")
        for media in all_media:
            self.media_combo.addItem(media['title'], media['id'])
            
        manual_layout.addWidget(self.media_combo)
            
        self.confirm_manual_button = QPushButton("Save with this Media")
        manual_layout.addWidget(self.confirm_manual_button)
        layout.addLayout(manual_layout)

        # --- Connections ---
        self.confirm_detected_button.clicked.connect(self.on_confirm_detected)
        self.confirm_manual_button.clicked.connect(self.on_confirm_manual)

    def on_confirm_detected(self):
        """ User accepted the automatic suggestion. """
        media_id = self.media_service.get_or_create_media_id(self.detected_media_name)
        self.accepted.emit(media_id)
        self.accept() # Close the dialog

    def on_confirm_manual(self):
        """ User selected/typed a media manually. """
        selected_text = self.media_combo.currentText()
        if not selected_text:
            return # Do nothing if empty
        
        media_id = self.media_service.get_or_create_media_id(selected_text)
        self.accepted.emit(media_id)
        self.accept() # Close the dialog
