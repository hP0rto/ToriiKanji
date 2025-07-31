import os
import json
from threading import Lock
from utils.paths import JSON_PATH

class SingletonMeta(type):
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args,**kwargs)
                cls._instances[cls] = instance
            return cls._instances[cls]

class SettingsService(metaclass=SingletonMeta):
    # Singleton
    def __init__(self):
        self.user_settings = {
                'exit_key': 'f4',
                'capture_key': 'f9',
                'toggle_key': 'f10'
        }

        if not os.path.exists(JSON_PATH):
            with open(JSON_PATH, 'w') as file:
                json.dump(self.user_settings, file, indent=4)

                
        self.set_settings()
    
    def edit_settings_file(self, action, key):
        '''Edits the .json file'''
        
        self.user_settings[action] = key

        with open(JSON_PATH, 'w') as file:
                json.dump(self.user_settings, file, indent=4)
        
        self.set_settings()

    def set_settings(self):
        '''Sets class atributes to match .json'''
        try:
            with open(JSON_PATH, 'r') as file:
                json_user_settings = json.load(file)
            
            self.user_settings['exit_key'] = json_user_settings['exit_key']
            self.user_settings['capture_key'] = json_user_settings['capture_key']
            self.user_settings['toggle_key'] = json_user_settings['toggle_key']
        except:
            print(f'Could not reach settings file:{JSON_PATH}')
    
    
    