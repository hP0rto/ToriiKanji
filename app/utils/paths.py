from pathlib import Path
import os
'''
    Arquivo para centralizar acesso de caminhos no codigo
'''


BASE_DIR = Path(__file__).resolve().parent.parent  # volta para pasta /app
ASSETS = BASE_DIR.parent / 'assets'

EXIT_ICON = ASSETS / 'exit_button.svg'
SETTINGS_ICON = ASSETS / 'setting_button.svg'


APP_DATA = os.getenv('APPDATA')
JSON_PATH = os.path.join(APP_DATA, 'ToriiKanji\\usersettings.json')