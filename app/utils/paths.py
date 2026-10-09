"""
Centralized path definitions for ToriiKanji.
All file and directory paths used across the application are defined here.
"""
import os
import platform
import sys
from pathlib import Path


def resource_path(relative_path):
    """Return the absolute path to a resource, working in both dev and PyInstaller modes."""
    try:
        base_path = Path(sys._MEIPASS)
    except Exception:
        base_path = Path(__file__).resolve().parent.parent.parent
    
    return base_path / relative_path


APP_NAME = 'ToriiKanji'

if platform.system() == 'Windows':
    base_dir = os.path.join(os.getenv('APPDATA'), APP_NAME)
elif platform.system() == 'Linux':
    base_dir = os.path.join(os.path.expanduser('~/.config'), APP_NAME)
else:
    base_dir = os.path.join(os.path.expanduser('~'), '.' + APP_NAME.lower())

os.makedirs(base_dir, exist_ok=True)

# Persistent database path in user AppData/config
DB_PATH = os.path.join(base_dir, 'toriikanji.db')

ASSETS = resource_path('assets')
TESSERACT_PATH = resource_path('tesseract/tesseract.exe')


EXIT_ICON = ASSETS / 'exit_button.svg'
SETTINGS_ICON = ASSETS / 'setting_button.svg'
BACKGROUND_IMG = ASSETS / 'background.png'
BOOK_OPEN_ICON = ASSETS / 'book-open.svg'
TRENDING_UP_ICON = ASSETS / 'trending-up.svg'
TARGET_ICON = ASSETS / 'target.svg'
ICON = ASSETS / 'icon' / 'icon.ico'
NO_IMG = ASSETS / 'no_image.png'

# Bundled kanji dictionary used to seed the database on first run
KANJI_SEED_PATH = ASSETS / 'data' / 'kanji_dict.json.gz'



JSON_PATH = os.path.join(base_dir, 'usersettings.json')



