import hashlib
import logging
import os
import subprocess
import zipfile

import requests

def download_file(url, dest, checksum=None):
    """
    Downloads a file from a URL to a destination path.

    Args:
        url (str): The URL to download from.
        dest (str): The file path where the downloaded content will be saved.
        checksum (str, optional): The SHA256 checksum to verify the file. Defaults to None.

    Returns:
        bool: True if download was successful and verified, False otherwise.
    """
    try:
        logging.info(f"Downloading {url} to {dest}...")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(dest, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logging.info("Download complete.")

        if checksum:
            logging.info("Verifying checksum...")
            sha256_hash = hashlib.sha256()
            with open(dest, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            calculated_checksum = sha256_hash.hexdigest()

            if calculated_checksum != checksum:
                logging.error(f"Checksum verification failed. Expected: {checksum}, Calculated: {calculated_checksum}")
                os.remove(dest)
                return False
            logging.info("Checksum verified successfully.")

        return True
    except Exception as e:
        logging.error(f"Failed to download file: {e}")
        if os.path.exists(dest):
            os.remove(dest)
        return False

def extract_zip(zip_path, extract_to):
    """
    Extracts a ZIP file to a destination directory.

    Args:
        zip_path (str): The path to the ZIP file.
        extract_to (str): The directory to extract contents to.

    Returns:
        bool: True if extraction was successful, False otherwise.
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

def install_driver(deps_path):
    """
    Installs the driver from the dependencies folder.
    Searches for .bat files (certificates) and .inf files (drivers).

    Args:
        deps_path (str): The path containing the driver files.

    Returns:
        bool: True if installation (certificate or driver) was attempted/successful, False if no installable files were found.
    """
    logging.info(f"Searching for driver files in {deps_path}...")

    cert_installed = False
    driver_installed = False

    for root, dirs, files in os.walk(deps_path):
        # Install Certificates (install_cert.bat)
        for file in files:
            if file.lower() == "install_cert.bat":
                bat_path = os.path.join(root, file)
                logging.info(f"Found certificate installer: {bat_path}")
                try:
                    # Run the batch file. Requires shell=True for .bat files usually, or passing to cmd /c
                    # For security we avoid shell=True if possible, but for bat files we need an interpreter.
                    # Using cmd.exe /c
                    logging.info("Running certificate installer...")
                    subprocess.run(["cmd.exe", "/c", bat_path], check=True, shell=False)
                    cert_installed = True
                    logging.info("Certificate installer executed successfully.")
                except subprocess.CalledProcessError as e:
                    logging.error(f"Failed to run certificate installer: {e}")
                except Exception as e:
                    logging.error(f"Error running certificate installer: {e}")

        # Install Driver (.inf)
        for file in files:
            if file.lower().endswith(".inf"):
                inf_path = os.path.join(root, file)
                logging.info(f"Found driver info file: {inf_path}")
                try:
                    logging.info("Installing driver via pnputil...")
                    # pnputil /add-driver "inf_path" /install
                    subprocess.run(["pnputil", "/add-driver", inf_path, "/install"], check=True, shell=False)
                    driver_installed = True
                    logging.info("Driver installed successfully.")
                except subprocess.CalledProcessError as e:
                    logging.error(f"Failed to install driver: {e}")
                except FileNotFoundError:
                     logging.error("pnputil not found. Make sure you are on Windows.")
                except Exception as e:
                    logging.error(f"Error installing driver: {e}")

    if cert_installed and driver_installed:
        logging.info("Driver installation automated steps completed.")
        return True
    elif cert_installed or driver_installed:
        logging.warning("Partial installation completed.")
        return True
    else:
        logging.warning("No installable driver files found.")
        return False
