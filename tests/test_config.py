import unittest
import json
import os
from unittest.mock import patch, mock_open
from src.config import load_config, DEFAULT_CONFIG

class TestConfig(unittest.TestCase):
    def test_load_config_file_not_found(self):
        """Test that default config is returned when file does not exist."""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = False
            config = load_config("non_existent_file.json")
            self.assertEqual(config, DEFAULT_CONFIG)

    def test_load_config_valid_file(self):
        """Test loading a valid configuration file."""
        test_config = {
            "sunshine_path": "C:\\Custom\\Sunshine.exe",
            "driver_tool_path": "C:\\Custom\\Driver.exe"
        }
        with patch('os.path.exists') as mock_exists, \
             patch('builtins.open', mock_open(read_data=json.dumps(test_config))):
            mock_exists.return_value = True
            config = load_config("dummy_path.json")
            self.assertEqual(config, test_config)

    def test_load_config_partial_file(self):
        """Test loading a configuration file with partial keys."""
        partial_config = {
            "sunshine_path": "C:\\Custom\\Sunshine.exe"
        }
        with patch('os.path.exists') as mock_exists, \
             patch('builtins.open', mock_open(read_data=json.dumps(partial_config))):
            mock_exists.return_value = True
            config = load_config("dummy_path.json")

            # sunshine_path should be updated
            self.assertEqual(config["sunshine_path"], partial_config["sunshine_path"])
            # driver_tool_path should remain default
            self.assertEqual(config["driver_tool_path"], DEFAULT_CONFIG["driver_tool_path"])

    def test_load_config_malformed_json(self):
        """Test handling of malformed JSON file."""
        with patch('os.path.exists') as mock_exists, \
             patch('builtins.open', mock_open(read_data="{invalid_json")):
            mock_exists.return_value = True

            # Should log error and return defaults
            with self.assertLogs(level='ERROR') as cm:
                config = load_config("dummy_path.json")
                self.assertEqual(config, DEFAULT_CONFIG)
                self.assertTrue(any("Error decoding JSON" in log for log in cm.output))

    def test_load_config_permission_error(self):
        """Test handling of unexpected errors (e.g. permission error)."""
        with patch('os.path.exists') as mock_exists, \
             patch('builtins.open', side_effect=PermissionError("Access denied")):
            mock_exists.return_value = True

            with self.assertLogs(level='ERROR') as cm:
                config = load_config("dummy_path.json")
                self.assertEqual(config, DEFAULT_CONFIG)
                self.assertTrue(any("Unexpected error loading config" in log for log in cm.output))

if __name__ == '__main__':
    unittest.main()
