import json
import os
import logging
import shutil

class SunshineManager:
    def __init__(self, sunshine_path):
        self.sunshine_path = sunshine_path
        # Assuming apps.json is in the same directory as Sunshine.exe or in a config subfolder
        # Standard Sunshine install might be C:\Program Files\Sunshine\config\apps.json or C:\Program Files\Sunshine\apps.json
        # Also could be in %ProgramData% on Windows?
        # Let's try to locate it or default to a safe location.

        base_dir = os.path.dirname(sunshine_path)

        # Check potential locations
        possible_paths = [
            os.path.join(base_dir, "config", "apps.json"),
            os.path.join(base_dir, "apps.json"),
            os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "Sunshine", "config", "apps.json")
        ]

        self.config_path = None
        for path in possible_paths:
            if os.path.exists(path):
                self.config_path = path
                break

        if not self.config_path:
            # If not found, default to config/apps.json relative to exe
            self.config_path = os.path.join(base_dir, "config", "apps.json")

        logging.info(f"Using Sunshine config at: {self.config_path}")

    def add_game(self, name, cmd, working_dir, image_path):
        """
        Adds or updates a game in Sunshine's apps.json.
        """
        # Ensure config dir exists
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

        data = {"env": {}, "apps": []}

        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    content = f.read()
                    if content.strip():
                        data = json.loads(content)
            except Exception as e:
                logging.error(f"Failed to read Sunshine config: {e}")
                return False

        # Check if game exists
        found = False
        for app in data["apps"]:
            if app["name"] == name:
                app["cmd"] = cmd
                app["working_dir"] = working_dir
                if image_path:
                    app["image-path"] = image_path
                found = True
                break

        if not found:
            new_app = {
                "name": name,
                "cmd": cmd,
                "working_dir": working_dir,
                "image-path": image_path if image_path else ""
            }
            # Optional: Add other fields like "detached", "output", etc. if needed.
            # Sunshine defaults are usually fine.
            data["apps"].append(new_app)

        try:
            with open(self.config_path, 'w') as f:
                json.dump(data, f, indent=4)
            logging.info(f"Updated Sunshine config for game: {name}")
            return True
        except Exception as e:
            logging.error(f"Failed to write Sunshine config: {e}")
            return False
