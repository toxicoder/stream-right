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
        # Mock load_config
        self.config_patcher = patch('src.orchestrator.load_config')
        self.mock_load_config = self.config_patcher.start()
        self.mock_load_config.return_value = {
            "sunshine_path": r"C:\Mock\Sunshine.exe",
            "driver_tool_path": r"C:\Mock\Driver.exe"
        }
        self.addCleanup(self.config_patcher.stop)

        # Mock os.path.exists to prevent file checks from failing
        self.path_exists_patcher = patch('os.path.exists')
        self.mock_path_exists = self.path_exists_patcher.start()
        self.mock_path_exists.return_value = True
        self.addCleanup(self.path_exists_patcher.stop)

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

    def test_install(self):
        # Just ensure it runs without error
        self.orchestrator.install()

if __name__ == '__main__':
    unittest.main()
