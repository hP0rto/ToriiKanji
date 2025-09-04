from PyQt6.QtWidgets import * 
from PyQt6.QtGui import *
from PyQt6.QtCore import *


class OverlayPanel(QWidget):

    def __init__(self, main_window):
        super().__init__()
            
        self.main_window = main_window # dependency injection 👍    
        
        select = QComboBox()
        select.addItems(["Opção 1", "Opção 2", "Opção 3"])
        
        # create layouts
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    

        
        # sets widget and layouts
        layout.addWidget(select)
        
        self.setLayout(layout)
        
        
        self.capture_label = QLabel("No capture made")
        self.capture_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.capture_label.resize(400,400)

        
        
        self.text_label = QLabel("")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setStyleSheet('font-size: 40px')
        
        self.kanji_result = QTextEdit()
        self.kanji_result.setReadOnly(True)  # impede edição
        self.kanji_result.setStyleSheet("font-size: 13px; padding: 6px;")
        
        layout.addWidget(self.capture_label)
        layout.addWidget(self.text_label)
        layout.addWidget(self.kanji_result)
        
        # show panel
        self.show()
        
    def show_capture(self, result):
        """Exibe a captura no painel"""
        original_pixmap = result.get('pixmap')

        
        self.capture_label.setPixmap(original_pixmap.scaled(
            400, 400,  # tamanho máximo de preview
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
        
        
        self.text_label.setText(result.get('raw_text'))
        
        self.exibir_resultado(result.get('kanjis'))
        
        

    def exibir_resultado(self, result_dict):
        content = ''
        for row in result_dict:
            content += f"""
            <b>Kanji:</b> {row["kanji"]}<br>
            <b>Onyomi:</b> {row["onyomi"]}<br>
            <b>Kunyomi:</b> {row["kunyomi"]}<br>
            <b>Meaning:</b> {row["meaning"]}<br>
            <b>Grade:</b> {row["grade"]}<br>
            <b>JLPT:</b> N{row["jlpt"] if row["jlpt"] else "-"}
            <hr>
            """
        # for row in result_dict:
        #     content += f"""
        #     <b>Kanji:</b> {row}<br>
        #     <hr>
        #     """
        self.kanji_result.setHtml(content)
        