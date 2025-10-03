from pathlib import Path
import platform
import os, sys
'''
    Arquivo para centralizar acesso de caminhos no codigo
'''
def resource_path(relative_path):
    """ Retorna o caminho absoluto para o recurso, funcionando tanto no dev quanto no PyInstaller """
    try:
        base_path = Path(sys._MEIPASS)
    except Exception:
        base_path = Path(__file__).resolve().parent.parent.parent
    
    return base_path / relative_path


DB_PATH = resource_path('database/toriikanji.db')
ASSETS = resource_path('assets')
TESSERACT_PATH = resource_path('tesseract/tesseract.exe')


EXIT_ICON = ASSETS / 'exit_button.svg'
SETTINGS_ICON = ASSETS / 'setting_button.svg'
BACKGROUND_IMG = ASSETS / 'background.png'
ICON = ASSETS / 'icon' / 'icon.ico'
NO_IMG = ASSETS / 'no_image.png'

APP_NAME = 'ToriiKanji'

if platform.system() == 'Windows':
    base_dir = os.path.join(os.getenv('APPDATA'), APP_NAME)
elif platform.system() == 'Linux':
    base_dir = os.path.join(os.path.expanduser('~/.config'), APP_NAME)

# Cria o diretório caso não exista
os.makedirs(base_dir, exist_ok=True)

JSON_PATH = os.path.join(base_dir, 'usersettings.json')
