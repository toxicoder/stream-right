import json
import os
import logging

class Config:
    DEFAULTS = {
        "sunshine_path": r"C:\Program Files\Sunshine\Sunshine.exe",
        "driver_tool_path": r"C:\Path\To\VirtualDriverControl.exe",
        "virtual_display_driver_url": "https://github.com/itsmikethetech/Virtual-Display-Driver/releases/download/23.12.2/Virtual-Display-Driver_23.12.2.zip",
        "deps_path": "deps",
        "igdb_client_id": "",
        "igdb_client_secret": ""
    }

    def __init__(self, config_path="config/settings.json"):
        self.config = self.DEFAULTS.copy()

        # Determine the absolute path for the config file
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = os.path.join(base_dir, config_path)

        self.load_from_file()
        self.load_from_env()

    def load_from_file(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    if data:
                        self.config.update(data)
            except Exception as e:
                logging.warning(f"Failed to load config file: {e}")
        else:
            logging.info(f"Config file not found at {self.config_path}, using defaults.")

    def load_from_env(self):
        # Override with environment variables if present
        if os.environ.get("SUNSHINE_PATH"):
            self.config["sunshine_path"] = os.environ.get("SUNSHINE_PATH")
        if os.environ.get("DRIVER_TOOL_PATH"):
            self.config["driver_tool_path"] = os.environ.get("DRIVER_TOOL_PATH")
        if os.environ.get("VIRTUAL_DISPLAY_DRIVER_URL"):
            self.config["virtual_display_driver_url"] = os.environ.get("VIRTUAL_DISPLAY_DRIVER_URL")
        if os.environ.get("DEPS_PATH"):
            self.config["deps_path"] = os.environ.get("DEPS_PATH")
        if os.environ.get("IGDB_CLIENT_ID"):
            self.config["igdb_client_id"] = os.environ.get("IGDB_CLIENT_ID")
        if os.environ.get("IGDB_CLIENT_SECRET"):
            self.config["igdb_client_secret"] = os.environ.get("IGDB_CLIENT_SECRET")

    def get(self, key):
        return self.config.get(key)
