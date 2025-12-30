import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
from src.installer import download_file, extract_zip

class TestInstaller(unittest.TestCase):

    @patch('src.installer.requests.get')
    def test_download_file_success(self, mock_get):
        # Mock response
        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b'chunk1', b'chunk2']
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        with patch('builtins.open', mock_open()) as mock_file:
            result = download_file("http://example.com/file.zip", "test.zip")

            self.assertTrue(result)
            mock_file.assert_called_with("test.zip", 'wb')
            mock_file().write.assert_any_call(b'chunk1')
            mock_file().write.assert_any_call(b'chunk2')

    @patch('src.installer.requests.get')
    def test_download_file_failure(self, mock_get):
        mock_get.side_effect = Exception("Download failed")
        result = download_file("http://example.com/file.zip", "test.zip")
        self.assertFalse(result)

    @patch('src.installer.zipfile.ZipFile')
    def test_extract_zip_success(self, mock_zipfile):
        mock_zip_ref = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_ref

        result = extract_zip("test.zip", "extract_dir")

        self.assertTrue(result)
        mock_zip_ref.extractall.assert_called_with("extract_dir")

    @patch('src.installer.zipfile.ZipFile')
    def test_extract_zip_failure(self, mock_zipfile):
        mock_zipfile.side_effect = Exception("Extraction failed")

        result = extract_zip("test.zip", "extract_dir")

        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
