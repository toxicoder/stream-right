import json
import os
import logging

DEFAULT_CONFIG = {
    "sunshine_path": r"C:\Program Files\Sunshine\Sunshine.exe",
    "driver_tool_path": r"C:\Path\To\VirtualDriverControl.exe"
}

def load_config(config_path=None):
    """
    Loads configuration from a JSON file.
    Falls back to default values if the file doesn't exist or keys are missing.
    """
    if config_path is None:
        # Resolve path relative to the project root
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, "config", "settings.json")

    config = DEFAULT_CONFIG.copy()

    if not os.path.exists(config_path):
        logging.warning(f"Config file not found at {config_path}. Using defaults.")
        return config

    try:
        with open(config_path, 'r') as f:
            file_config = json.load(f)
            # Update defaults with file values (only if they exist in file)
            config.update(file_config)
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from {config_path}. Using defaults.")
    except Exception as e:
        logging.error(f"Unexpected error loading config: {e}. Using defaults.")

    return config
