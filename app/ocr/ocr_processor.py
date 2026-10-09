"""
Tesseract OCR wrapper for ToriiKanji.
Locates a Tesseract executable and the Japanese language data.
"""

import os
import shutil
from pathlib import Path

import pytesseract
from PIL import Image

from utils.paths import TESSERACT_PATH

# Common install locations checked when Tesseract is not on PATH
_COMMON_TESSERACT_LOCATIONS = [
    Path(os.environ.get('ProgramFiles', r'C:\Program Files')) / 'Tesseract-OCR' / 'tesseract.exe',
    Path(os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)')) / 'Tesseract-OCR' / 'tesseract.exe',
    Path(os.environ.get('LOCALAPPDATA', '')) / 'Programs' / 'Tesseract-OCR' / 'tesseract.exe',
    Path('/usr/bin/tesseract'),
    Path('/usr/local/bin/tesseract'),
    Path('/opt/homebrew/bin/tesseract'),
]


class TesseractNotFoundError(RuntimeError):
    """Raised when no Tesseract executable can be located."""


def find_tesseract():
    """Return the path to a Tesseract executable, or None if not found.

    Search order: embedded copy → system PATH → common install locations.
    """
    if TESSERACT_PATH.is_file():
        return TESSERACT_PATH

    on_path = shutil.which('tesseract')
    if on_path:
        return Path(on_path)

    for candidate in _COMMON_TESSERACT_LOCATIONS:
        if candidate.is_file():
            return candidate

    return None


def find_tessdata(lang, tesseract_exe):
    """Return a tessdata directory that contains `<lang>.traineddata`, or None.

    Prefers the embedded tessdata (shipped with the app), then the one next to
    the Tesseract executable. Returning None lets Tesseract use its default.
    """
    candidates = [TESSERACT_PATH.parent / 'tessdata']
    if tesseract_exe is not None:
        candidates.append(tesseract_exe.parent / 'tessdata')

    for directory in candidates:
        if (directory / f'{lang}.traineddata').is_file():
            return directory
    return None


class OcrProcessor:
    def __init__(self, lang="jpn"):
        self.lang = lang
        self.file_name = ""
        self._configure_tesseract()

    def _configure_tesseract(self):
        tesseract_exe = find_tesseract()
        if tesseract_exe is None:
            raise TesseractNotFoundError(
                "Tesseract OCR was not found. Install it (e.g. from "
                "https://github.com/UB-Mannheim/tesseract/wiki) or place a portable "
                f"copy at: {TESSERACT_PATH}"
            )

        pytesseract.pytesseract.tesseract_cmd = str(tesseract_exe)
        print(f'Using tesseract: {tesseract_exe}')

        self.config = '--oem 3 --psm 6'
        tessdata_dir = find_tessdata(self.lang, tesseract_exe)
        if tessdata_dir is not None:
            # Use the env var rather than --tessdata-dir: pytesseract passes quotes
            # literally on Windows, which breaks paths (especially ones with spaces).
            os.environ['TESSDATA_PREFIX'] = str(tessdata_dir)
        else:
            print(f'Warning: {self.lang}.traineddata not found; relying on Tesseract defaults.')

    def extract_text(self, image: Image.Image) -> str:
        return pytesseract.image_to_string(image, lang=self.lang, config=self.config)

    def extract_data(self, image: Image.Image):
        return pytesseract.image_to_data(image, lang=self.lang, config=self.config, output_type=pytesseract.Output.DICT)
