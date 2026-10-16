import json
import tempfile
import unittest
from pathlib import Path

from core.services import setting_services


class SettingsServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.settings_file = Path(self.temp_dir.name) / "usersettings.json"
        self.original_json_path = setting_services.JSON_PATH
        setting_services.JSON_PATH = str(self.settings_file)
        setting_services.SingletonMeta._instances.pop(setting_services.SettingsService, None)

    def tearDown(self):
        setting_services.SingletonMeta._instances.pop(setting_services.SettingsService, None)
        setting_services.JSON_PATH = self.original_json_path
        self.temp_dir.cleanup()

    def test_load_settings_keeps_new_default_keys_when_saved_file_is_partial(self):
        partial_settings = {"lang": "pt"}
        self.settings_file.write_text(json.dumps(partial_settings), encoding="utf-8")

        service = setting_services.SettingsService()

        self.assertEqual(service.get("lang"), "pt")
        self.assertEqual(service.get("capture_key"), setting_services.SettingsService.DEFAULT_SETTINGS["capture_key"])
        self.assertEqual(service.get("display_mode"), setting_services.SettingsService.DEFAULT_SETTINGS["display_mode"])

    def test_load_settings_with_invalid_json_keeps_default_settings(self):
        self.settings_file.write_text("{invalid json", encoding="utf-8")

        service = setting_services.SettingsService()

        self.assertEqual(service.user_settings, setting_services.SettingsService.DEFAULT_SETTINGS)


if __name__ == "__main__":
    unittest.main()
