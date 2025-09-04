import pytesseract
import shutil

from utils.paths import TESSERACT_PATH

from PIL import Image

class OcrProcessor:
    def __init__(self, lang="jpn"):
        self.lang = lang
        self._configure_tesseract()
        self.file_name = ""

    def _configure_tesseract(self):
        path_in_system = shutil.which("tesseract")
        if path_in_system:
            pytesseract.pytesseract.tesseract_cmd = path_in_system
            print(f'Find tesseract: {path_in_system}')
        else:
            pytesseract.pytesseract.tesseract_cmd = str(TESSERACT_PATH)
            print(f'Find tesseract: {str(TESSERACT_PATH)}')
        
        # Config extra para usar tessdata embutido
        self.config = f'--oem 3 --psm 6'

    def extract_text(self, image: Image.Image) -> str:
        return pytesseract.image_to_string(image, lang=self.lang, config=self.config)
         

    def extract_data(self, image: Image.Image):
        return pytesseract.image_to_data(image, lang=self.lang, config=self.config, output_type=pytesseract.Output.DICT)