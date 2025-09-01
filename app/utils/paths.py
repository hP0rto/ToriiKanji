from pathlib import Path
import platform
import os, sys
'''
    Arquivo para centralizar acesso de caminhos no codigo
'''
BASE_DIR = Path(__file__).resolve().parent.parent  # volta para pasta /app
ASSETS = BASE_DIR.parent / 'assets'
TESSERACT_PATH = BASE_DIR.parent / 'tesseract' / 'tesseract.exe'


EXIT_ICON = ASSETS / 'exit_button.svg'
SETTINGS_ICON = ASSETS / 'setting_button.svg'
BACKGROUND_IMG = ASSETS / 'background.png'
ICON = ASSETS / 'icon' / 'icon.ico'

APP_NAME = 'ToriiKanji'

if platform.system() == 'Windows':
    base_dir = os.path.join(os.getenv('APPDATA'), APP_NAME)
elif platform.system() == 'Linux':
    base_dir = os.path.join(os.path.expanduser('~/.config'), APP_NAME)

# Cria o diretório caso não exista
os.makedirs(base_dir, exist_ok=True)

JSON_PATH = os.path.join(base_dir, 'usersettings.json')
