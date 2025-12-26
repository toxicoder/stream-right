import unittest
from unittest.mock import patch, MagicMock
import sys

# Mock windows modules
sys.modules['win32api'] = MagicMock()
sys.modules['win32con'] = MagicMock()
sys.modules['ctypes'] = MagicMock()
sys.modules['ctypes.wintypes'] = MagicMock()

from src.display_manager import DisplayManager

class TestDisplayManager(unittest.TestCase):
    def setUp(self):
        self.manager = DisplayManager()

    @patch('src.display_manager.run_command')
    def test_create_virtual_display_success(self, mock_run):
        mock_run.return_value = (0, "Success", "")
        result = self.manager.create_virtual_display("path/to/driver.exe")
        self.assertTrue(result)
        mock_run.assert_called_with('"path/to/driver.exe" add')

    @patch('src.display_manager.run_command')
    def test_create_virtual_display_failure(self, mock_run):
        mock_run.return_value = (1, "", "Error")
        result = self.manager.create_virtual_display("path/to/driver.exe")
        self.assertFalse(result)

    @patch('src.display_manager.win32api')
    @patch('src.display_manager.win32con')
    def test_set_resolution_success(self, mock_con, mock_api):
        mock_con.ENM_CURRENT_SETTINGS = -1
        mock_con.DM_PELSWIDTH = 0x80000
        mock_con.DM_PELSHEIGHT = 0x100000
        mock_con.CDS_TEST = 2
        mock_con.DISP_CHANGE_SUCCESSFUL = 0

        # Mock device
        mock_device = MagicMock()
        mock_device.DeviceName = "DISPLAY1"
        mock_api.EnumDisplayDevices.return_value = mock_device

        # Mock DevMode
        mock_devmode = MagicMock()
        mock_api.EnumDisplaySettings.return_value = mock_devmode

        mock_api.ChangeDisplaySettingsEx.return_value = 0 # Success

        result = self.manager.set_resolution(1920, 1080)

        self.assertTrue(result)
        self.assertEqual(mock_devmode.PelsWidth, 1920)
        self.assertEqual(mock_devmode.PelsHeight, 1080)
        # Should be called twice: once for test, once for real
        self.assertEqual(mock_api.ChangeDisplaySettingsEx.call_count, 2)

    @patch('src.display_manager.ctypes')
    def test_toggle_physical_display(self, mock_ctypes):
        # Mocking SendMessageW
        mock_ctypes.windll.user32.SendMessageW.return_value = 0

        result = self.manager.toggle_physical_display(enable=False)
        self.assertTrue(result)
        mock_ctypes.windll.user32.SendMessageW.assert_called()

        # Verify arguments (handle, msg, wparam, lparam)
        args = mock_ctypes.windll.user32.SendMessageW.call_args[0]
        self.assertEqual(args[3], 2) # monitor_off = 2

        result = self.manager.toggle_physical_display(enable=True)
        args = mock_ctypes.windll.user32.SendMessageW.call_args[0]
        self.assertEqual(args[3], -1) # monitor_on = -1

if __name__ == '__main__':
    unittest.main()
