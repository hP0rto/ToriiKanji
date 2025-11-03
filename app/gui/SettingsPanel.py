from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QMessageBox, QHBoxLayout
from PyQt6.QtCore import Qt, QRunnable, QThreadPool, pyqtSignal, QObject

from core.services.hotkey_services import update_hotkey
from core.services.setting_services import SettingsService


from gui.components.Switch import Switch
from gui.components.HotkeyLineEdit import HotkeyLineEdit
from gui.components.buttons_factory import create_text_button

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)
class SaveWorker(QRunnable):
    def __init__(self, inputs, setting_service, main_window):
        super().__init__()
        self.inputs = inputs
        self.setting_service = setting_service
        self.main_window = main_window
        self.signals = WorkerSignals()
        

    def run(self):
        try:
            # Simula operação de salvamento
            for key, widget in self.inputs.items():
                if isinstance(widget, HotkeyLineEdit):
                    self.setting_service.edit_settings_file(key, widget.text())
                elif isinstance(widget, Switch):
                    self.setting_service.edit_settings_file(key, widget.isChecked())
        
            update_hotkey(self.main_window) 
            self.signals.finished.emit()

        except Exception as e:
            self.signals.error.emit(str(e))


class SettingsPanel(QWidget):
    settings_saved = pyqtSignal()
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window # dependency injection 👍    
        
        self.setWindowTitle("Configurações")
        
        self.setting_service = SettingsService()
        self.inputs = {}
        self.threadpool = QThreadPool() 

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        title = QLabel('Hotkeys')
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        main_layout.addWidget(title)
        
        # ---------- Hotkeys Section ----------
        hotkeys = [
            ("Exit", "exit_key"),
            ("Capture", "capture_key"),
            ("Toggle Visibility", "toggle_key"),
        ]
        
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setColumnStretch(0,1)
        grid.setColumnStretch(1,1)

        for row, (label_text, hotkey) in enumerate(hotkeys):
            action_label = QLabel(label_text)
            action_label.setStyleSheet("color: white; font-size: 16px; border: 1px solid #aaa; border-radius: 6px; padding: 5px 10px ;")


            hotkey_input = HotkeyLineEdit(self.setting_service.user_settings.get(hotkey))
            hotkey_input.setObjectName(hotkey)
            hotkey_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
            hotkey_input.setStyleSheet("color: white; font-size: 16px; border: 1px solid #aaa; border-radius: 6px; padding: 5px 10px ;")
            self.inputs[hotkey] = hotkey_input
            
            #hotkey_input.editingFinished.connect(lambda h=hotkey_input: self.change_key(h))

            grid.addWidget(action_label, row, 0)
            grid.addWidget(hotkey_input, row, 1)
            

        main_layout.addLayout(grid)
        # ---------- Saving Settings ----------
        
        

        title2 = QLabel('Saving')
        title2.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        main_layout.addWidget(title2)
        
        

        options = [
            ("Save capture automatically", "auto_save"),
            ("Save image captures on disk", "save_image"),
            ("Show media dialog on auto-save", "show_media_dialog")
        ]

        self.saving_grid = QVBoxLayout()
        self.saving_grid.setSpacing(12)
        self.enable_labels = {}

        for row, (label_text, key) in enumerate(options):
            state = self.setting_service.user_settings.get(key, False)
            label = QLabel(label_text)
            label.setStyleSheet("color: white; font-size: 14px;")
            enable_label = QLabel('Enable' if state else 'Disable')
            enable_label.setStyleSheet("color: white; font-size: 14px; padding-right: 10px;font-weight: bold;")
            enable_label.setMinimumWidth(70)
            switch = Switch()
            switch.setChecked(state)
            switch.clicked.connect(lambda check, enable_lab=enable_label, key=key: self.on_switch_changed(check,enable_lab,key))
            self.inputs[key] = switch
            self.enable_labels[key] = enable_label
            row_layout = QHBoxLayout()
            row_layout.addWidget(label, 3)
            row_layout.addWidget(enable_label, 1)
            row_layout.addWidget(switch, 0)
            row_layout.setSpacing(8)
            row_layout.setStretch(0, 3)
            row_layout.setStretch(1, 1)
            row_layout.setStretch(2, 0)
            self.saving_grid.addLayout(row_layout)

        # Adiciona o switch para show_media_dialog, mas só mostra se auto_save estiver ativado
        # self.media_dialog_label = QLabel('Show media dialog on auto-save')
        # self.media_dialog_label.setStyleSheet("color: white; font-size: 14px;")
        # self.media_dialog_switch = Switch()
        # media_dialog_state = self.setting_service.user_settings.get('show_media_dialog', True)
        # self.media_dialog_switch.setChecked(media_dialog_state)
        # self.media_dialog_switch.clicked.connect(lambda check: self.on_media_dialog_switch_changed(check))
        # self.inputs['show_media_dialog'] = self.media_dialog_switch

        # Só adiciona ao grid se auto_save estiver ativado
        # if self.inputs["auto_save"].isChecked():
        #     self.saving_grid.addWidget(self.media_dialog_label, len(options), 0, alignment=Qt.AlignmentFlag.AlignLeft)
        #     self.saving_grid.addWidget(self.media_dialog_switch, len(options), 1, alignment=Qt.AlignmentFlag.AlignRight)

        self.on_switch_changed(self.inputs["auto_save"].isChecked(), self.enable_labels["auto_save"], key="auto_save")
        main_layout.addLayout(self.saving_grid)
                        
        # ---------- Other Settings Section ----------
        self.save_button = create_text_button('Save', on_click=self.save_settings)
        
        main_layout.addStretch()
        main_layout.addWidget(self.save_button)
        
        self.setLayout(main_layout)

    def on_switch_changed(self, checked, enable_label, key):
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
                save_label.setStyleSheet("color: #aaa; font-size: 14px; padding-right: 10px;font-weight: bold;")

                show_media_switch.setEnabled(True)
                show_media_label.setStyleSheet("color: #aaa; font-size: 14px; padding-right: 10px;font-weight: bold;")
            else:
                save_switch.setEnabled(True)
                save_label.setStyleSheet("color: white; font-size: 14px; padding-right: 10px;font-weight: bold;")
                show_media_switch.setEnabled(False)
                show_media_label.setStyleSheet("color: #aaa; font-size: 14px; padding-right: 10px;font-weight: bold;")
                
    def on_media_dialog_switch_changed(self, checked):
        # Atualiza o valor na configuração
        self.setting_service.edit_settings_file('show_media_dialog', checked)
        
    def save_settings(self):
        self.save_button.setEnabled(False)
        self.save_button.setText("Saving...")

        # Cria worker
        worker = SaveWorker(self.inputs, self.setting_service, self.main_window)
        worker.signals.finished.connect(self.on_save_finished)
        worker.signals.error.connect(self.on_save_error)

        self.threadpool.start(worker)
        
        
    def on_save_finished(self):
        self.save_button.setEnabled(True)
        self.save_button.setText("Save")
        from utils.i18n import t
        QMessageBox.information(self, t('settings'), "Settings saved successfully!")
        self.settings_saved.emit()
        
    def on_save_error(self, error_msg):
        self.save_button.setEnabled(True)
        self.save_button.setText("Save")
        from utils.i18n import t
        QMessageBox.critical(self, t('error'), f"Error saving settings:\n{error_msg}")
            
               
            
       