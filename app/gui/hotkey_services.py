import keyboard
from core.setting_services import setting_services
from PyQt6.QtCore import QEvent  
from PyQt6.QtWidgets import QApplication


class CustomHotkeyEvent(QEvent):
    def __init__(self, tipo):
      super().__init__(QEvent.Type(QEvent.registerEventType()))
      self.tipo = tipo     

def config_hotkey(self):
  '''Maps the hotkey'''
  settings = setting_services()

  keyboard.add_hotkey(settings.exit_key, lambda: QApplication.postEvent(self, CustomHotkeyEvent("exit")))
  keyboard.add_hotkey(settings.capture_key, lambda: QApplication.postEvent(self, CustomHotkeyEvent("capture")))
  keyboard.add_hotkey(settings.toggle_key, lambda: QApplication.postEvent(self, CustomHotkeyEvent("toggle")))

def update_hotkey(self):
  '''Removes all hotkeys and remaps them'''
  keyboard.remove_all_hotkeys()
  config_hotkey(self)



    