from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout
from PyQt6.QtCore import   QVariantAnimation, Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QPalette


class KanjiFrame(QFrame):
    clicked = pyqtSignal(object)
    
    def __init__(self,kanji):
        super().__init__()
        self.setFixedSize(150, 180)
        self.setAutoFillBackground(True)
        self.kanji = kanji
        # cores
        self.normal_color = QColor("#3C3C3C")
        self.hover_color = QColor("#C24338")
        
        self.selected = False

        self._balloon = None  # Balloon widget for KanjiCard

        self._balloon_timer = None  # QTimer for delayed balloon

        # paleta inicial
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, self.normal_color)
        self.setPalette(pal)


        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        kanji_box = QLabel(kanji['kanji'])
        kanji_box.setFixedSize(60, 60)
        kanji_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        kanji_box.setStyleSheet("""
            QLabel {
                background-color: #C24338;
                color: white;
                font-size: 50px;
                font-weight: bold;
                border-radius: 6px;
                margin-right: 10px;
            }
        """)
        layout.addWidget(kanji_box)
    
        capture = f'{kanji['cnt']} Captures' if kanji['cnt'] > 1 else f'1 Capture'
    
        layout.addWidget(QLabel(capture))
        
        self.setLayout(layout)


        # animação de cor
        self.color_anim = QVariantAnimation()
        self.color_anim.setDuration(200)
        self.color_anim.valueChanged.connect(self.update_color)
        
        self._base_geometry = None  
    
    def mousePressEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.toggle_selection()
        else:
            self.clicked.emit(self.kanji)
        super().mousePressEvent(event)
    
    
    def toggle_selection(self):
        self.selected = not self.selected
        if self.selected:
            self.setStyleSheet("background-color: #C24338;")  # azul, por exemplo
        else:
            self.setStyleSheet("")
            
    def showEvent(self, event):
        # garante que a geometry base só é salva quando o widget for exibido
        if self._base_geometry is None:
            self._base_geometry = self.geometry()
        super().showEvent(event)

    def update_color(self, color):
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, color)
        self.setPalette(pal)

    def enterEvent(self, event):
        if self._base_geometry is None:
            return

        self.color_anim.stop()
        self.color_anim.setStartValue(self.normal_color)
        self.color_anim.setEndValue(self.hover_color)
        self.color_anim.start()

        
        if self._balloon_timer is not None:
            self._balloon_timer.stop()
            self._balloon_timer.deleteLater()
        self._balloon_timer = QTimer(self)
        self._balloon_timer.setSingleShot(True)
        self._balloon_timer.timeout.connect(self._show_balloon)
        self._balloon_timer.start(2000)

        super().enterEvent(event)

    def _show_balloon(self):
        if self._balloon is not None:
            return
        from gui.components.KanjiCard import KanjiCard
        # Truncate long texts for balloon
        def elide(text, maxlen=32):
            if text and len(text) > maxlen:
                return text[:maxlen-3] + '...'
            return text

        card = KanjiCard(
            kanji=self.kanji.get('kanji', ''),
            kunyomi=elide(self.kanji.get('kunyomi', ''), 24),
            onyomi=elide(self.kanji.get('onyomi', ''), 24),
            meaning=elide(self.kanji.get('meaning', ''), 32),
            jlpt=None,
            strokes=None
        )
        card.setWindowFlags(Qt.WindowType.ToolTip)
        card.setFixedSize(300, 170)
        # Add a soft rounded border for the balloon only
        card.setStyleSheet(card.styleSheet() + "\nQFrame#kanjiCard { border: 2px solid #555; background-color: #2b2b2b; }")
        # Apply a rounded mask to the card (balloon) only
        from PyQt6.QtGui import QPainterPath, QRegion
        from PyQt6.QtCore import QRectF
        path = QPainterPath()
        rect = QRectF(0, 0, card.width(), card.height())
        path.addRoundedRect(rect, 8, 8)
        region = QRegion(path.toFillPolygon().toPolygon())
        card.setMask(region)
        # Enable word wrap for value labels
        for child in card.findChildren(QLabel):
            if child.property("role") is None:
                child.setWordWrap(True)
        self._balloon = card
        # Always show below, centered horizontally to KanjiFrame
        below_pos = self.mapToGlobal(self.rect().bottomLeft())
        center_x = below_pos.x() + (self.width() // 2) - (card.width() // 2)
        self._balloon.move(center_x, below_pos.y() + 10)
        self._balloon.show()

    def leaveEvent(self, event):
        if self._base_geometry is None:
            return

        self.color_anim.stop()
        self.color_anim.setStartValue(self.hover_color)
        self.color_anim.setEndValue(self.normal_color)
        self.color_anim.start()

        # Cancel balloon timer if running
        if self._balloon_timer is not None:
            self._balloon_timer.stop()
            self._balloon_timer.deleteLater()
            self._balloon_timer = None

        # Hide and delete balloon
        if self._balloon is not None:
            self._balloon.hide()
            self._balloon.deleteLater()
            self._balloon = None

        super().leaveEvent(event)
