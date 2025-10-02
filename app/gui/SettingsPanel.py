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
        ]

        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(0, 3)
        grid.setColumnStretch(1, 1)

        self.enable_labels = {}

        for row, (label_text, key) in enumerate(options):
            state = self.setting_service.user_settings.get(key, False)
            
            label = QLabel(label_text)
            label.setStyleSheet("color: white; font-size: 14px;")
            
            enable_label = QLabel('Enable' if state else 'Disable')
            enable_label.setStyleSheet("color: white; font-size: 14px; padding-right: 10px;font-weight: bold;")
            
            switch = Switch()
            switch.setChecked(state)
            switch.clicked.connect(lambda check, enable_lab=enable_label, key=key: self.on_switch_changed(check,enable_lab,key))
            self.inputs[key] = switch

            self.enable_labels[key] = enable_label

            grid.addWidget(label, row, 0, alignment=Qt.AlignmentFlag.AlignLeft)
            grid.addWidget(enable_label, row, 1, alignment=Qt.AlignmentFlag.AlignLeft)
            grid.addWidget(switch, row, 1, alignment=Qt.AlignmentFlag.AlignRight)

        self.on_switch_changed(self.inputs["auto_save"].isChecked(), self.enable_labels["auto_save"], key="auto_save")
        
        main_layout.addLayout(grid)
                        
        # ---------- Other Settings Section ----------
        self.save_button = create_text_button('Save', on_click=self.save_settings)
        
        main_layout.addStretch()
        main_layout.addWidget(self.save_button)
        
        self.setLayout(main_layout)

    def on_switch_changed(self, checked, enable_label, key):
        enable_label.setText('Enable' if checked else 'Disable')
        
        if key == "auto_save":
            dependent_switch = self.inputs["save_image"]  # exemplo de outro switch
            dependent_label = self.enable_labels["save_image"]

            if checked:
                dependent_switch.setChecked(True)
                dependent_switch.setEnabled(False)  # bloqueia interação
                dependent_label.setText("Enable")
                dependent_label.setStyleSheet("color: #aaa; font-size: 14px; padding-right: 10px;font-weight: bold;")  # fica cinza
            else:
                dependent_switch.setEnabled(True)  # libera interação
                dependent_label.setStyleSheet("color: white; font-size: 14px; padding-right: 10px;font-weight: bold;")
        
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
        QMessageBox.information(self, "Settings", "Settings saved successfully!")
        self.settings_saved.emit()
        
    def on_save_error(self, error_msg):
        self.save_button.setEnabled(True)
        self.save_button.setText("Save")
        QMessageBox.critical(self, "Error", f"Error saving settings:\n{error_msg}")
        
    
    # def change_key(self, hotkey_input: HotkeyLineEdit):
    #     if hotkey_input.text():
    #         self.setting_service.edit_settings_file(hotkey_input.objectName(), hotkey_input.text())
    #         update_hotkey(self.main_window) 
            
               
            
       