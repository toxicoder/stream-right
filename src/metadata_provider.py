import requests
import logging
import os
import time

class IGDBMetadataProvider:
    AUTH_URL = "https://id.twitch.tv/oauth2/token"
    API_URL = "https://api.igdb.com/v4"

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expiry = 0

    def authenticate(self):
        """Authenticates with Twitch to get an access token."""
        if not self.client_id or not self.client_secret:
            logging.error("IGDB Client ID or Secret is missing.")
            return False

        if self.access_token and time.time() < self.token_expiry:
            return True

        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        try:
            response = requests.post(self.AUTH_URL, params=params)
            response.raise_for_status()
            data = response.json()
            self.access_token = data["access_token"]
            self.token_expiry = time.time() + data["expires_in"] - 60 # Buffer
            logging.info("Successfully authenticated with IGDB.")
            return True
        except Exception as e:
            logging.error(f"Failed to authenticate with IGDB: {e}")
            return False

    def search_game(self, game_name):
        """
        Searches for a game by name on IGDB.
        Returns the first match with a cover.
        """
        if not self.authenticate():
            return None

        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}"
        }

        # Search for game and get cover
        query = f'search "{game_name}"; fields name,cover.url; where cover != null; limit 1;'

        try:
            response = requests.post(f"{self.API_URL}/games", headers=headers, data=query)
            response.raise_for_status()
            data = response.json()
            if data:
                return data[0]
            return None
        except Exception as e:
            logging.error(f"Failed to search game {game_name}: {e}")
            return None

    def get_cover_art(self, game_data):
        """Extracts the cover art URL from game data."""
        if not game_data or "cover" not in game_data or "url" not in game_data["cover"]:
            return None

        url = game_data["cover"]["url"]
        if url.startswith("//"):
            url = "https:" + url

        # Get higher resolution (t_720p or t_1080p instead of t_thumb)
        url = url.replace("t_thumb", "t_720p")
        return url

    def download_cover_art(self, url, save_path):
        """Downloads the cover art to the specified path."""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except Exception as e:
            logging.error(f"Failed to download cover art from {url}: {e}")
            return False
