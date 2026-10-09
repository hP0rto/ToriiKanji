"""
Settings panel for ToriiKanji.
Provides UI for configuring hotkeys, saving behavior, display mode, and more.
"""

from PyQt6.QtCore import QObject, QRunnable, Qt, QThreadPool, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from core.services.hotkey_services import update_hotkey
from core.services.setting_services import SettingsService
from gui.components.buttons_factory import create_text_button
from gui.components.HotkeyLineEdit import HotkeyLineEdit
from gui.components.Switch import Switch
from gui.theme import (
    FONT_SIZE_LG,
    FONT_SIZE_SM,
    TEXT_DISABLED,
    TEXT_MUTED,
    input_style,
    label_style,
)


class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)


class SaveWorker(QRunnable):
    """Background worker for saving settings to disk."""

    def __init__(self, inputs, setting_service, main_window):
        super().__init__()
        self.inputs = inputs
        self.setting_service = setting_service
        self.main_window = main_window
        self.signals = WorkerSignals()

    def run(self):
        try:
            for key, widget in self.inputs.items():
                if isinstance(widget, HotkeyLineEdit):
                    self.setting_service.edit_settings_file(key, widget.text())
                elif isinstance(widget, Switch):
                    self.setting_service.edit_settings_file(key, widget.isChecked())
                elif isinstance(widget, QSlider):
                    self.setting_service.edit_settings_file(key, widget.value())
                elif isinstance(widget, QComboBox):
                    self.setting_service.edit_settings_file(key, widget.currentData())
                elif isinstance(widget, QLabel):
                    # For display-only labels (like folder path), skip
                    pass

            update_hotkey(self.main_window)
            self.signals.finished.emit()
        except Exception as e:
            self.signals.error.emit(str(e))


