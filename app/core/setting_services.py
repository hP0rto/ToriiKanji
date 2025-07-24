import os
import json
from lxml import etree
from threading import Lock, Thread

APP_DATA = os.getenv('APPDATA')
JSON_PATH = os.path.join(APP_DATA, 'ToriiKanji\\usersettings.json')

class SingletonMeta(type):
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args,**kwargs)
                cls._instances[cls] = instance
            return cls._instances[cls]

# PEP 8: Class always CamelCase
class SettingsService(metaclass=SingletonMeta):
    # Singleton

    def __init__(self):
        self.user_settings = {
                'exit_key': 'f4',
                'capture_key': 'f9',
                'toggle_key': 'f10'
        } 
        self.create_settings_file()
        self.set_settings()


    def create_settings_file(self): 
        '''Create usersettings.json if none exists''' 
        #
        #   BART, não é melhor colocar essa verificação junto com o resto das coisas na linha 13?
        #   já q toda hora q for instanciado ele já vai ter q rodar isso daqui.
        #   se sua resposta for sim, exclui essa função e bota isso daqui junto com o resto dos coisas
        #
        if not os.path.exists(JSON_PATH):
            with open(JSON_PATH, 'w') as file:
                json.dump(self.user_settings, file, indent=4)
    
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
        

    # def get_xml_path(self):
    #     '''Get .xml file path'''
    #     # get appdata location 
    #     appdata_path = os.getenv('APPDATA')

    #     # create subfolder on appdata/Roaming
    #     my_app_path = os.path.join(appdata_path, 'ToriiKanji')
    #     os.makedirs(my_app_path, exist_ok=True)
        
    #     # get usersettings.xml
    #     xml_path = os.path.join(my_app_path,'usersettings.xml')

    #     return xml_path

    # def create_hotkey_file(self): 
    #     '''Create usersettings.xml if none exists''' 
    #     if not os.path.exists(self.xml_path):
    #     # create xml file
    #         data = etree.Element('hotkeys')

    #         element1 = etree.SubElement(data, 'exit')
    #         element1.set('key', 'f4')
            
    #         element2 = etree.SubElement(data, 'capture')
    #         element2.set('key', 'f9')

    #         element3 = etree.SubElement(data, 'toggle')
    #         element3.set('key', 'f10')

    #         b_xml = etree.tostring(data)
    #         with open(self.xml_path, 'wb') as f:
    #             f.write(b_xml)

    # def edit_hotkey_file(self):
    #     '''Edits the .xml file'''
    #     tree = etree.parse(self.xml_path)
    #     root = tree.getroot()

    #     exit_element = root.find('exit')
    #     if exit_element is not None:
    #         exit_element.set('key', 'f6')

    #     tree.write(self.xml_path, pretty_print=True, xml_declaration=True, encoding='utf-8')

    #     self.set_setting()

    
    

    # def set_setting(self):
    #     '''Sets class atributes to match the .xml'''
    #     tree = etree.parse(self.xml_path, None)

    #     self.exit_key = tree.find('exit').get('key')
    #     self.capture_key = tree.find('capture').get('key')
    #     self.toggle_key = tree.find('toggle').get('key')
    
    
    
    