"""
Business Finder Italia
Client OpenStreetMap (Overpass)
"""

from __future__ import annotations

import random
import time
import requests

from config import (
    OVERPASS_SERVERS,
    REQUEST_TIMEOUT,
    RETRY,
)


class OverpassClient:

    def __init__(self):
        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": "BusinessFinderItalia/3.0"
            }
        )

    def build_query(self, location, mode, key, value):

        admin = {
            "comune": "8",
            "provincia": "6",
            "regione": "4",
        }[mode]

        return f"""
[out:json][timeout:{REQUEST_TIMEOUT}];

relation
["boundary"="administrative"]
["admin_level"="{admin}"]
["name"="{location}"];

map_to_area->.searchArea;

(
node["{key}"="{value}"](area.searchArea);
way["{key}"="{value}"](area.searchArea);
relation["{key}"="{value}"](area.searchArea);
);

out center tags;
"""

    def search(self, location, mode, key, value):

        query = self.build_query(
            location,
            mode,
            key,
            value
        )

        servers = OVERPASS_SERVERS.copy()
        random.shuffle(servers)

        last_error = None

        for server in servers:

            for attempt in range(RETRY):

                try:

                    response = self.session.post(
                        server,
                        data=query.encode("utf-8"),
                        headers={
                            "Content-Type": "text/plain"
                        },
                        timeout=REQUEST_TIMEOUT
                    )

                    if response.status_code == 429:

                        wait = 10 * (attempt + 1)

                        print(
                            f"Troppe richieste. Attendo {wait} secondi..."
                        )

                        time.sleep(wait)

                        continue

                    if response.status_code in (
                        500,
                        502,
                        503,
                        504,
                    ):

                        wait = 5 * (attempt + 1)

                        print(
                            f"Server temporaneamente occupato. Attendo {wait} secondi..."
                        )

                        time.sleep(wait)

                        continue

                    response.raise_for_status()

                    data = response.json()

                    return data.get(
                        "elements",
                        []
                    )

                except Exception as e:

                    last_error = e

                    time.sleep(5)

        raise RuntimeError(
            f"Nessun server Overpass disponibile.\nUltimo errore: {last_error}"
        )
