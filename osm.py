"""
Business Finder Italia
Client OpenStreetMap (Overpass)
"""

from __future__ import annotations

import time
import requests

from config import OVERPASS_SERVERS, REQUEST_TIMEOUT, RETRY


class OverpassClient:
    def __init__(self):
        self.servers = OVERPASS_SERVERS

    def build_query(self, city: str, key: str, value: str) -> str:
        return f"""
[out:json][timeout:60];

area["name"="{city}"]->.searchArea;

(
  node["{key}"="{value}"](area.searchArea);
  way["{key}"="{value}"](area.searchArea);
  relation["{key}"="{value}"](area.searchArea);
);

out center tags;
"""

    def search(self, city: str, key: str, value: str):
        query = self.build_query(city, key, value)

        last_error = None

        for server in self.servers:
            for attempt in range(RETRY):
                try:
                    response = requests.post(
                        server,
                        data=query.encode("utf-8"),
                        headers={
                            "User-Agent": "BusinessFinderItalia/2.0",
                            "Content-Type": "text/plain"
                        },
                        timeout=REQUEST_TIMEOUT
                    )

                    response.raise_for_status()

                    data = response.json()

                    return data.get("elements", [])

                except Exception as e:
                    last_error = e
                    time.sleep(3)

        raise last_error
