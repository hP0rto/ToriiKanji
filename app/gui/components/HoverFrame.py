from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout
from PyQt6.QtCore import   QVariantAnimation, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPalette, QPixmap

from utils.helpers import pixmap_null_handler

from datetime import datetime

class HoverFrame(QFrame):
    clicked = pyqtSignal(object)
    
    def __init__(self,capture, media_service):
        super().__init__()
        self.setFixedSize(150, 180)
        self.setAutoFillBackground(True)
        self.capture = capture
        # cores
        self.normal_color = QColor("#3C3C3C")
        self.hover_color = QColor("#C24338")
        
        self.selected = False
        
        self.media_service = media_service

        # paleta inicial
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, self.normal_color)
        self.setPalette(pal)

        # label de teste
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        pixmap = pixmap_null_handler(QPixmap(capture['image_path']))
        pixmap = pixmap.scaled(
            130, 
            130, 
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        img_label = QLabel()
        img_label.setPixmap(pixmap)
        img_label.setFixedSize(130, 130)
        
        dt = datetime.fromisoformat(capture['timestamp'])  
        formatted = dt.strftime("%d/%m/%Y %H:%M:%S")
        
        layout.addWidget(img_label)
        layout.addWidget(QLabel(f"ID: {capture['id']}\n{formatted}"))
        
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
            media = self.media_service.get_media_by_id(self.capture['media_id'])
            if media:
                self.capture['media_name'] = media['title']
            self.clicked.emit(self.capture)
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

        super().enterEvent(event)

    def leaveEvent(self, event):
        if self._base_geometry is None:
            return

        self.color_anim.stop()
        self.color_anim.setStartValue(self.hover_color)
        self.color_anim.setEndValue(self.normal_color)
        self.color_anim.start()

        super().leaveEvent(event)
