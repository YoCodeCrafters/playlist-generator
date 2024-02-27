import re
from difflib import get_close_matches
from urllib.parse import urlparse
from typing import List, Dict
from datetime import datetime
from jinja2 import Template
import json
import os

PLAYLISTS_DIR = "playlists"
RESOURCES_DIR = "helpers/res"


def get_base_url(url: str) -> str:
    parsed_url = urlparse(url)
    base_url = parsed_url.scheme + "://" + parsed_url.netloc
    return base_url


def generate_playlist(service_name: str, data: List[Dict[str, Dict]]) -> str:
    playlist_splitted = ["#EXTM3U"]

    with open(os.path.join(RESOURCES_DIR, "playlist-header.txt"), encoding="utf-8") as file:
        header_template = Template(file.read())

    current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    playlist_splitted.append("\n" + header_template.render(
        time_of_update=current_time,
        service_name=service_name,
        num_of_channels=str(len(data))
    ) + "\n")

    for channel in data:
        channel_name = channel.get("name")
        channel_logo = channel.get("logo")
        channel_group = channel.get("group")
        channel_url = channel.get("stream-url")
        channel_headers = channel.get("headers")

        playlist_splitted.append(
            f'#EXTINF:-1 tvg-name="{channel_name}" tvg-logo="{channel_logo}" group-title="{channel_group}",{channel_name}')

        channel_referer = channel_headers.get("referer")
        if channel_referer:
            playlist_splitted.append(
                f"#EXTVLCOPT:http-referrer={channel_referer}")

            channel_headers.pop("referer")

        channel_UA = channel_headers.get("user-agent")
        if channel_UA:
            playlist_splitted.append(
                f"#EXTVLCOPT:http-user-agent={channel_UA}")

            channel_headers.pop("user-agent")

        if channel_headers:
            playlist_splitted.append("EXTHTTP:" + json.dumps(channel_headers))

        playlist_splitted.append(channel_url)

        playlist_splitted.append("")

    playlist = "\n".join(playlist_splitted)
    return playlist


def get_logo_url(channel_name: str) -> str:
    logo_data = json.load(
        open(os.path.join("helpers", "res", "logo-fraudiay.json"), encoding="utf-8"))

    logo_tree = logo_data.get("tree", [])

    logo_paths = [logo.get("path", "")
                  for logo in logo_tree if ".png" in logo.get("path", "")]
    logo_names = [logo_path.split(
        "/")[-1] if "/" in logo_path else "" for logo_path in logo_paths]

    channel_logo_matches = get_close_matches(
        channel_name, logo_names, cutoff=0.5)
    channel_logo_path = logo_paths[logo_names.index(
        channel_logo_matches[0])] if channel_logo_matches else None

    if channel_logo_path:
        return f"https://raw.githubusercontent.com/fraudiay79/logos/master/{channel_logo_path}"

    return None
