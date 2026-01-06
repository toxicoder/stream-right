import argparse
import logging
import os
import sys
import time

from .config import Config
from .display_manager import DisplayManager
from .gpu_manager import GPUManager
from .installer import download_file, extract_zip, install_driver
from .game_scanner import GameScanner
from .metadata_provider import IGDBMetadataProvider
from .sunshine_manager import SunshineManager
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
        if not self.display_manager.create_virtual_display(self.driver_tool_path):
            logging.error("Failed to create virtual display. Aborting setup.")
            return

        # 3. Set Resolution
        logging.info("Setting resolution...")
        # Note: We'd need the specific device name for the virtual display in reality.
        # Passing None to target primary/default for demonstration/fallback.
        if not self.display_manager.set_resolution(width, height):
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
        # self.display_manager.remove_virtual_display(...)

        logging.info("Teardown complete.")

    def scan_games(self):
        """
        Scans for games, fetches metadata from IGDB, and updates Sunshine config.
        """
        client_id = self.config.get("igdb_client_id")
        client_secret = self.config.get("igdb_client_secret")

        if not client_id or not client_secret:
            logging.error("IGDB credentials not found. Please set IGDB_CLIENT_ID and IGDB_CLIENT_SECRET in environment or config.")
            return

        logging.info("Initializing game scanner...")
        scanner = GameScanner()
        games = scanner.scan_system()
        logging.info(f"Found {len(games)} games.")

        logging.info("Initializing metadata provider...")
        metadata_provider = IGDBMetadataProvider(client_id, client_secret)
        if not metadata_provider.authenticate():
            logging.error("Failed to authenticate with IGDB. Aborting.")
            return

        logging.info("Initializing Sunshine manager...")
        sunshine_manager = SunshineManager(self.sunshine_path)

        # Create covers directory
        covers_dir = os.path.join(os.path.dirname(sunshine_manager.config_path), "covers")
        os.makedirs(covers_dir, exist_ok=True)

        for game in games:
            name = game["name"]
            logging.info(f"Processing {name}...")

            # Search IGDB
            game_data = metadata_provider.search_game(name)
            image_path = ""

            if game_data:
                cover_url = metadata_provider.get_cover_art(game_data)
                if cover_url:
                    # Sanitize filename
                    safe_name = "".join([c for c in name if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                    local_cover_path = os.path.join(covers_dir, f"{safe_name}.jpg")

                    if metadata_provider.download_cover_art(cover_url, local_cover_path):
                        image_path = local_cover_path
                        logging.info(f"Downloaded cover for {name}")
            else:
                logging.warning(f"No metadata found for {name}")

            # Update Sunshine
            sunshine_manager.add_game(name, game["cmd"], game["working_dir"], image_path)

        logging.info("Game scan and update complete.")

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
        if download_file(driver_url, zip_path):
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

    scan_parser = subparsers.add_parser("scan", help="Scan for games and update Sunshine")

    args = parser.parse_args()

    orchestrator = Orchestrator()

    if args.command == "start":
        orchestrator.start(args.client_res)
    elif args.command == "stop":
        orchestrator.stop()
    elif args.command == "install":
        orchestrator.install()
    elif args.command == "scan":
        orchestrator.scan_games()
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
