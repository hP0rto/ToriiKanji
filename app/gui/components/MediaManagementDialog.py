from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from utils.i18n import t


class MediaManagementDialog(QDialog):
    # Signal emitting the selected media when the user picks one
    media_selected = pyqtSignal(dict)

    def __init__(self, media_service, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t('apps_manager'))
        self.setModal(True)
        self.media_service = media_service

        # --- Main Layout ---
        layout = QVBoxLayout(self)

        # --- Media List ---
        layout.addWidget(QLabel(t('existing_apps')))
        self.media_list = QListWidget()
        self.media_list.itemDoubleClicked.connect(self.on_select_media) # Double click to select
        layout.addWidget(self.media_list)

        # --- List Action Buttons ---
        list_actions_layout = QHBoxLayout()
        self.select_button = QPushButton(t('select_app'))
        self.delete_button = QPushButton(t('remove_app'))
        list_actions_layout.addWidget(self.select_button)
        list_actions_layout.addWidget(self.delete_button)
        layout.addLayout(list_actions_layout)

        # --- Add New Media Section ---
        layout.addWidget(QLabel(t('add_new_app')))
        new_media_layout = QHBoxLayout()
        self.new_media_input = QLineEdit()
        self.new_media_input.setPlaceholderText(t('new_app_placeholder'))
        self.add_button = QPushButton(t('add'))
        new_media_layout.addWidget(self.new_media_input)
        new_media_layout.addWidget(self.add_button)
        layout.addLayout(new_media_layout)
        
        # --- Populate the initial list ---
        self.populate_media_list()

        # --- Connections ---
        self.select_button.clicked.connect(self.on_select_media)
        self.delete_button.clicked.connect(self.on_delete_media)
        self.add_button.clicked.connect(self.on_add_media)
        self.new_media_input.returnPressed.connect(self.on_add_media) # Allows adding with "Enter"

    def populate_media_list(self):
        """ Clear and fill the list with media from the database. """
        self.media_list.clear()
        all_media = self.media_service.get_all_media()
        for media in all_media:
            item = QListWidgetItem(media['title'])
            # Store the whole dict in the item for easy access
            item.setData(Qt.ItemDataRole.UserRole, media)
            self.media_list.addItem(item)

    def on_select_media(self):
        """ Emit the signal with the selected media and close the dialog. """
        current_item = self.media_list.currentItem()
        if current_item:
            media_data = current_item.data(Qt.ItemDataRole.UserRole)
            self.media_selected.emit(media_data)
            self.accept() # Close the dialog successfully

    def on_delete_media(self):
        """ Delete the selected media after confirmation. """
        current_item = self.media_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, t('attention'), "Select a media to remove.")
            return

        media_data = current_item.data(Qt.ItemDataRole.UserRole)
        confirm = QMessageBox.question(
            self,
            t('confirm_removal_title'),
            t('confirm_removal_body', title=media_data['title']),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            self.media_service.delete_media(media_data['id'])
            # Visually remove the item from the list
            self.media_list.takeItem(self.media_list.row(current_item))
            QMessageBox.information(self, t('success'), t('media_removed'))

    def on_add_media(self):
        """ Add a new media from the text field. """
        new_title = self.new_media_input.text().strip()
        if not new_title:
            QMessageBox.warning(self, t('attention'), t('empty_media_name'))
            return

        # The service already avoids creating duplicates
        new_media_id = self.media_service.get_or_create_media_id(new_title)
        
        # Clear the input and refresh the list
        self.new_media_input.clear()
        self.populate_media_list()

        # Optional: select the newly created item in the list
        for i in range(self.media_list.count()):
            item = self.media_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole)['id'] == new_media_id:
                self.media_list.setCurrentItem(item)
                break
