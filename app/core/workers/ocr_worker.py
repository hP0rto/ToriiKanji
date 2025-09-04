from PyQt6.QtCore import QObject, pyqtSignal


class OcrWorker(QObject):
    finished = pyqtSignal(dict)  # resultado do OCR (dict com kanji e dados)
    error = pyqtSignal(str)

    def __init__(self, ocr_service, image):
        super().__init__()
        self.ocr_service = ocr_service
        self.image = image

    def run(self):
        try:
            result = self.ocr_service.extract_kanji(self.image)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
