"""
Business Finder Italia
Parser dei dati OpenStreetMap
"""

from typing import Dict, List


def _address(tags: Dict) -> tuple[str, str, str]:
    """
    Restituisce:
    indirizzo, CAP, città
    """

    street = tags.get("addr:street", "")
    number = tags.get("addr:housenumber", "")

    if street and number:
        address = f"{street}, {number}"
    else:
        address = street or number

    postcode = tags.get("addr:postcode", "")
    city = tags.get("addr:city", "")

    return address, postcode, city


def parse_elements(elements: List[Dict], settore: str) -> List[Dict]:

    risultati = []

    for element in elements:

        tags = element.get("tags", {})

        indirizzo, cap, citta = _address(tags)

        risultati.append({

            "Nome attività": tags.get("name", ""),

            "Settore": settore,

            "Categoria OSM": (
                tags.get("amenity")
                or tags.get("shop")
                or tags.get("craft")
                or tags.get("office")
                or tags.get("tourism")
                or tags.get("landuse")
                or ""
            ),

            "Indirizzo": indirizzo,

            "CAP": cap,

            "Città": citta,

            "Provincia": "",

            "Telefono": tags.get("phone", ""),

            "Email": tags.get("email", ""),

            "Sito web": tags.get("website", ""),

            "Stato contatto": ""

        })

    return risultati
