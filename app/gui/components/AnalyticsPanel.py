from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget
from db.repositories.kanji_repository import KanjiRepository
from db.repositories.capture_repository import CaptureRepository

class AnalyticsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.kanji_repo = KanjiRepository()
        self.capture_repo = CaptureRepository()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('Analytics'))
        self.summary_label = QLabel('')
        layout.addWidget(self.summary_label)
        self.top_list = QListWidget()
        layout.addWidget(self.top_list)
        self.refresh()

    def refresh(self, top_n=10):
        # Total unique kanjis and total captures
        rows = self.kanji_repo.list_kanjis_with_counts(limit=100000, order_by='count')
        total_kanjis = len([r for r in rows if r.get('cnt', 0) > 0])
        total_occurrences = sum(r.get('cnt', 0) for r in rows)
        self.summary_label.setText(f'Unique kanjis in captures: {total_kanjis}\nTotal kanji occurrences: {total_occurrences}')
        self.top_list.clear()
        for r in rows[:top_n]:
            self.top_list.addItem(f"{r['kanji']} — {r.get('cnt',0)} occurrences — JLPT:{r.get('jlpt')} — {r.get('strokes')} strokes")
