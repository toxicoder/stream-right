import os
import requests
import zipfile
import logging
import subprocess

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

def install_driver(deps_path):
    """
    Installs the driver from the dependencies folder.
    Searches for .bat files (certificates) and .inf files (drivers).
    """
    logging.info(f"Searching for driver files in {deps_path}...")

    cert_installed = False
    driver_installed = False

    for root, dirs, files in os.walk(deps_path):
        # Install Certificates (.bat)
        for file in files:
            if file.lower().endswith(".bat"):
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
