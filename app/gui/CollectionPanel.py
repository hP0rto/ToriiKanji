from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QGridLayout, QMessageBox
from PyQt6.QtCore import Qt


from gui.components.buttons_factory import create_text_button
from gui.components.HoverFrame import HoverFrame

from utils.helpers import run_in_thread

from core.services.media_service import MediaService
from core.workers.db_worker import DbWorker

class CollectionPanel(QWidget):
    COL_NUMBER = 3
    
    def __init__(self, main_window, capture_service, media_service):
        super().__init__()
        self.threads = []
        self.workers = []
        self.main_window = main_window
        
        self._initial_load_started = False
        
        self.capture_service = capture_service
        self.media_service = media_service

        layout = QVBoxLayout(self) 
        
        delete_button = create_text_button('Delete selected', self.delete_selected_captures)
        layout.addWidget(delete_button)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        container = QWidget()
        
        self.grid = QGridLayout(container)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignVCenter)

        
        scroll_area.setWidget(container)
        
        layout.addWidget(scroll_area)
        
        self.setLayout(layout)
        self.show()
        
    def showEvent(self, event):
        '''
            Fill list in show event to prevent race condition in __init__ :)
        '''
        super().showEvent(event) 
        
        if not self._initial_load_started:
            self._initial_load_started = True
            
            initial_worker = DbWorker(
                self.capture_service,
                'get_captures'
            )

            thread = run_in_thread( initial_worker, on_finished=self.fill_list, on_error=lambda msg: print('Error:', msg))
            
            self.threads.append(thread)
            self.workers.append(initial_worker)
    
    def on_capture_clicked(self, capture):
        print(capture)
        self.main_window.custom_tab.show_capture(capture)
        
    def fill_list(self, result):
        for index, capture in enumerate(result):
            row, col = self.get_row_and_col(index)

            frame = HoverFrame(capture, self.media_service)
            frame.clicked.connect(self.on_capture_clicked)
            
            self.grid.addWidget(frame, row, col)
        
        
    def add_capture_to_grid(self, capture_id):
        capture = self.capture_service.find_by_id_capture(capture_id)

        row, col  = self.get_row_and_col(self.grid.count())

        frame = HoverFrame(capture, self.media_service)
        frame.clicked.connect(self.on_capture_clicked)
        
        self.grid.addWidget(frame, row, col)
    
    def delete_selected_captures(self):
        selected_frames = [
            self.grid.itemAt(i).widget()
            for i in range(self.grid.count())
            if hasattr(self.grid.itemAt(i).widget(), "selected") and self.grid.itemAt(i).widget().selected
        ]

        if not selected_frames:
            QMessageBox.information(self, "Delete", "Nenhuma captura selecionada.")
            return

        confirm = QMessageBox.question(
            self,
            "Confirmar exclusão",
            f"Excluir {len(selected_frames)} captura(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            for frame in selected_frames:
                self.capture_service.remove_capture(frame.capture)

                self.grid.removeWidget(frame)
                frame.deleteLater()

            self.reorganize_grid()
    
    def reorganize_grid(self):
        # Guardar todos os widgets atuais numa lista
        widgets = []
        for i in range(self.grid.count()):
            item = self.grid.itemAt(i)
            widget = item.widget()
            if widget:
                widgets.append(widget)

        # Limpar o grid completamente
        for i in reversed(range(self.grid.count())):
            item = self.grid.itemAt(i)
            widget = item.widget()
            if widget:
                self.grid.removeWidget(widget)

        # Reordenar de acordo com o ID da captura (ascendente)
        widgets.sort(key=lambda w: w.capture["id"])

        # Reposicionar cada widget no grid
        for index, widget in enumerate(widgets):
            row, col = self.get_row_and_col(index)
            self.grid.addWidget(widget, row, col)
        
    def get_row_and_col(self, index):
        row = index // self.COL_NUMBER
        col = index % self.COL_NUMBER
        
        return (row, col)