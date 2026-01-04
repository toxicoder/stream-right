import unittest
import os
import json
import tempfile
from src.config import Config

class TestConfig(unittest.TestCase):
    def setUp(self):
        # Create a temporary config file
        self.temp_config_fd, self.temp_config_path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(self.temp_config_fd, 'w') as f:
            json.dump({
                "sunshine_path": "C:\\Custom\\Sunshine.exe",
                "driver_tool_path": "C:\\Custom\\Driver.exe"
            }, f)

    def tearDown(self):
        os.remove(self.temp_config_path)
        # Clear env vars if set
        if "SUNSHINE_PATH" in os.environ:
            del os.environ["SUNSHINE_PATH"]
        if "DRIVER_TOOL_PATH" in os.environ:
            del os.environ["DRIVER_TOOL_PATH"]

    def test_load_defaults(self):
        # Test loading defaults when file doesn't exist
        config = Config(config_path="non_existent_file.json")
        self.assertEqual(config.get("sunshine_path"), r"C:\Program Files\Sunshine\Sunshine.exe")
        self.assertEqual(config.get("driver_tool_path"), r"C:\Path\To\VirtualDriverControl.exe")

    def test_load_from_file(self):
        # Test loading from file. Since Config uses absolute path relative to file location,
        # we need to be careful. But Config() takes config_path which is joined with base_dir.
        # However, for this test, we want to point to our temp file.
        # But Config joins path.

        # Let's see src/config.py implementation again.
        # base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # self.config_path = os.path.join(base_dir, config_path)

        # So if we pass an absolute path as config_path, os.path.join might behave differently on Windows/Linux?
        # On Linux, os.path.join("/a", "/b") is "/b".
        # So if we pass absolute path to temp file, it should work.

        config = Config(config_path=self.temp_config_path)
        self.assertEqual(config.get("sunshine_path"), "C:\\Custom\\Sunshine.exe")
        self.assertEqual(config.get("driver_tool_path"), "C:\\Custom\\Driver.exe")

    def test_load_from_env(self):
        os.environ["SUNSHINE_PATH"] = "C:\\Env\\Sunshine.exe"
        os.environ["DRIVER_TOOL_PATH"] = "C:\\Env\\Driver.exe"

        config = Config(config_path="non_existent_file.json")
        self.assertEqual(config.get("sunshine_path"), "C:\\Env\\Sunshine.exe")
        self.assertEqual(config.get("driver_tool_path"), "C:\\Env\\Driver.exe")

    def test_env_override_file(self):
        os.environ["SUNSHINE_PATH"] = "C:\\Env\\Sunshine.exe"

        config = Config(config_path=self.temp_config_path)
        self.assertEqual(config.get("sunshine_path"), "C:\\Env\\Sunshine.exe")
        self.assertEqual(config.get("driver_tool_path"), "C:\\Custom\\Driver.exe") # From file

if __name__ == '__main__':
    unittest.main()
