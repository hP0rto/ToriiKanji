from datetime import datetime
import os
from tkinter import Tk

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
from PyQt6.QtWidgets import   QSystemTrayIcon

from core.services.ocr_service import OcrService
from core.services.setting_services import SettingsService
from core.services.kanji_service import KanjiService 
from core.workers.db_worker import DbWorker
from core.workers.ocr_worker import OcrWorker

from utils.helpers import run_in_thread
from ocr.ScreenCapture import ScreenCapture
from db.repositories.capture_repository import CaptureRepository

class CaptureService(QObject):
    ocr_finished = pyqtSignal(dict)
    capture_saved = pyqtSignal(int)
    image_saved = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.kanji_service = KanjiService() # Instancie o KanjiService
        self.ocr_service = OcrService()   
        self.capture_repo = CaptureRepository()
        self.settings_service = SettingsService()
        
        self.save_dir = "captures"
        os.makedirs("captures", exist_ok=True)
        
        self.threads = []
        self.workers = []

    def start_full_capture_flow(self):
        """ Inicia o fluxo completo: screenshot -> ocr -> salvar (se aplicável). """
        if self.main_window.isVisible():
            self.main_window.toggle_visibility()

        screenshot_result = self._start_screenshot()
        if screenshot_result and screenshot_result.get('screenshot'):
            self._run_ocr_in_thread(
                screenshot_result.get('screenshot'),
                screenshot_result.get('captured_app_name')
            )
        else:
            self.main_window.toggle_visibility()
            
    def _start_screenshot(self):
        root = Tk()
        app = ScreenCapture(root)
        root.mainloop()
    
        
        return {
            'captured_app_name': app.captured_app_name,
            'file_name': app.file_name,
            'screenshot': app.screenshot
        }

    def _run_ocr_in_thread(self, image, captured_app_name):
        thread = QThread()
        worker = OcrWorker(self.ocr_service, image)
        
        on_finished_callback = lambda ocr_result: self._handle_ocr_result(ocr_result, captured_app_name)
        
        thread = run_in_thread(
            worker=worker,
            on_finished=on_finished_callback,
            on_error=self._handle_error
            )
        
        # Guardamos a referência para que não seja coletado pelo garbage collector
        self.threads.append(thread)
        self.workers.append(worker)

    def _handle_ocr_result(self, result, captured_app_name):
        """ Chamado quando o OCR termina. Decide o que fazer a seguir. """
        kanjis = result["kanjis"]
        result['kanjis'] = self.kanji_service.get_all_kanjis(kanjis)
  
        result['media_name'] = captured_app_name or 'Unknown'
    
        self.ocr_finished.emit(result)
            
    def _handle_error(self, msg):
        # Propaga o erro para a UI através de um sinal
        self.error_occurred.emit(msg)    

    
    @pyqtSlot(dict, int) # Agora recebe o resultado E o media_id
    def start_save_flow(self, result_data, media_id):

        print(f"Serviço: Iniciando fluxo de salvamento com media_id: {media_id}")
        result_data['media_id'] = media_id
        
        auto_save = self.settings_service.user_settings.get('auto_save', False)
        save_image = self.settings_service.user_settings.get('save_image', False)
        
        if auto_save:
            print("Serviço: Iniciando fluxo de salvamento automático.")
            self._run_full_save_in_thread(result_data)
        elif save_image:
            self.save_image_to_disk(result_data['pixmap'])
        elif not auto_save and not save_image:
            self._run_full_save_in_thread(result_data)
        
    def _run_save_capture_in_disk_in_thread(self,result):
        worker = DbWorker(self, 'save_image_to_disk', result['pixmap'])
        
        thread = run_in_thread(
            worker=worker,
            on_finished=lambda image_path: self.main_window.tray_icon.showMessage(
                'Image', f'Image {image_path} saved successfully!'
            ),
            on_error=self._handle_error
        )
        
        self.threads.append(thread)
        self.workers.append(worker)
        
    def _run_full_save_in_thread(self, result):
        worker = DbWorker(self, 'save_image_to_disk', result['pixmap'])
        
        thread = run_in_thread(
            worker=worker,
            on_finished=lambda image_path: self._run_save_capture_data_in_thread(result,image_path),
            on_error=self._handle_error
            )
        
        # Guardamos a referência para que não seja coletado pelo garbage collector
        self.threads.append(thread)
        self.workers.append(worker)
        
    def _run_save_capture_data_in_thread(self, result, image_path):
        """ Passo 2 do fluxo: Salva os metadados da captura no banco de dados. """
        capture_worker = DbWorker(
            self,
            "save_capture_to_db", # Renomeei para ser mais claro
            result['raw_text'],
            image_path,
            result["kanjis"],
            result['media_id']
        )
        
        def on_finished(id):
            self.main_window.tray_icon.showMessage(
                'Capture', f'Capture {id} saved successfully!'
            )
            self.main_window.custom_tab.collection_panel.add_capture_to_grid(id)
        
        thread = run_in_thread(
            worker=capture_worker,
            on_finished=on_finished,
            on_error=self._handle_error
        )
        
        self.threads.append(thread)
        self.workers.append(capture_worker)


    def save_capture_to_db(self,raw_text, image_path, kanjis, media_id=None):
        capture_id = self.capture_repo.insert_capture(raw_text, image_path, media_id)

        for k in kanjis:
            self.capture_repo.insert_capture_kanji(capture_id, k['kanji'])
            
        return capture_id
        
    def save_image_to_disk(self, image):
        print(image)
        image_path = None
        
        filename = f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        image_path = os.path.join(self.save_dir, filename)
        image.save(image_path)
        
        return image_path
    
    def get_captures(self):
        print('Collection call!')
        return self.capture_repo.select_captures()
    
    def remove_capture(self, capture):
        self.capture_repo.delete_capture(capture['id'])
        image_path = capture['image_path']
        
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
        
    def find_by_id_capture(self, id):
        return self.capture_repo.select_capture_by_id(id)

