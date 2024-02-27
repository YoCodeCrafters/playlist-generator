from helpers import PLAYLISTS_DIR, generate_playlist
import requests
import os


class BaseService:
    def __init__(self, SERVICE_NAME: str, SERVICE_URL: str) -> None:
        self.SERVICE_URL = SERVICE_URL
        self.SERVICE_NAME = SERVICE_NAME
        self.PLAYLIST_PATH = os.path.join(
            PLAYLISTS_DIR, self.SERVICE_NAME.lower() + ".m3u")

        self.requests_session = requests.Session()

        self.USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        self.requests_session.headers = {
            "User-Agent": self.USER_AGENT
        }

    def update(self) -> None:
        playlist_str = self._get_playlist()

        os.makedirs(os.path.dirname(self.PLAYLIST_PATH), exist_ok=True)

        with open(self.PLAYLIST_PATH, "w", encoding="utf-8") as file:
            file.write(playlist_str)

    def _get_playlist(self) -> str:
        channels_data = self._get_data()
        return generate_playlist(self.SERVICE_NAME, channels_data)

    def _get_src(self) -> str:
        response = self.requests_session.get(self.SERVICE_URL)
        source_code = response.text

        return source_code
