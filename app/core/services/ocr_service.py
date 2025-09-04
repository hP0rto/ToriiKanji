from ocr.ocr_processor import OcrProcessor
from utils.paths import TESSERACT_PATH
from utils.converters import pil_to_qpixmap

class OcrService:
    def extract_kanji(self, pil_image) -> dict:
        ocr_processor = OcrProcessor()
        
        text = ocr_processor.extract_text(pil_image)

        pixmap = pil_to_qpixmap(pil_image)
        kanjis = [char for char in text if '\u4e00' <= char <= '\u9faf']
        
        
        return {"raw_text": text, "kanjis": kanjis, "pixmap": pixmap}
