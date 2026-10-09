"""
Overlay panel for ToriiKanji.
Displays the current capture, OCR text, and kanji analysis cards.
"""

from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLayout,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from gui.components.buttons_factory import create_text_button
from gui.components.KanjiCard import KanjiCard
from gui.components.MediaManagementDialog import MediaManagementDialog
from gui.theme import PRIMARY, text_edit_style
from utils.helpers import pixmap_null_handler
from utils.i18n import t


class OverlayPanel(QWidget):
    """Panel that displays OCR results with the captured image and kanji cards."""

    save_requested = pyqtSignal(dict)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.result = None
        # Use the application's shared KanjiService (injected via MainWindow)
        self.kanji_service = self.main_window.kanji_service
        # Use the application's shared MediaService so signals propagate
        self.media_service = self.main_window.media_service

        # Media info row
        media_layout = QHBoxLayout()
        media_layout.addWidget(QLabel("App:"))
        self.media_label = QLabel("N/A")
        self.media_label.setStyleSheet("font-weight: bold;")
        self.change_media_button = QPushButton("Change")

        media_layout.addWidget(self.media_label)
        media_layout.addStretch()
        media_layout.addWidget(self.change_media_button)

        self.change_media_button.clicked.connect(self.on_change_media)
        self.change_media_button.hide()

        self._current_media_id = None

        # Main layout
        layout = QVBoxLayout()
        layout.addLayout(media_layout)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        splitter = QSplitter(Qt.Orientation.Vertical)
        self.setLayout(layout)

        # Top section: image and text
        top_container = QWidget()
        top_layout = QVBoxLayout(top_container)

        self.capture_label = QLabel("No capture made")
        self.capture_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.capture_label.resize(400, 400)

        self.text_box = QTextEdit("")
        self.text_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_box.setReadOnly(True)
        self.text_box.setStyleSheet('font-size: 24px;')
        self.text_box.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.text_box.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        top_layout.addWidget(self.capture_label)
        top_layout.addWidget(self.text_box)

        # Bottom section: kanji cards
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
        splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {PRIMARY};
                height: 3px;
            }}
        """)

        layout.addWidget(splitter)

        # Save button (only visible when auto_save is off)
        self.save_button = create_text_button(t('save'), on_click=self.on_save_clicked)
        self.save_button.hide()
        layout.addWidget(self.save_button)

        self.update_ui_from_settings()
        self.show()

    def resizeEvent(self, event):
        """Adjust text box sizing on resize."""
        super().resizeEvent(event)
        font_size = max(24, min(48, int(self.height() * 0.06)))
        self.text_box.setStyleSheet(text_edit_style(font_size))
        self.text_box.setFixedWidth(self.width() - 40)
        self.text_box.setMinimumHeight(60)
        self.text_box.setMaximumHeight(int(self.height() * 0.28))

    @pyqtSlot()
    def update_ui_from_settings(self):
        """Update the UI based on current settings (e.g., auto_save state)."""
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
        """Emit save_requested signal when the Save button is clicked."""
        if self.result and self._current_media_id is not None:
            # Prevent double-clicks
            self.save_button.setEnabled(False)
            self.save_button.setText("Saving...")

            self.result['media_id'] = self._current_media_id
            self.save_requested.emit(self.result)

    def show_capture(self, result):
        """Display a capture result (new or from collection)."""
        self.result = result
        image_path = result.get('image_path')
        original_pixmap = result.get('pixmap')
        media_name = result.get('media_name')
        is_existing_capture = 'id' in result and result.get('id') is not None

        if is_existing_capture:
            # Viewing a capture from the collection
            self.save_button.hide()
            self.change_media_button.show()

            media = self.media_service.get_media_by_id(result.get('media_id'))
            if media:
                media_name = media['title']
            self._current_media_id = result.get('media_id')
        else:
            # Viewing a NEW capture (post-OCR)
            auto_save_enabled = self.main_window.setting_service.user_settings.get("auto_save", False)
            if auto_save_enabled:
                self.save_button.hide()
            else:
                self.save_button.show()
                self.save_button.setEnabled(True)
                self.save_button.setText('Save')

            self.change_media_button.show()

            media_name = result.get('media_name')
            media_id = self.media_service.get_or_create_media_id(media_name)
            self._current_media_id = media_id

        if image_path:
            original_pixmap = pixmap_null_handler(QPixmap(image_path))

        self.media_label.setText(media_name.title() if media_name else 'N/A')

        scaled_pixmap = original_pixmap.scaled(
            self.capture_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.capture_label.setPixmap(scaled_pixmap)

        kanjis = result.get('kanjis', self.kanji_service.get_all_kanji_capture(result.get('id')))

        normalized_text = result.get('raw_text').replace("\n", "")
        self.text_box.setHtml(f'<div style="text-align:center;">{normalized_text}</div>')
        self.text_box.setFixedWidth(self.width() - 40)

        self.show_result(kanjis)
        self.main_window.custom_tab.show_tab(0)

    @pyqtSlot(int)
    def on_capture_saved(self, capture_id):
        """Update the save button state when a capture is saved."""
        if hasattr(self, 'save_button') and self.save_button.isVisible():
            self.save_button.setEnabled(False)
            self.save_button.setText('Saved')

    def show_result(self, result_dict):
        """Display kanji cards for the given kanji data."""
        self.clear_layout(self.kanjis_layout)
        for row in result_dict:
            card = KanjiCard(
                row["kanji"],
                row.get("kunyomi", ""),
                row.get("onyomi", ""),
                row.get("meaning", ""),
                row.get("jlpt"),
                row.get("strokes")
            )
            self.kanjis_layout.addWidget(card)

    def on_change_media(self):
        """Open the media management dialog for changing media association."""
        dialog = MediaManagementDialog(self.media_service, self)
        dialog.media_selected.connect(self.on_media_selected)
        dialog.exec()

    @pyqtSlot(dict)
    def on_media_selected(self, media_data):
        """Handle media selection from the management dialog."""
        self.media_label.setText(media_data['title'])
        self._current_media_id = media_data['id']

        is_existing_capture = 'id' in self.result and self.result.get('id') is not None
        if is_existing_capture:
            self.main_window.capture_service.update_capture_media(
                self.result['id'],
                self._current_media_id
            )
            QMessageBox.information(self, t('success'), t('media_removed'))

    def update_displayed_media(self, media_name, media_id):
        """Public slot to force-update the displayed media info."""
        self.media_label.setText(media_name)
        self._current_media_id = media_id

    def clear_layout(self, layout: QLayout):
        """Remove all widgets from a given QLayout."""
        if layout is None:
            return

        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
            else:
                sub_layout = item.layout()
                if sub_layout is not None:
                    self.clear_layout(sub_layout)
                del item
