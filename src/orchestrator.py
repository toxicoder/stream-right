import argparse
import logging
import os
import sys
import time

from .config import Config
from .display_manager import DisplayManager
from .gpu_manager import GPUManager
from .installer import download_file, extract_zip, install_driver
from .utils import setup_logging

# Configure logging
setup_logging()

class Orchestrator:
    """
    Main orchestrator for handling the streaming lifecycle.
    """
    def __init__(self):
        self.config = Config()
        self.display_manager = DisplayManager()
        self.gpu_manager = GPUManager()

        self.sunshine_path = self.config.get("sunshine_path")
        self.driver_tool_path = self.config.get("driver_tool_path")

        # Check if paths exist
        if not os.path.exists(self.sunshine_path):
             logging.warning(f"Sunshine executable not found at: {self.sunshine_path}")

        if not os.path.exists(self.driver_tool_path):
             logging.warning(f"Driver tool not found at: {self.driver_tool_path}")

    def start(self, client_res):
        """
        Starts the streaming setup.

        Args:
            client_res (str): The desired resolution in the format "WIDTHxHEIGHT" (e.g., "1920x1080").
        """
        logging.info(f"Starting setup with resolution: {client_res}")

        # Parse resolution
        try:
            width, height = map(int, client_res.lower().split('x'))
        except ValueError:
            logging.error("Invalid resolution format. Use WIDTHxHEIGHT (e.g., 1920x1080)")
            return

        # 1. Force dGPU for Sunshine
        logging.info("Forcing dGPU for Sunshine...")
        self.gpu_manager.force_high_performance(self.sunshine_path)

        # 2. Create/Prepare Virtual Display
        logging.info("Preparing virtual display...")
        # In a real run, we might verify if it exists first.
        virtual_display_device = self.display_manager.create_virtual_display(self.driver_tool_path)
        if not virtual_display_device:
            logging.error("Failed to create virtual display or identify the new device. Aborting setup.")
            return

        # 3. Set Resolution
        logging.info("Setting resolution...")
        if not self.display_manager.set_resolution(width, height, device_name=virtual_display_device):
            logging.error("Failed to set resolution. Aborting setup.")
            return

        # 4. Turn off physical display
        logging.info("Turning off physical display...")
        if not self.display_manager.toggle_physical_display(enable=False):
            logging.warning("Failed to turn off physical display.")

        logging.info("Setup complete. Ready for streaming.")

    def stop(self):
        """
        Stops the streaming setup and reverts changes.

        This involves waking up the physical display and potentially removing virtual displays.
        """
        logging.info("Stopping setup...")

        # 1. Re-enable physical display
        logging.info("Waking up physical display...")
        if not self.display_manager.toggle_physical_display(enable=True):
             logging.warning("Failed to turn on physical display.")

        # 2. Revert other changes if necessary (e.g., remove virtual display)
        self.display_manager.remove_virtual_display(self.driver_tool_path)

        logging.info("Teardown complete.")

    def install(self):
        """
        Installs necessary dependencies.

        Downloads and installs the Virtual Display Driver and potentially other tools.
        Uses configuration to determine URLs and paths.
        """
        logging.info("Installing dependencies...")

        # Define URL and paths
        driver_url = self.config.get("virtual_display_driver_url")
        deps_path = self.config.get("deps_path")
        driver_checksum = self.config.get("driver_checksum")

        # Resolve absolute path for deps
        if not os.path.isabs(deps_path):
             base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
             deps_dir = os.path.join(base_dir, deps_path)
        else:
             deps_dir = deps_path

        zip_path = os.path.join(deps_dir, "Virtual-Display-Driver.zip")

        if not os.path.exists(deps_dir):
            os.makedirs(deps_dir)

        # Download
        if download_file(driver_url, zip_path, checksum=driver_checksum):
            # Extract
            if extract_zip(zip_path, deps_dir):
                logging.info(f"Dependencies extracted to {deps_dir}")

                # Attempt automated installation
                logging.info("Attempting automated driver installation...")
                if install_driver(deps_dir):
                     logging.info("Automated installation steps finished.")
                else:
                     logging.info("Manual installation might be required. Please check the extracted files.")

                logging.info("If the driver is not working, please manually install using the extracted files (e.g. run install_cert.bat and add device via Device Manager).")

                # Clean up zip
                try:
                    os.remove(zip_path)
                except Exception as e:
                    logging.warning(f"Could not remove zip file: {e}")
            else:
                logging.error("Failed to extract dependencies.")
        else:
            logging.error("Failed to download dependencies.")

def main():
    parser = argparse.ArgumentParser(description="Easy Game Streaming Orchestrator")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    start_parser = subparsers.add_parser("start", help="Start the streaming setup")
    start_parser.add_argument("--client-res", type=str, required=True, help="Client resolution (e.g., 1920x1080)")

    stop_parser = subparsers.add_parser("stop", help="Stop the streaming setup")

    install_parser = subparsers.add_parser("install", help="Install dependencies")

    args = parser.parse_args()

    orchestrator = Orchestrator()

    if args.command == "start":
        orchestrator.start(args.client_res)
    elif args.command == "stop":
        orchestrator.stop()
    elif args.command == "install":
        orchestrator.install()
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
