"""
Settings service for ToriiKanji.
Singleton that manages user preferences stored in a JSON file.
"""

import json
import os
from threading import Lock

from utils.paths import JSON_PATH


class SingletonMeta(type):
    """Thread-safe singleton metaclass."""
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
            return cls._instances[cls]


class SettingsService(metaclass=SingletonMeta):
    """
    Manages user settings persisted in a JSON file.
    Uses the Singleton pattern to ensure a single instance across the app.
    """

    # Default settings — new installs start with these values
    DEFAULT_SETTINGS = {
        # Hotkeys
        'exit_key': 'f4',
        'capture_key': 'f9',
        'toggle_key': 'f10',

        # Saving behavior
        'auto_save': False,
        'save_image': False,
        'show_media_dialog': True,

        # Display
        'display_mode': 'overlay',      # 'overlay' | 'windowed' | 'compact'
        'window_opacity': 92,           # 20-100 (percentage)

        # OCR
        'ocr_preprocessing': True,      # Enable/disable image pre-processing

        # Capture storage
        'capture_save_dir': '',         # Empty = default (AppData/captures)

        # Language
        'lang': 'en',
    }

    def __init__(self):
        self.user_settings = dict(self.DEFAULT_SETTINGS)

        if not os.path.exists(JSON_PATH):
            self._write_settings()

        self._load_settings()

    def edit_settings_file(self, key, value):
        """Update a single setting and persist to disk."""
        self.user_settings[key] = value
        self._write_settings()
        self._load_settings()

    def get(self, key, default=None):
        """Get a setting value with an optional default."""
        return self.user_settings.get(key, default)

    def _write_settings(self):
        """Write current settings to the JSON file."""
        try:
            os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)
            with open(JSON_PATH, 'w') as file:
                json.dump(self.user_settings, file, indent=4)
        except Exception as e:
            print(f"Error writing settings file: {e}")

    def _load_settings(self):
        """Load settings from JSON file, merging with defaults for any missing keys."""
        try:
            with open(JSON_PATH, 'r') as file:
                saved_settings = json.load(file)

            # Merge: saved values override defaults, but new defaults are preserved
            self.user_settings = dict(self.DEFAULT_SETTINGS)
            self.user_settings.update(saved_settings)
        except Exception as e:
            print(f"Could not read settings file ({JSON_PATH}): {e}")
