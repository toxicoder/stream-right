import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os

# Mock winreg before importing GameScanner if it's missing (Linux)
if 'winreg' not in sys.modules:
    sys.modules['winreg'] = MagicMock()

from src.game_scanner import GameScanner

class TestGameScanner(unittest.TestCase):
    def setUp(self):
        self.scanner = GameScanner()

    @patch("src.game_scanner.winreg.OpenKey")
    @patch("src.game_scanner.winreg.QueryValueEx")
    @patch("src.game_scanner.winreg.CloseKey")
    @patch("os.path.exists")
    @patch("src.game_scanner.GameScanner._parse_library_folders")
    @patch("os.listdir")
    @patch("src.game_scanner.GameScanner._parse_app_manifest")
    def test_scan_steam_library(self, mock_parse_manifest, mock_listdir, mock_parse_folders, mock_exists, mock_close_key, mock_query_value, mock_open_key):
        # Only run if winreg is mockable or present
        if not hasattr(self.scanner, 'scan_steam_library'):
             return

        # Mock Registry
        mock_query_value.return_value = (r"C:\Program Files (x86)\Steam", 1)

        # Mock file existence
        mock_exists.return_value = True

        # Mock library folders
        mock_parse_folders.return_value = [r"C:\Program Files (x86)\Steam"]

        # Mock listdir
        mock_listdir.return_value = ["appmanifest_10.acf"]

        # Mock parse manifest
        expected_game = {
            "name": "Counter-Strike",
            "cmd": "steam://rungameid/10",
            "working_dir": r"C:\Program Files (x86)\Steam\steamapps\common\Half-Life",
            "platform": "steam"
        }
        mock_parse_manifest.return_value = expected_game

        games = self.scanner.scan_steam_library()

        self.assertEqual(len(games), 1)
        self.assertEqual(games[0]["name"], "Counter-Strike")
        self.assertEqual(games[0]["platform"], "steam")

    def test_parse_library_folders(self):
        vdf_content = """"libraryfolders"
{
    "1"
    {
        "path"      "C:\\Program Files (x86)\\Steam"
    }
    "2"
    {
        "path"      "D:\\Games\\SteamLibrary"
    }
}
"""
        with patch("builtins.open", mock_open(read_data=vdf_content)):
            paths = self.scanner._parse_library_folders("dummy_path")
            self.assertEqual(len(paths), 2)
            self.assertIn(r"C:\Program Files (x86)\Steam", paths)
            self.assertIn(r"D:\Games\SteamLibrary", paths)

    def test_parse_app_manifest(self):
        manifest_content = """"AppState"
{
    "appid"     "10"
    "Universe"      "1"
    "name"      "Counter-Strike"
    "StateFlags"        "4"
    "installdir"        "Half-Life"
}
"""
        with patch("builtins.open", mock_open(read_data=manifest_content)):
            # Use os.path.join for cross-platform compatibility in test expectation
            steamapps_path = os.path.join("C:", "Steam", "steamapps")
            game = self.scanner._parse_app_manifest("dummy_path", steamapps_path)
            self.assertEqual(game["name"], "Counter-Strike")
            self.assertEqual(game["cmd"], "steam://rungameid/10")

            expected_dir = os.path.join(os.path.dirname(steamapps_path), "common", "Half-Life")
            self.assertEqual(game["working_dir"], expected_dir)

if __name__ == '__main__':
    unittest.main()
