import unittest
from unittest.mock import patch, MagicMock
import sys

# Mock winreg before importing src.gpu_manager
sys.modules['winreg'] = MagicMock()

from src.gpu_manager import GPUManager

class TestGPUManager(unittest.TestCase):
    def setUp(self):
        self.manager = GPUManager()

    @patch('src.gpu_manager.winreg')
    def test_force_high_performance_success(self, mock_winreg):
        # Setup mocks
        mock_key = MagicMock()
        mock_winreg.CreateKey.return_value = mock_key
        mock_winreg.HKEY_CURRENT_USER = 1
        mock_winreg.REG_SZ = 1

        result = self.manager.force_high_performance("C:\\App.exe")

        self.assertTrue(result)
        mock_winreg.CreateKey.assert_called_with(1, r"Software\Microsoft\DirectX\UserGpuPreferences")
        mock_winreg.SetValueEx.assert_called_with(mock_key, "C:\\App.exe", 0, 1, "GpuPreference=2;")
        mock_winreg.CloseKey.assert_called_with(mock_key)

    @patch('src.gpu_manager.winreg')
    def test_force_high_performance_exception(self, mock_winreg):
        mock_winreg.CreateKey.side_effect = Exception("Registry Error")

        result = self.manager.force_high_performance("C:\\App.exe")

        self.assertFalse(result)

    @patch('src.gpu_manager.winreg')
    def test_force_high_performance_permission_error(self, mock_winreg):
        # Create an OSError with winerror=5 (Access Denied)
        error = OSError()
        error.winerror = 5
        mock_winreg.CreateKey.side_effect = error

        result = self.manager.force_high_performance("C:\\App.exe")
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
