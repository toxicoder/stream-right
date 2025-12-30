import unittest
from unittest.mock import patch, MagicMock
import sys

# Ensure mocks for dependencies are in place before importing orchestrator
sys.modules['win32api'] = MagicMock()
sys.modules['win32con'] = MagicMock()
sys.modules['ctypes'] = MagicMock()
sys.modules['winreg'] = MagicMock()

from src.orchestrator import Orchestrator

class TestOrchestrator(unittest.TestCase):
    def setUp(self):
        self.orchestrator = Orchestrator()

    @patch('src.orchestrator.DisplayManager')
    @patch('src.orchestrator.GPUManager')
    def test_start_success(self, MockGPU, MockDisplay):
        # We need to mock the instances attached to self.orchestrator
        self.orchestrator.display_manager = MockDisplay()
        self.orchestrator.gpu_manager = MockGPU()

        self.orchestrator.start("1920x1080")

        self.orchestrator.gpu_manager.force_high_performance.assert_called()
        self.orchestrator.display_manager.create_virtual_display.assert_called()
        self.orchestrator.display_manager.set_resolution.assert_called_with(1920, 1080)
        self.orchestrator.display_manager.toggle_physical_display.assert_called_with(enable=False)

    @patch('src.orchestrator.DisplayManager')
    def test_start_invalid_resolution(self, MockDisplay):
        self.orchestrator.display_manager = MockDisplay()

        # Should return early and not call anything
        self.orchestrator.start("invalid")

        self.orchestrator.display_manager.set_resolution.assert_not_called()

    @patch('src.orchestrator.DisplayManager')
    def test_stop_success(self, MockDisplay):
        self.orchestrator.display_manager = MockDisplay()

        self.orchestrator.stop()

        self.orchestrator.display_manager.toggle_physical_display.assert_called_with(enable=True)

    @patch('src.orchestrator.download_file')
    @patch('src.orchestrator.extract_zip')
    def test_install(self, mock_extract, mock_download):
        mock_download.return_value = True
        mock_extract.return_value = True

        # Just ensure it runs without error and calls the mocks
        self.orchestrator.install()

        mock_download.assert_called()
        mock_extract.assert_called()

if __name__ == '__main__':
    unittest.main()
