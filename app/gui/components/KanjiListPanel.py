from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel
from PyQt6.QtCore import pyqtSignal

from db.repositories.kanji_repository import KanjiRepository

class KanjiListPanel(QWidget):
    kanji_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.repo = KanjiRepository()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Kanjis"))
        self.list = QListWidget()
        layout.addWidget(self.list)
        self.list.itemClicked.connect(self._on_item_clicked)
        self.refresh()

    def refresh(self, limit=200, order_by='count'):
        self.list.clear()
        rows = self.repo.list_kanjis_with_counts(limit=limit, order_by=order_by)
        for row in rows:
            kanji = row['kanji']
            cnt = row.get('cnt', 0)
            jlpt = row.get('jlpt')
            strokes = row.get('strokes')
            label = f"{kanji} ({cnt})"
            if jlpt:
                label += f"  JLPT:N{jlpt}"
            if strokes:
                label += f"  ⤷ {strokes} strokes"
            self.list.addItem(label)

    def _on_item_clicked(self, item):
        kanji = item.text().split()[0]
        self.kanji_selected.emit(kanji)