class SettingsPanel(QWidget):
    settings_saved = pyqtSignal()

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Settings")

        self.setting_service = SettingsService()
        self.inputs = {}
        self.threadpool = QThreadPool()

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ─── Hotkeys Section ─────────────────────────────────────────────
        title = QLabel('Hotkeys')
        title.setStyleSheet(label_style(FONT_SIZE_LG, bold=True))
        main_layout.addWidget(title)

        hotkeys = [
            ("Exit", "exit_key"),
            ("Capture", "capture_key"),
            ("Toggle Visibility", "toggle_key"),
        ]

        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        for row, (label_text, hotkey) in enumerate(hotkeys):
            action_label = QLabel(label_text)
            action_label.setStyleSheet(input_style())

            hotkey_input = HotkeyLineEdit(self.setting_service.user_settings.get(hotkey))
            hotkey_input.setObjectName(hotkey)
            hotkey_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
            hotkey_input.setStyleSheet(input_style())
            self.inputs[hotkey] = hotkey_input

            grid.addWidget(action_label, row, 0)
            grid.addWidget(hotkey_input, row, 1)

        main_layout.addLayout(grid)

        # ─── Saving Section ──────────────────────────────────────────────
        title2 = QLabel('Saving')
        title2.setStyleSheet(label_style(FONT_SIZE_LG, bold=True))
        main_layout.addWidget(title2)

        options = [
            ("Save capture automatically", "auto_save"),
            ("Save image captures on disk", "save_image"),
            ("Show media dialog on auto-save", "show_media_dialog"),
        ]

        self.saving_grid = QVBoxLayout()
        self.saving_grid.setSpacing(12)
        self.enable_labels = {}

        for row, (label_text, key) in enumerate(options):
            state = self.setting_service.user_settings.get(key, False)
            label = QLabel(label_text)
            label.setStyleSheet(label_style(FONT_SIZE_SM))

            enable_label = QLabel('Enable' if state else 'Disable')
            enable_label.setStyleSheet(label_style(FONT_SIZE_SM, bold=True))
            enable_label.setMinimumWidth(70)

            switch = Switch()
            switch.setChecked(state)
            switch.clicked.connect(
                lambda check, el=enable_label, k=key: self.on_switch_changed(check, el, k)
            )
            self.inputs[key] = switch
            self.enable_labels[key] = enable_label

            row_layout = QHBoxLayout()
            row_layout.addWidget(label, 3)
            row_layout.addWidget(enable_label, 1)
            row_layout.addWidget(switch, 0)
            row_layout.setSpacing(8)
            self.saving_grid.addLayout(row_layout)

        # Apply initial auto_save state
        self.on_switch_changed(
            self.inputs["auto_save"].isChecked(),
            self.enable_labels["auto_save"],
            key="auto_save"
        )
        main_layout.addLayout(self.saving_grid)

        # ─── Display Section ─────────────────────────────────────────────
        title3 = QLabel('Display')
        title3.setStyleSheet(label_style(FONT_SIZE_LG, bold=True))
        main_layout.addWidget(title3)

        # Display Mode
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Display Mode")
        mode_label.setStyleSheet(label_style(FONT_SIZE_SM))

        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Overlay (Side Panel)", "overlay")
        self.mode_combo.addItem("Windowed", "windowed")
        self.mode_combo.addItem("Compact (Minimal)", "compact")

        current_mode = self.setting_service.get('display_mode', 'overlay')
        for i in range(self.mode_combo.count()):
            if self.mode_combo.itemData(i) == current_mode:
                self.mode_combo.setCurrentIndex(i)
                break
        self.inputs['display_mode'] = self.mode_combo

        mode_layout.addWidget(mode_label, 3)
        mode_layout.addWidget(self.mode_combo, 2)
        main_layout.addLayout(mode_layout)

        # Opacity Slider
        opacity_layout = QHBoxLayout()
        opacity_label = QLabel("Window Opacity")
        opacity_label.setStyleSheet(label_style(FONT_SIZE_SM))

        current_opacity = self.setting_service.get('window_opacity', 92)
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(20, 100)
        self.opacity_slider.setValue(current_opacity)
        self.opacity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.opacity_slider.setTickInterval(10)

        self.opacity_value_label = QLabel(f"{current_opacity}%")
        self.opacity_value_label.setStyleSheet(label_style(FONT_SIZE_SM, bold=True))
        self.opacity_value_label.setMinimumWidth(45)

        self.opacity_slider.valueChanged.connect(
            lambda val: self.opacity_value_label.setText(f"{val}%")
        )
        self.inputs['window_opacity'] = self.opacity_slider

        opacity_layout.addWidget(opacity_label, 3)
        opacity_layout.addWidget(self.opacity_slider, 2)
        opacity_layout.addWidget(self.opacity_value_label, 0)
        main_layout.addLayout(opacity_layout)

        # ─── OCR Section ─────────────────────────────────────────────────
        title4 = QLabel('OCR')
        title4.setStyleSheet(label_style(FONT_SIZE_LG, bold=True))
        main_layout.addWidget(title4)

        ocr_layout = QHBoxLayout()
        ocr_label = QLabel("Image Pre-processing")
        ocr_label.setStyleSheet(label_style(FONT_SIZE_SM))

        ocr_state = self.setting_service.get('ocr_preprocessing', True)
        ocr_enable_label = QLabel('Enable' if ocr_state else 'Disable')
        ocr_enable_label.setStyleSheet(label_style(FONT_SIZE_SM, bold=True))
        ocr_enable_label.setMinimumWidth(70)

        ocr_switch = Switch()
        ocr_switch.setChecked(ocr_state)
        ocr_switch.clicked.connect(
            lambda check, el=ocr_enable_label: el.setText('Enable' if check else 'Disable')
        )
        self.inputs['ocr_preprocessing'] = ocr_switch

        ocr_layout.addWidget(ocr_label, 3)
        ocr_layout.addWidget(ocr_enable_label, 1)
        ocr_layout.addWidget(ocr_switch, 0)
        main_layout.addLayout(ocr_layout)

        # ─── Capture Folder Section ──────────────────────────────────────
        folder_layout = QHBoxLayout()
        folder_label = QLabel("Capture Save Folder")
        folder_label.setStyleSheet(label_style(FONT_SIZE_SM))

        current_folder = self.setting_service.get('capture_save_dir', '')
        self.folder_path_label = QLabel(current_folder if current_folder else "(Default)")
        self.folder_path_label.setStyleSheet(label_style(FONT_SIZE_SM, color=TEXT_MUTED))
        self.folder_path_label.setWordWrap(True)

        folder_button = QPushButton("Browse...")
        folder_button.clicked.connect(self.browse_capture_folder)

        folder_layout.addWidget(folder_label, 2)
        folder_layout.addWidget(self.folder_path_label, 2)
        folder_layout.addWidget(folder_button, 1)
        main_layout.addLayout(folder_layout)

        # ─── Save Button ────────────────────────────────────────────────
        self.save_button = create_text_button('Save', on_click=self.save_settings)

        main_layout.addStretch()
        main_layout.addWidget(self.save_button)

        self.setLayout(main_layout)

    def on_switch_changed(self, checked, enable_label, key):
        """Handle switch state changes with cascading logic."""
        enable_label.setText('Enable' if checked else 'Disable')

        if key == "auto_save":
            save_switch = self.inputs["save_image"]
            save_label = self.enable_labels["save_image"]
            show_media_switch = self.inputs["show_media_dialog"]
            show_media_label = self.enable_labels["show_media_dialog"]

            if checked:
                save_switch.setChecked(True)
                save_switch.setEnabled(False)
                save_label.setText("Enable")
                save_label.setStyleSheet(label_style(FONT_SIZE_SM, color=TEXT_DISABLED, bold=True))

                show_media_switch.setEnabled(True)
                show_media_label.setStyleSheet(label_style(FONT_SIZE_SM, color=TEXT_MUTED, bold=True))
            else:
                save_switch.setEnabled(True)
                save_label.setStyleSheet(label_style(FONT_SIZE_SM, bold=True))
                show_media_switch.setEnabled(False)
                show_media_label.setStyleSheet(label_style(FONT_SIZE_SM, color=TEXT_DISABLED, bold=True))

    def browse_capture_folder(self):
        """Open a folder picker for the capture save directory."""
        folder = QFileDialog.getExistingDirectory(self, "Select Capture Save Folder")
        if folder:
            self.folder_path_label.setText(folder)
            self.setting_service.edit_settings_file('capture_save_dir', folder)

    def save_settings(self):
        """Save all settings to disk in a background thread."""
        self.save_button.setEnabled(False)
        self.save_button.setText("Saving...")

        worker = SaveWorker(self.inputs, self.setting_service, self.main_window)
        worker.signals.finished.connect(self.on_save_finished)
        worker.signals.error.connect(self.on_save_error)

        self.threadpool.start(worker)

    def on_save_finished(self):
        """Handle successful settings save."""
        self.save_button.setEnabled(True)
        self.save_button.setText("Save")
        QMessageBox.information(self, "Settings", "Settings saved successfully!")
        self.settings_saved.emit()

    def on_save_error(self, error_msg):
        """Handle settings save error."""
        self.save_button.setEnabled(True)
        self.save_button.setText("Save")
        QMessageBox.critical(self, "Error", f"Error saving settings:\n{error_msg}")
