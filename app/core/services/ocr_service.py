"""
OCR service for ToriiKanji.
Orchestrates OCR processing and kanji extraction.
"""

from core.services.setting_services import SettingsService
from ocr.ocr_processor import OcrProcessor
from ocr.preprocessor import preprocess
from utils.converters import pil_to_qpixmap


class OcrService:
    """Extracts text and kanji characters from images using Tesseract OCR."""

    def extract_kanji(self, pil_image) -> dict:
        """
        Process an image through OCR and extract kanji characters.

        Args:
            pil_image: PIL Image to process

        Returns:
            dict with 'raw_text', 'kanjis' (list of kanji chars), and 'pixmap' (QPixmap)
        """
        settings = SettingsService()
        enable_preprocessing = settings.get('ocr_preprocessing', True)

        # Keep original for display
        pixmap = pil_to_qpixmap(pil_image)

        # Pre-process for better OCR accuracy
        processed_image = preprocess(pil_image, enable=enable_preprocessing)

        ocr_processor = OcrProcessor()
        text = ocr_processor.extract_text(processed_image)

        # Extract CJK Unified Ideographs (kanji range)
        kanjis = [char for char in text if '\u4e00' <= char <= '\u9faf']

        return {"raw_text": text, "kanjis": kanjis, "pixmap": pixmap}
