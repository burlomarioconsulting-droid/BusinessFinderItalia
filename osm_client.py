"""
Business Finder Italia
Client OpenStreetMap tramite Overpass API.
"""

from __future__ import annotations

import time
from typing import Any

import requests

from config import OVERPASS_SERVERS, REQUEST_TIMEOUT, RETRY


class OverpassClient:
    """Gestisce le ricerche tramite i server Overpass."""

    ADMIN_LEVELS = {
        "comune": "8",
        "provincia": "6",
        "regione": "4",
    }

    def __init__(self) -> None:
        self.servers = OVERPASS_SERVERS

    @staticmethod
    def _escape(value: str) -> str:
        """Protegge i caratteri speciali usati nella query."""
        return value.replace("\\", "\\\\").replace('"', '\\"')

    def build_query(
        self,
        location: str,
        search_mode: str,
        key: str,
        value: str,
    ) -> str:
        """Costruisce la query per comune, provincia o regione."""

        mode = search_mode.strip().lower()

        if mode not in self.ADMIN_LEVELS:
            raise ValueError(
                "SEARCH_MODE non valido. "
                "Usa 'comune', 'provincia' oppure 'regione'."
            )

        admin_level = self.ADMIN_LEVELS[mode]

        safe_location = self._escape(location.strip())
        safe_key = self._escape(key.strip())
        safe_value = self._escape(value.strip())

        # La ricerca con espressione regolare permette di trovare anche
        # denominazioni come "Città metropolitana di Milano".
        area_pattern = f".*{safe_location}.*"

        return f"""
[out:json][timeout:{REQUEST_TIMEOUT}];

relation
  ["boundary"="administrative"]
  ["admin_level"="{admin_level}"]
  ["name"~"{area_pattern}", i];

map_to_area -> .searchArea;

(
  node["{safe_key}"="{safe_value}"](area.searchArea);
  way["{safe_key}"="{safe_value}"](area.searchArea);
  relation["{safe_key}"="{safe_value}"](area.searchArea);
);

out center tags;
"""

    def search(
        self,
        location: str,
        search_mode: str,
        key: str,
        value: str,
    ) -> list[dict[str, Any]]:
        """Esegue la richiesta e restituisce gli elementi trovati."""

        query = self.build_query(
            location=location,
            search_mode=search_mode,
            key=key,
            value=value,
        )

        last_error: Exception | None = None

        for server in self.servers:

            for attempt in range(1, RETRY + 1):

                try:
                    response = requests.post(
                        server,
                        data={"data": query},
                        headers={
                            "User-Agent": (
                                "BusinessFinderItalia/2.0 "
                                "(OpenStreetMap business search)"
                            )
                        },
                        timeout=REQUEST_TIMEOUT,
                    )

                    if response.status_code == 429:
                        wait_seconds = attempt * 10
                        print(
                            f"  Troppe richieste. "
                            f"Attendo {wait_seconds} secondi..."
                        )
                        time.sleep(wait_seconds)
                        continue

                    if response.status_code in (502, 503, 504):
                        wait_seconds = attempt * 5
                        print(
                            f"  Server temporaneamente occupato. "
                            f"Attendo {wait_seconds} secondi..."
                        )
                        time.sleep(wait_seconds)
                        continue

                    response.raise_for_status()

                    data = response.json()

                    return data.get("elements", [])

                except (
                    requests.Timeout,
                    requests.ConnectionError,
                    requests.HTTPError,
                    ValueError,
                ) as error:

                    last_error = error

                    print(
                        f"  Tentativo {attempt}/{RETRY} fallito "
                        f"su {server}"
                    )

                    time.sleep(attempt * 3)

        raise RuntimeError(
            "Nessun server Overpass disponibile. "
            f"Ultimo errore: {last_error}"
        )
