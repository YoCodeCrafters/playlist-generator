from urllib.parse import urlparse
from bs4 import BeautifulSoup
from . import BaseService
import requests
import re


class DaddyHD(BaseService):
    def __init__(self) -> None:
        super().__init__(
            SERVICE_NAME="DaddyHD",
            SERVICE_URL="https://dlhd.sx/24-7-channels.php",
        )

    def _get_data(self) -> dict:
        soup = BeautifulSoup(self._get_src(), "html.parser")
        config_data = self._get_config_data()

        channels_data = []

        channels_divs = soup.select("div.grid-item")
        for channel_div in channels_divs:
            channel_slug = channel_div.select_one("a").get("href").strip()

            FIRST_INDEX = channel_slug.find("stream-") + len("stream-")
            LAST_INDEX = channel_slug.find(".php")

            channel_id = channel_slug[FIRST_INDEX:LAST_INDEX]
            channel_name = channel_div.text.strip()

            if "18+" in channel_name:
                continue

            channels_data.append({
                "name": channel_name,
                "logo": "",
                "group": "DaddyHD",
                "stream-url": config_data.get("endpoint").replace("STREAM-ID", channel_id),
                "headers": {
                    "referer": config_data.get("referer"),
                    "user-agent": self.USER_AGENT
                }
            })

        return channels_data

    def _get_config_data(self) -> dict:
        EMBED_URL = "https://dlhd.sx/embed/stream-1.php"
        parsed_embed = urlparse(EMBED_URL)

        response = requests.get(EMBED_URL)
        soup = BeautifulSoup(response.text, "html.parser")

        iframe_url = soup.find("iframe", {"id": "thatframe"})["src"]
        iframe_parsed = urlparse(iframe_url)
        iframe_response = requests.get(iframe_url, headers={
            "Referer": f"{parsed_embed.scheme}://{parsed_embed.netloc}/"})
        iframe_source = iframe_response.text
        iframe_pattern = r"source:'(https:\/\/[^\s']+)'"

        matches = re.findall(iframe_pattern, iframe_source)

        config_endpoint = matches[1].replace("1", "STREAM-ID")

        config = {
            "endpoint": config_endpoint,
            "referer": f"{iframe_parsed.scheme}://{iframe_parsed.netloc}/"
        }

        return config
