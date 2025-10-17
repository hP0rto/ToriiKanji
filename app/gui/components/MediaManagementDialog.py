from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, 
                               QLineEdit, QPushButton, QMessageBox, QListWidgetItem)
from PyQt6.QtCore import pyqtSignal, Qt
from utils.i18n import t


class MediaManagementDialog(QDialog):
    # Sinal que emitirá o ID da mídia confirmada quando o usuário aceitar
    media_selected = pyqtSignal(dict)

    def __init__(self, media_service, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t('apps_manager'))
        self.setModal(True)
        self.media_service = media_service

        # --- Layout Principal ---
        layout = QVBoxLayout(self)

        # --- Lista de Mídias ---
        layout.addWidget(QLabel(t('existing_apps')))
        self.media_list = QListWidget()
        self.media_list.itemDoubleClicked.connect(self.on_select_media) # Duplo clique para selecionar
        layout.addWidget(self.media_list)

        # --- Botões de Ação para a Lista ---
        list_actions_layout = QHBoxLayout()
        self.select_button = QPushButton(t('select_app'))
        self.delete_button = QPushButton(t('remove_app'))
        list_actions_layout.addWidget(self.select_button)
        list_actions_layout.addWidget(self.delete_button)
        layout.addLayout(list_actions_layout)

        # --- Seção para Adicionar Nova Mídia ---
        layout.addWidget(QLabel(t('add_new_app')))
        new_media_layout = QHBoxLayout()
        self.new_media_input = QLineEdit()
        self.new_media_input.setPlaceholderText(t('new_app_placeholder'))
        self.add_button = QPushButton(t('add'))
        new_media_layout.addWidget(self.new_media_input)
        new_media_layout.addWidget(self.add_button)
        layout.addLayout(new_media_layout)
        
        # --- Preencher a lista inicial ---
        self.populate_media_list()

        # --- Conexões ---
        self.select_button.clicked.connect(self.on_select_media)
        self.delete_button.clicked.connect(self.on_delete_media)
        self.add_button.clicked.connect(self.on_add_media)
        self.new_media_input.returnPressed.connect(self.on_add_media) # Permite adicionar com "Enter"

    def populate_media_list(self):
        """ Limpa e preenche a lista com as mídias do banco de dados. """
        self.media_list.clear()
        all_media = self.media_service.get_all_media()
        for media in all_media:
            item = QListWidgetItem(media['title'])
            # Guardamos o dicionário inteiro no item para fácil acesso
            item.setData(Qt.ItemDataRole.UserRole, media)
            self.media_list.addItem(item)

    def on_select_media(self):
        """ Emite o sinal com a mídia selecionada e fecha o diálogo. """
        current_item = self.media_list.currentItem()
        if current_item:
            media_data = current_item.data(Qt.ItemDataRole.UserRole)
            self.media_selected.emit(media_data)
            self.accept() # Fecha o diálogo com sucesso

    def on_delete_media(self):
        """ Deleta a mídia selecionada após confirmação. """
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
            # Remove o item da lista visualmente
            self.media_list.takeItem(self.media_list.row(current_item))
            QMessageBox.information(self, t('success'), t('media_removed'))

    def on_add_media(self):
        """ Adiciona uma nova mídia a partir do campo de texto. """
        new_title = self.new_media_input.text().strip()
        if not new_title:
            QMessageBox.warning(self, t('attention'), t('empty_media_name'))
            return

        # O serviço já lida com a lógica de não criar duplicatas
        new_media_id = self.media_service.get_or_create_media_id(new_title)
        
        # Limpa o input e atualiza a lista
        self.new_media_input.clear()
        self.populate_media_list()

        # Opcional: Selecionar o item recém-criado na lista
        for i in range(self.media_list.count()):
            item = self.media_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole)['id'] == new_media_id:
                self.media_list.setCurrentItem(item)
                break