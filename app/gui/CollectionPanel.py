from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QGridLayout, QMessageBox, QHBoxLayout, QLabel, QComboBox, QSizePolicy
from PyQt6.QtCore import Qt


from gui.components.KanjiFrame import KanjiFrame
from gui.components.buttons_factory import create_text_button
from gui.components.HoverFrame import HoverFrame

from utils.helpers import run_in_thread

from core.services.media_service import MediaService
from core.workers.db_worker import DbWorker

class CollectionPanel(QWidget):
    COL_NUMBER_DEFAULT = 3
    
    def __init__(self, main_window, capture_service, media_service, kanji_service):
        super().__init__()
        self.threads = []
        self.workers = []
        self.main_window = main_window
        
        self._initial_load_started = False
        # track latest load request to ignore stale worker results
        self._latest_load_request = 0
        self._current_request_id = None
        
        self.capture_service = capture_service
        self.media_service = media_service
        self.kanji_service = kanji_service

        layout = QVBoxLayout(self) 
        
        delete_button = create_text_button('Delete selected', self.delete_selected_captures)
       
        self._current_filter = None
        # Sort controls row
        sort_row = QWidget()
        sort_layout = QHBoxLayout(sort_row)
        sort_layout.setContentsMargins(0,0,0,0)
        
        sort_layout.addWidget(QLabel('Sort:'))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(['Most recent', 'Oldest'])
        self.sort_combo.currentIndexChanged.connect(self.on_sort_changed)
        sort_layout.addWidget(self.sort_combo)
        
        sort_layout.addWidget(QLabel('Type:'))
        self.type_combo = QComboBox()
        self.type_combo.addItems(['Captures', 'Kanji'])
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        sort_layout.addWidget(self.type_combo)

        sort_layout.addWidget(QLabel('Media:'))
        self.media_combo = QComboBox()
        try:
            medias = self.media_service.get_all_media()
        except Exception:
            medias = []
        self.media_combo.addItem('All', None)
        self.media_combo.addItem('N/A', -1)
        for m in medias:
            self.media_combo.addItem(m['title'], m['id'])   
        self.media_combo.currentIndexChanged.connect(self.on_media_changed)
        sort_layout.addWidget(self.media_combo)
        screen_width = self.main_window.width() / 0.3
        if screen_width < 2000:
            # Smaller screens: compact controls
            label_font_size = "font-size: 11px;"
            combo_min_width = 80
            button_min_width = 60
        else:
            # Larger screens: normal controls
            label_font_size = ""
            combo_min_width = 100
            button_min_width = 80

        # Apply responsive styling to labels and combos
        for i in range(sort_layout.count()):
            item = sort_layout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, QLabel):
                widget.setStyleSheet(f"QLabel {{ {label_font_size} }}")
            elif isinstance(widget, QComboBox):
                widget.setMinimumWidth(combo_min_width)
                widget.setStyleSheet(f"QComboBox {{ {label_font_size} }}")

        # Responsive button styling based on screen width
        if screen_width < 2000:
            # Smaller screens: compact buttons
            style_sheet = f"""
                QPushButton {{
                    background-color: #2c2c2c;
                    color: white;
                    border: 1px solid #555;
                    padding: 2px 8px;
                    border-radius: 6px;
                    {label_font_size}
                    min-width: {button_min_width}px;
                }}
                QPushButton:hover {{
                    background-color: #3c3c3c;
                }}
                QComboBox {{
                    padding: 2px;
                    {label_font_size}
                }}
            """
        else:
            # Larger screens: normal buttons
            style_sheet = f"""
                QPushButton {{
                    background-color: #2c2c2c;
                    color: white;
                    border: 1px solid #555;
                    padding: 3px 16px;
                    border-radius: 8px;
                    min-width: {button_min_width}px;
                }}
                QPushButton:hover {{
                    background-color: #3c3c3c;
                }}
            """
        
        refresh_button = create_text_button('Refresh', self.load_captures, style_sheet)
        refresh_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        # Listen for media changes to refresh combo
        try:
            if hasattr(self.media_service, 'media_changed'):
                self.media_service.media_changed.connect(self.refresh_media_combo)
        except Exception:
            pass

        
        sort_layout.addStretch()
        sort_layout.addWidget(refresh_button, 1)
        
        layout.addWidget(sort_row)
        
        layout.addWidget(delete_button)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        container = QWidget()
        
        self.grid = QGridLayout(container)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        # Responsive: set column stretch so grid is always centered
        for col in range(self.COL_NUMBER_DEFAULT):
            self.grid.setColumnStretch(col, 1)
        
        scroll_area.setWidget(container)
        
        layout.addWidget(scroll_area)
        
        self.setLayout(layout)
        
        self._current_col_number = self.COL_NUMBER_DEFAULT
        
        self.show()
        
    def get_col_number(self):
        # Responsive column count based on screen width (main window is 30% of screen)
        screen_width = self.main_window.width() / 0.3
        if screen_width < 2000:  # Smaller screens: 2 columns
            return 2
        else:  # Larger screens: 3 columns
            return 3
        
    def showEvent(self, event):
        '''
            Fill list in show event to prevent race condition in __init__ :)
        '''
        super().showEvent(event) 
        
        if not self._initial_load_started:
            self._initial_load_started = True
            
            self.load_captures()
            
    def on_kanji_selected(self, kanji_char):
        if kanji_char:
            self._current_filter = kanji_char
        else:
            self._current_filter = None
        self.type_combo.setCurrentIndex(0)
    
    def on_capture_clicked(self, capture):
        print(capture)
        self.main_window.custom_tab.show_capture(capture)
        
    def on_kanji_clicked(self, kanji):
        print(kanji)
        self.on_kanji_selected(kanji['kanji'])
        
    def fill_list(self, result, type=None):
        # If a new load request started after this worker was launched, ignore these results
        # (workers capture the request id via closure when invoked)
        request_id = getattr(self, '_current_request_id', None)
        if request_id is not None and request_id != self._latest_load_request:
            # stale result, ignore
            return

        # Populate the grid. Clear existing items first to avoid mixing types.
        self.clear_grid()

        if type == 0:
            for index, capture in enumerate(result):
                row, col = self.get_row_and_col(index)

                frame = HoverFrame(capture, self.media_service)
                frame.clicked.connect(self.on_capture_clicked)
                
                self.grid.addWidget(frame, row, col)
        elif type == 1:
            for index, kanji in enumerate(result):
                row, col = self.get_row_and_col(index)

                frame = KanjiFrame(kanji)
                frame.clicked.connect(self.on_kanji_clicked)
                
                self.grid.addWidget(frame, row, col)
        

    def clear_grid(self):
        """Remove and delete all widgets from the grid layout."""
        # iterate and remove widgets safely
        widgets = []
        for i in range(self.grid.count()):
            item = self.grid.itemAt(i)
            widget = item.widget()
            if widget:
                widgets.append(widget)

        for widget in widgets:
            self.grid.removeWidget(widget)
            widget.setParent(None)
            try:
                widget.deleteLater()
            except Exception:
                pass
    
    def delete_selected_captures(self):
        type = self.type_combo.currentIndex()
        
        if type == 0:
            selected_frames = [
                self.grid.itemAt(i).widget()
                for i in range(self.grid.count())
                if hasattr(self.grid.itemAt(i).widget(), "selected") and self.grid.itemAt(i).widget().selected
            ]

            from utils.i18n import t
            if not selected_frames:
                QMessageBox.information(self, t('delete_selected'), t('no_capture_selected'))
                return

            confirm = QMessageBox.question(
                self,
                t('confirm_removal_title'),
                f"Delete {len(selected_frames)} capture(s)?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if confirm == QMessageBox.StandardButton.Yes:
                for frame in selected_frames:
                    self.capture_service.remove_capture(frame.capture)

                    self.grid.removeWidget(frame)
                    frame.deleteLater()

                self.reorganize_grid()
        elif type == 1:
             selected_frames = [
                self.grid.itemAt(i).widget()
                for i in range(self.grid.count())
                if hasattr(self.grid.itemAt(i).widget(), "selected") and self.grid.itemAt(i).widget().selected
             ]
             if not selected_frames:
                 QMessageBox.information(self, "Delete", "No kanji selected")
                 return
            
             confirm = QMessageBox.question(
                self,
                "Confirm",
                f"Delete all captures for {len(selected_frames)} kanji(s)?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
             )
             if confirm == QMessageBox.StandardButton.Yes:
                 for frame in selected_frames:
                     kanji_char = frame.kanji.get('kanji')
                     self.capture_service.remove_captures_by_kanji(kanji_char)
                 self.load_captures()
    
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

        # Update column stretches for responsive design
        col_count = self.get_col_number()
        for col in range(col_count):
            self.grid.setColumnStretch(col, 1)

        # Reposicionar cada widget no grid
        for index, widget in enumerate(widgets):
            row, col = self.get_row_and_col(index)
            self.grid.addWidget(widget, row, col)
        
    def get_row_and_col(self, index):
        row = index // self.get_col_number()
        col = index % self.get_col_number()
        
        return (row, col)
    def resizeEvent(self, event):
        super().resizeEvent(event)
        new_col_number = self.get_col_number()
        if new_col_number != self._current_col_number:
            self._current_col_number = new_col_number
            self.reorganize_grid()
        grid_width = self.width() * 0.92  # leave some margin
        item_width = int(grid_width / self.get_col_number()) - 12  # 12px for spacing
        item_height = int(item_width * 1.15)  # aspect ratio
        for i in range(self.grid.count()):
            item = self.grid.itemAt(i)
            widget = item.widget()
            if widget:
                widget.setMinimumWidth(item_width)
                widget.setMaximumWidth(item_width)
                widget.setMinimumHeight(item_height)
                widget.setMaximumHeight(item_height)
    
    def on_sort_changed(self, idx):
        # reload with new order
        self.load_captures()
        
    def on_type_changed(self, idx):
        self.load_captures()

    def on_media_changed(self, idx):
        # reload with new media filter
        self.load_captures()

    def refresh_media_combo(self):
        """Reload medias into the combo while preserving the current selection if possible."""
        try:
            self.media_combo.blockSignals(True)
            self.media_combo.clear()
            self.media_combo.addItem('All', None)
            self.media_combo.addItem('N/A', -1)
            
            try:
                medias = self.media_service.get_all_media()
            except Exception:
                medias = []

            for m in medias:
                self.media_combo.addItem(m['title'], m['id'])

            self.media_combo.setCurrentIndex(0)
        except Exception:
            pass
        finally:
            try:
                self.media_combo.blockSignals(False)
            except Exception:
                pass

    def load_captures(self):
        order = 'DESC' if self.sort_combo.currentIndex() == 0 else 'ASC'
        type = self.type_combo.currentIndex()
        # determine selected media id (None means all)
        media_id = self.media_combo.currentData()
        print(f'load_capture: {order}, {type}')

        # increment request counter and attach to this load so late workers are ignored
        self._latest_load_request += 1
        self._current_request_id = self._latest_load_request

        # clear grid immediately to avoid visual mixing while workers run
        self.clear_grid()

        if type == 0:
            # Captures view
            if media_id is not None:
                # filter captures by media
                worker = DbWorker(self.capture_service, 'get_captures_by_media', media_id, order)
            elif self._current_filter:
                worker = DbWorker(self.capture_service, 'get_captures_by_kanji', self._current_filter, order)
            else:
                worker = DbWorker(self.capture_service, 'get_captures_ordered', order)
        else:
            # Kanji view
            if media_id is not None:
                worker = DbWorker(self.kanji_service, 'get_all_user_kanji_with_count_by_media', media_id, order)
            else:
                worker = DbWorker(self.kanji_service, 'get_all_user_kanji_with_count', order)

        # reset the transient filter after creating the worker
        self._current_filter = None

        # capture the request id in the callback closure so fill_list can detect staleness
        request_id = self._current_request_id
        thread = run_in_thread(
            worker,
            on_finished=lambda result, _req=request_id, _type=type: (setattr(self, '_current_request_id', _req), self.fill_list(result, _type)),
            on_error=lambda msg: print('Error:', msg)
        )
        self.threads.append(thread)
        self.workers.append(worker)
