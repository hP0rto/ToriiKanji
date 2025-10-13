from PyQt6.QtWidgets import * 
from PyQt6.QtGui import *
from PyQt6.QtCore import *

from gui.components.MediaManagementDialog import MediaManagementDialog
from gui.components.buttons_factory import create_text_button
from gui.components.KanjiCard import KanjiCard

from core.services.media_service import MediaService
from core.services.kanji_service import KanjiService

from utils.helpers import pixmap_null_handler
class OverlayPanel(QWidget):
    save_requested = pyqtSignal(dict) 

    def __init__(self, main_window, ):
        super().__init__()
        self.main_window = main_window # dependency injection 👍    
        self.result = None
        self.kanji_service = KanjiService()
        self.media_service = MediaService()
        
        
        media_layout = QHBoxLayout()
        media_layout.addWidget(QLabel("App:"))
        self.media_label = QLabel("N/A")
        self.media_label.setStyleSheet("font-weight: bold;")
        self.change_media_button = QPushButton("Change")
        
        media_layout.addWidget(self.media_label)
        media_layout.addStretch()
        media_layout.addWidget(self.change_media_button)
        
        self.change_media_button.clicked.connect(self.on_change_media)
        
        self._current_media_id = None
        
        # create layouts
        layout = QVBoxLayout()
        layout.addLayout(media_layout)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        splitter = QSplitter(Qt.Orientation.Vertical)

        self.setLayout(layout)
        
        
        top_container = QWidget()
        top_layout = QVBoxLayout(top_container)
        
        self.capture_label = QLabel("No capture made")
        self.capture_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.capture_label.resize(400,400)

        self.text_label = QLabel("")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setStyleSheet('font-size: 20px')
        
        top_layout.addWidget(self.capture_label)
        top_layout.addWidget(self.text_label)


        bottom_container = QWidget()
        bottom_layout = QVBoxLayout(bottom_container)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        container = QWidget()
        self.kanjis_layout = QVBoxLayout(container)
        
        scroll_area.setWidget(container)
        
        bottom_layout.addWidget(scroll_area)
        
        splitter.addWidget(top_container)
        splitter.addWidget(bottom_container)
        splitter.setSizes([self.height() // 2, self.height() // 2])

        layout.addWidget(splitter)
        
        self.save_button = None
        
        if not self.main_window.setting_service.user_settings.get("auto_save", False):
            self.save_button = create_text_button('Save', on_click=self.on_save_clicked)
            layout.addWidget(self.save_button)

        self.show()
    
    @pyqtSlot()
    def update_ui_from_settings(self):
        """
        Atualiza a UI com base nas configurações atuais.
        """
        auto_save_enabled = self.main_window.setting_service.user_settings.get("auto_save", False)

        if not auto_save_enabled:
            if not self.save_button:
                self.save_button = create_text_button('Save', on_click=self.on_save_clicked)
                self.layout().addWidget(self.save_button)
            self.save_button.setVisible(True)
        else:
            if self.save_button:
                self.save_button.setVisible(False)
        
    def on_save_clicked(self):
        """Emite o sinal pedindo pra salvar a captura"""
        if self.result and self._current_media_id is not None:
            self.result['media_id'] = self._current_media_id
            self.save_requested.emit(self.result)
        
    def show_capture(self, result):
        print(result)
        
        self.result = result
        image_path = result.get('image_path') 
        original_pixmap = result.get('pixmap')
        media_name = result.get('media_name', 'Unknown')
        
        if image_path:
            original_pixmap = pixmap_null_handler(QPixmap(image_path))
        
        self.media_label.setText(media_name)
        media_id = self.media_service.get_or_create_media_id(media_name)
        self._current_media_id = media_id

        scaled_pixmap = original_pixmap.scaled(
            self.capture_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        self.capture_label.setPixmap(scaled_pixmap)
        
        kanjis = result.get('kanjis', self.kanji_service.get_all_kanji_capture(result.get('id')))
        
        normalized_text = result.get('raw_text').replace("\n", "")

        self.text_label.setFixedWidth(self.width())
        self.text_label.setText(normalized_text)
        
        self.show_result(kanjis)
        
        self.main_window.custom_tab.show_tab(0)
        
    def show_result(self, result_dict):
        self.clear_layout(self.kanjis_layout)
        for row in result_dict:
            card = KanjiCard(row["kanji"], row["kunyomi"], row["onyomi"], row["meaning"], row["jlpt"])
            self.kanjis_layout.addWidget(card)
            
    def on_change_media(self):
        """ Abre um diálogo para o usuário gerenciar e selecionar uma mídia. """
        dialog = MediaManagementDialog(self.media_service, self)
        # Conecta o sinal do diálogo a um slot para atualizar a UI
        dialog.media_selected.connect(self.on_media_selected)
        dialog.exec()
        
    @pyqtSlot(dict)
    def on_media_selected(self, media_data):
        """ Atualiza a UI quando o usuário seleciona uma nova mídia no diálogo. """
        self.media_label.setText(media_data['title'])
        self._current_media_id = media_data['id']
    
    
    def clear_layout(self, layout: QLayout):
        """Removes all widgets from a given QLayout."""
        if layout is None:
            return

        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)  # Remove the widget from its parent
                widget.deleteLater()    # Schedule the widget for deletion
            else:
                # If the item is a nested layout, recursively clear it
                sub_layout = item.layout()
                if sub_layout is not None:
                    self.clear_layout(sub_layout)
                # Delete the layout item itself
                del item 