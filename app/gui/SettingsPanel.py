from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QMessageBox
from PyQt6.QtGui import QMovie, QIcon, QPixmap
from PyQt6.QtCore import Qt, QRunnable, QThreadPool, pyqtSignal, QObject
from core.services.hotkey_services import update_hotkey
from gui.components.HotkeyLineEdit import HotkeyLineEdit
from gui.components.buttons_factory import create_text_button
from core.services.setting_services import SettingsService

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
                    

        
            update_hotkey(self.main_window) 
            # Se necessário: update_hotkey(self.main_window)
            self.signals.finished.emit()

        except Exception as e:
            self.signals.error.emit(str(e))


class SettingsPanel(QWidget):
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

        title2 = QLabel('Saving')
        title2.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        main_layout.addWidget(title2)
        
        # ---------- Other Settings Section ----------
        self.save_button = create_text_button('Save', on_click=self.save_settings)
        
        main_layout.addStretch()
        main_layout.addWidget(self.save_button)
        
        self.setLayout(main_layout)
        
        
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
        
    def on_save_error(self, error_msg):
        self.save_button.setEnabled(True)
        self.save_button.setText("Save")
        QMessageBox.critical(self, "Error", f"Error saving settings:\n{error_msg}")
        
    
    # def change_key(self, hotkey_input: HotkeyLineEdit):
    #     if hotkey_input.text():
    #         self.setting_service.edit_settings_file(hotkey_input.objectName(), hotkey_input.text())
    #         update_hotkey(self.main_window) 
            
               
            
       