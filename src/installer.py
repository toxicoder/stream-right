import os
import requests
import zipfile
import logging

def download_file(url, dest):
    """
    Downloads a file from a URL to a destination path.
    """
    try:
        logging.info(f"Downloading {url} to {dest}...")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(dest, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logging.info("Download complete.")
        return True
    except Exception as e:
        logging.error(f"Failed to download file: {e}")
        return False

def extract_zip(zip_path, extract_to):
    """
    Extracts a ZIP file to a destination directory.
    """
    try:
        logging.info(f"Extracting {zip_path} to {extract_to}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        logging.info("Extraction complete.")
        return True
    except Exception as e:
        logging.error(f"Failed to extract zip file: {e}")
        return False
