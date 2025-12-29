import argparse
import sys
import logging
import os
import time

from .display_manager import DisplayManager
from .gpu_manager import GPUManager
from .utils import run_command, setup_logging
from .config import Config

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
        self.display_manager.create_virtual_display(self.driver_tool_path)

        # 3. Set Resolution
        logging.info("Setting resolution...")
        # Note: We'd need the specific device name for the virtual display in reality.
        # Passing None to target primary/default for demonstration/fallback.
        self.display_manager.set_resolution(width, height)

        # 4. Turn off physical display
        logging.info("Turning off physical display...")
        self.display_manager.toggle_physical_display(enable=False)

        logging.info("Setup complete. Ready for streaming.")

    def stop(self):
        """
        Stops the streaming setup and reverts changes.
        """
        logging.info("Stopping setup...")

        # 1. Re-enable physical display
        logging.info("Waking up physical display...")
        self.display_manager.toggle_physical_display(enable=True)

        # 2. Revert other changes if necessary (e.g., remove virtual display)
        # self.display_manager.remove_virtual_display(...)

        logging.info("Teardown complete.")

    def install(self):
        """
        Installs necessary dependencies.
        """
        logging.info("Installing dependencies...")
        # Logic to download/install drivers would go here.
        logging.info("Dependencies installed (simulated).")

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
