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
    media_confirmation_required = pyqtSignal(dict, str)

    def __init__(self):
        super().__init__()
        self.kanji_service = KanjiService() 
        self.ocr_service = OcrService()   
        self.capture_repo = CaptureRepository()
        self.settings_service = SettingsService()
        
        self.last_confirmed_media_id = None
        
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
        
        detected_media_id = self.main_window.media_service.get_or_create_media_id(result['media_name'])
        
        if self.settings_service.user_settings.get('auto_save', False):
            show_media_dialog = self.settings_service.user_settings.get('show_media_dialog', True)
            # Só mostra o diálogo se a opção estiver ativada
            if show_media_dialog:
                # Condições para mostrar o diálogo:
                # 1. É a primeira captura (memória está vazia).
                # 2. A mídia detectada é DIFERENTE da última confirmada.
                if self.last_confirmed_media_id is None or self.last_confirmed_media_id != detected_media_id:
                    self.media_confirmation_required.emit(result, result['media_name'])
                else:
                    # O app é o mesmo, não precisa de diálogo. Salva direto.
                    print(f"Auto-save: Mídia '{result['media_name']}' já confirmada. Salvando diretamente.")
                    self.start_save_flow(result, self.last_confirmed_media_id)
            else:
                # Não mostra o diálogo, salva direto
                print("Auto-save: Configuração para não mostrar diálogo de mídia. Salvando diretamente.")
                self.start_save_flow(result, detected_media_id)
        else:
            # auto_save está desativado: não iniciar o fluxo de salvamento automaticamente
            print("Auto-save: desativado. Aguardando ação manual do usuário para salvar.")
            
    def _handle_error(self, msg):
        # Propaga o erro para a UI através de um sinal
        self.error_occurred.emit(msg)    

    
    @pyqtSlot(dict, int)
    def start_save_flow(self, result_data, media_id, is_manual=False):
        print(f"Serviço: Iniciando fluxo de salvamento com media_id: {media_id}")
        # Proteção contra salvamentos duplicados para o mesmo resultado
        if result_data is None:
            return
        if result_data.get('_saving_in_progress'):
            print('Serviço: Salvamento já em progresso para este resultado. Ignorando nova solicitação.')
            return
        if result_data.get('_saved'):
            print('Serviço: Resultado já salvo anteriormente. Ignorando solicitação.')
            return

        result_data['media_id'] = media_id
        result_data['_saving_in_progress'] = True
        self.last_confirmed_media_id = media_id

        auto_save = self.settings_service.user_settings.get('auto_save', False)
        save_image = self.settings_service.user_settings.get('save_image', False)

        # Se não for auto_save, mas for para salvar imagem, salve a imagem e armazene o caminho
        if not auto_save and save_image and not is_manual:
            print("Servico: Iniciando fluxo de salvamento de imagem (prévio ao manual).")
            image_path = self.save_image_to_disk(result_data['pixmap'])
            result_data['image_path'] = image_path
            # Não salva no banco ainda, só salva a imagem
            return

        if is_manual:
            print("Serviço: Iniciando fluxo de salvamento manual.")
            # Se já existe image_path, não salve a imagem de novo
            if 'image_path' in result_data and result_data['image_path']:
                print("Imagem já salva anteriormente, salvando apenas metadados.")
                self._run_save_capture_data_in_thread(result_data, result_data['image_path'])
            else:
                self._run_full_save_in_thread(result_data)
        else:
            if auto_save:
                print("Serviço: Iniciando fluxo de salvamento automático.")
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
            # Marca como salvo para evitar re-saves da mesma captura
            try:
                result['_saved'] = True
                result.pop('_saving_in_progress', None)
            except Exception:
                pass

            # Emite sinal para que a UI atualize (MainWindow irá adicionar à grid)
            try:
                self.capture_saved.emit(id)
            except Exception:
                pass
        
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
        return self.capture_repo.select_captures_ordered('DESC')

    def get_captures_ordered(self, order='DESC'):
        return self.capture_repo.select_captures_ordered(order)

    def get_captures_by_kanji(self, kanji, order='DESC'):
        return self.capture_repo.get_captures_by_kanji(kanji, order)
    
    def remove_capture(self, capture):
        self.capture_repo.delete_capture(capture['id'])
        image_path = capture['image_path']
        
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
        
    def find_by_id_capture(self, id):
        return self.capture_repo.select_capture_by_id(id)

    def update_capture_media(self, capture_id, media_id):
        """ Ponto de entrada do serviço para atualizar a mídia de uma captura. """
        self.capture_repo.update_media_id(capture_id, media_id)
        print(f"Mídia da captura {capture_id} atualizada para {media_id}")