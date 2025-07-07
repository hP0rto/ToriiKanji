import keyboard
import os
from lxml import etree

class setting_services:
    def __init__(self):
        self.xml_path = self.get_xml_path()
        self.exit_key = 'f4'
        self.capture_key = 'f9' 
        self.toggle_key = 'f10'
        pass   

    def get_xml_path(self):
        '''Get .xml file path'''
        # get appdata location 
        appdata_path = os.getenv('APPDATA')

        # create subfolder on appdata/Roaming
        my_app_path = os.path.join(appdata_path, 'ToriiKanji')
        os.makedirs(my_app_path, exist_ok=True)
        
        # get usersettings.xml
        xml_path = os.path.join(my_app_path,'usersettings.xml')

        return xml_path


    def create_hotkey_file(self): 
        '''Create usersettings.xml if none exists''' 
        self.xml_path

        if not os.path.exists(self.xml_path):
        # create xml file
            data = etree.Element('hotkeys')

            element1 = etree.SubElement(data, 'exit')
            element1.set('key', 'f4')
            
            element2 = etree.SubElement(data, 'capture')
            element2.set('key', 'f9')

            element3 = etree.SubElement(data, 'toggle')
            element3.set('key', 'f10')

            b_xml = etree.tostring(data)
            with open(self.xml_path, 'wb') as f:
                f.write(b_xml)
        


    def edit_hotkey_file(self):   
        self.xml_path
        
        tree = etree.parse(self.xml_path)
        root = tree.getroot()

        exit_element = root.find('exit')
        if exit_element is not None:
            exit_element.set('key', 'f8')

        tree.write(self.xml_path, pretty_print=True, xml_declaration=True, encoding='utf-8')


        self.set_setting()
        


    def set_setting(self):
        self.xml_path
        tree = etree.parse(self.xml_path, None)

        self.exit_key = tree.find('exit').get('key')
        self.capture_key = tree.find('capture').get('key')
        self.toggle_key = tree.find('toggle').get('key')