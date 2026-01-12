import os
import logging
import re

try:
    import winreg
except ImportError:
    winreg = None

class GameScanner:
    def __init__(self):
        pass

    def scan_steam_library(self):
        """
        Scans Steam library for installed games.
        Returns a list of dicts: {"name": str, "path": str, "platform": "steam"}
        """
        games = []
        try:
            # Find Steam Path
            hkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
            steam_path, _ = winreg.QueryValueEx(hkey, "SteamPath")
            winreg.CloseKey(hkey)

            # Allow for paths with forward slashes
            steam_path = os.path.normpath(steam_path)

            library_vdf_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
            if not os.path.exists(library_vdf_path):
                logging.warning(f"Steam library folders file not found: {library_vdf_path}")
                return games

            library_paths = self._parse_library_folders(library_vdf_path)

            # Add main steam path if not discovered (usually it is in libraryfolders.vdf)
            if steam_path not in library_paths:
                 library_paths.append(steam_path)

            for lib_path in library_paths:
                steamapps_path = os.path.join(lib_path, "steamapps")
                if not os.path.exists(steamapps_path):
                    continue

                for filename in os.listdir(steamapps_path):
                    if filename.startswith("appmanifest_") and filename.endswith(".acf"):
                        manifest_path = os.path.join(steamapps_path, filename)
                        game = self._parse_app_manifest(manifest_path, steamapps_path)
                        if game:
                            games.append(game)

        except Exception as e:
            logging.error(f"Error scanning Steam library: {e}")

        return games

    def _parse_library_folders(self, vdf_path):
        """
        Parses libraryfolders.vdf to find all library paths.
        This is a simple parser as VDF is somewhat like JSON but not quite.
        """
        paths = []
        try:
            with open(vdf_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Simple regex to find "path" "..."
                # Modern VDF looks like: "1" { "path" "C:\\Games\\Steam" ... }
                matches = re.findall(r'"path"\s+"([^"]+)"', content)
                for m in matches:
                    # Unescape double backslashes
                    path = m.replace(r'\\', '\\')
                    paths.append(path)
        except Exception as e:
            logging.error(f"Error parsing libraryfolders.vdf: {e}")
        return paths

    def _parse_app_manifest(self, manifest_path, steamapps_path):
        """
        Parses an app manifest to get game details.
        """
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()

            name_match = re.search(r'"name"\s+"([^"]+)"', content)
            install_dir_match = re.search(r'"installdir"\s+"([^"]+)"', content)

            if name_match and install_dir_match:
                name = name_match.group(1)
                install_dir = install_dir_match.group(1)

                # Construct full path
                # Game is usually in steamapps/common/install_dir
                full_path = os.path.join(os.path.dirname(steamapps_path), "common", install_dir)

                # We need an executable. This is tricky without knowing the exact exe name.
                # For now, we will store the directory. Sunshine can often infer or we might need to find the largest EXE.
                # Or we can use the steam protocol command: steam://rungameid/<id>

                appid_match = re.search(r'"appid"\s+"(\d+)"', content)
                appid = appid_match.group(1) if appid_match else None

                cmd = f"steam://rungameid/{appid}" if appid else full_path

                return {
                    "name": name,
                    "cmd": cmd, # Using steam protocol is safer for launching
                    "working_dir": full_path, # Not always needed for steam protocol but good to have
                    "platform": "steam"
                }
        except Exception as e:
            logging.warning(f"Error parsing manifest {manifest_path}: {e}")

        return None

    def scan_system(self):
        """
        Scans the system for all supported games.
        """
        all_games = []
        logging.info("Scanning Steam library...")
        all_games.extend(self.scan_steam_library())

        # Add other scanners here (Epic, GOG, etc.)

        return all_games
