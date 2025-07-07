import keyboard
from core.setting_services import setting_services
from PyQt6.QtCore import QEvent  
from PyQt6.QtWidgets import QApplication
from lxml import etree

class CustomHotkeyEvent(QEvent):
  def __init__(self, tipo):
      super().__init__(QEvent.Type(QEvent.registerEventType()))
      self.tipo = tipo     

def config_hotkey(self):
        settings = setting_services()

        keyboard.add_hotkey(settings.exit_key, lambda: QApplication.postEvent(self, CustomHotkeyEvent("exit")))
        keyboard.add_hotkey(settings.capture_key, lambda: QApplication.postEvent(self, CustomHotkeyEvent("capture")))
        keyboard.add_hotkey(settings.toggle_key, lambda: QApplication.postEvent(self, CustomHotkeyEvent("toggle")))


    