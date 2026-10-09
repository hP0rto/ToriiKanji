"""
Hotkey configuration service.
Maps keyboard hotkeys to Qt events for the main window.
"""

import keyboard
from PyQt6.QtCore import QEvent
from PyQt6.QtWidgets import QApplication

from core.services.setting_services import SettingsService


class CustomHotkeyEvent(QEvent):
    """Custom Qt event triggered by global hotkeys."""

    def __init__(self, action_type):
        super().__init__(QEvent.Type(QEvent.registerEventType()))
        self.action_type = action_type


def config_hotkey(target_widget):
    """Register all hotkeys to post events to the target widget."""
    settings = SettingsService()
    keyboard.add_hotkey(
        settings.user_settings['exit_key'],
        lambda: QApplication.postEvent(target_widget, CustomHotkeyEvent('exit'))
    )
    keyboard.add_hotkey(
        settings.user_settings['capture_key'],
        lambda: QApplication.postEvent(target_widget, CustomHotkeyEvent('capture'))
    )
    keyboard.add_hotkey(
        settings.user_settings['toggle_key'],
        lambda: QApplication.postEvent(target_widget, CustomHotkeyEvent('toggle'))
    )


def update_hotkey(target_widget):
    """Remove all hotkeys and re-register them with current settings."""
    keyboard.remove_all_hotkeys()
    config_hotkey(target_widget)
