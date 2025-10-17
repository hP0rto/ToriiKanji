from PyQt6.QtWidgets import QSizePolicy, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class KanjiCard(QFrame):
    def __init__(self, kanji, kunyomi, onyomi, meaning, jlpt, strokes=None, parent=None):
        super().__init__(parent)

        self.setObjectName("kanjiCard")
        self.setStyleSheet("""
            QFrame#kanjiCard {
                background-color: #2b2b2b;
                border-radius: 8px;
                padding: 10px;
            }
            QLabel {
                color: white;
            }
            QLabel[role="title"] {
                color: #aaa;
                font-size: 12px;
            }
            QLabel[role="kanji"] {
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        # Quadrado do kanji
        kanji_box = QLabel(kanji)
        kanji_box.setFixedSize(60, 60)
        kanji_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        kanji_box.setStyleSheet("""
            QLabel {
                background-color: #C24338;
                color: white;
                font-size: 28px;
                font-weight: bold;
                border-radius: 6px;
                margin-right: 10px;
            }
        """)
        layout.addWidget(kanji_box)

        # Infos ao lado
        info_layout = QVBoxLayout()

        kunyomi_label = QLabel("Kunyomi")
        kunyomi_label.setProperty("role", "title")
        kunyomi_value = QLabel(kunyomi)

        onyomi_label = QLabel("Onyomi")
        onyomi_label.setProperty("role", "title")
        onyomi_value = QLabel(onyomi)

        meaning_label = QLabel("Meaning")
        meaning_label.setProperty("role", "title")
        meaning_value = QLabel(meaning)

        # Strokes (optional)
        strokes_label = QLabel("Strokes")
        strokes_label.setProperty("role", "title")
        strokes_value = QLabel(str(strokes) if strokes is not None else "—")

        jlpt_label = QLabel("JLPT Level")
        jlpt_label.setProperty("role", "title")
        jlpt_value = QLabel(f'N{jlpt}' if jlpt is not None else "—")
        jlpt_value.setStyleSheet('''
                QLabel {
                    background-color: #C24338;
                    color: white;
                    border-radius: 6px;
                    padding: 10px;
                }
        ''')

        info_layout.addWidget(kunyomi_label)
        info_layout.addWidget(kunyomi_value)
        info_layout.addWidget(onyomi_label)
        info_layout.addWidget(onyomi_value)
        info_layout.addWidget(meaning_label)
        info_layout.addWidget(meaning_value)
        info_layout.addWidget(strokes_label)
        info_layout.addWidget(strokes_value)
        if jlpt:
            info_layout.addWidget(jlpt_label)
            info_layout.addWidget(jlpt_value)

        layout.addLayout(info_layout)