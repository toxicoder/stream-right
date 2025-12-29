import unittest
from unittest.mock import patch, MagicMock
from src import utils

class TestUtils(unittest.TestCase):
    @patch('subprocess.run')
    def test_run_command_success(self, mock_run):
        # Mock setup
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        code, stdout, stderr = utils.run_command(["echo", "hello"])

        self.assertEqual(code, 0)
        self.assertEqual(stdout, "output")
        self.assertEqual(stderr, "")
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_run_command_failure(self, mock_run):
        # Mock setup
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "error"
        mock_run.return_value = mock_result

        code, stdout, stderr = utils.run_command("invalid_command")

        self.assertEqual(code, 1)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "error")

    @patch('subprocess.run')
    def test_run_command_exception(self, mock_run):
        mock_run.side_effect = Exception("Crash")

        code, stdout, stderr = utils.run_command("crash")

        self.assertEqual(code, -1)
        self.assertEqual(stdout, "")
        self.assertIn("Crash", stderr)

if __name__ == '__main__':
    unittest.main()
