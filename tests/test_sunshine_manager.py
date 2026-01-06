import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import os
from src.sunshine_manager import SunshineManager

class TestSunshineManager(unittest.TestCase):
    def setUp(self):
        self.sunshine_path = r"C:\Program Files\Sunshine\Sunshine.exe"
        self.manager = SunshineManager(self.sunshine_path)

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.makedirs")
    def test_add_game_new(self, mock_makedirs, mock_file, mock_exists):
        # Mock file existence: config does not exist initially
        mock_exists.side_effect = lambda x: x == self.manager.config_path

        # Mock reading empty or non-existent file
        # We need to manage the side_effect carefully.
        # When add_game opens the file for reading:
        read_handle = mock_open(read_data='{"apps": []}').return_value
        # When add_game opens the file for writing:
        write_handle = mock_open().return_value

        def side_effect(*args, **kwargs):
            mode = 'r'
            if len(args) > 1:
                mode = args[1]
            elif 'mode' in kwargs:
                mode = kwargs['mode']

            if 'r' in mode:
                return read_handle
            else:
                return write_handle

        mock_file.side_effect = side_effect

        success = self.manager.add_game("Test Game", "C:\\Game.exe", "C:\\", "cover.png")

        self.assertTrue(success)

        # Check if write was called with correct data
        # We need to inspect the write_handle we created
        # json.dump might call write multiple times
        written_content = "".join([call.args[0] for call in write_handle.write.mock_calls])
        written_data = json.loads(written_content)

        self.assertEqual(len(written_data["apps"]), 1)
        self.assertEqual(written_data["apps"][0]["name"], "Test Game")
        self.assertEqual(written_data["apps"][0]["image-path"], "cover.png")

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.makedirs")
    def test_add_game_update(self, mock_makedirs, mock_file, mock_exists):
        initial_data = {
            "apps": [
                {
                    "name": "Test Game",
                    "cmd": "OldPath.exe",
                    "working_dir": "OldDir",
                    "image-path": ""
                }
            ]
        }

        mock_exists.return_value = True

        # Mock reading existing file
        read_handle = mock_open(read_data=json.dumps(initial_data)).return_value
        write_handle = mock_open().return_value

        def side_effect(*args, **kwargs):
            mode = 'r'
            if len(args) > 1:
                mode = args[1]
            elif 'mode' in kwargs:
                mode = kwargs['mode']

            if 'r' in mode:
                return read_handle
            else:
                return write_handle

        mock_file.side_effect = side_effect

        success = self.manager.add_game("Test Game", "C:\\NewGame.exe", "C:\\NewDir", "new_cover.png")

        self.assertTrue(success)

        # Check if write was called with updated data
        # We need to inspect the write_handle we created
        written_content = "".join([call.args[0] for call in write_handle.write.mock_calls])
        written_data = json.loads(written_content)

        self.assertEqual(len(written_data["apps"]), 1)
        self.assertEqual(written_data["apps"][0]["name"], "Test Game")
        self.assertEqual(written_data["apps"][0]["cmd"], "C:\\NewGame.exe")
        self.assertEqual(written_data["apps"][0]["image-path"], "new_cover.png")

if __name__ == '__main__':
    unittest.main()
