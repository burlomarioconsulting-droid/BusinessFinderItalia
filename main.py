"""
Business Finder Italia
Programma principale.
"""

import time

from config import LOCATION, SEARCH_MODE, PAUSE_SECONDS
from categories import CATEGORIES
from osm_client import OverpassClient
from parser import parse_elements
from exporter import export_results


def element_identifier(element):
    """
    Crea un identificativo per evitare duplicati provenienti
    da più query della stessa categoria.
    """
    return (
        element.get("type", ""),
        element.get("id", ""),
    )


def main():

    client = OverpassClient()
    all_records = []

    print("=" * 55)
    print("BUSINESS FINDER ITALIA")
    print("=" * 55)
    print(f"Località: {LOCATION}")
    print(f"Modalità: {SEARCH_MODE}")
    print()

    for category in CATEGORIES:

        label = category["label"]
        queries = category["queries"]

        print(f"Cerco {label}...")

        category_elements = []
        seen_elements = set()

        for query_data in queries:

            key = query_data["key"]
            value = query_data["value"]

            try:
                elements = client.search(
                    LOCATION,
                    SEARCH_MODE,
                    key,
                    value,
                )

                for element in elements:
                    identifier = element_identifier(element)

                    if identifier not in seen_elements:
                        seen_elements.add(identifier)
                        category_elements.append(element)

            except Exception as error:
                print(
                    f"  Query {key}={value} non completata: "
                    f"{error}"
                )

            # Riduce il rischio di errori 429.
            time.sleep(PAUSE_SECONDS)

        records = parse_elements(category_elements, label)
        all_records.extend(records)

        print(f"  Trovati: {len(records)}")

    print()
    print("Esporto i risultati...")

    export_results(
        all_records,
        filename=f"BusinessFinder_{LOCATION}_{SEARCH_MODE}",
    )

    print("Operazione completata.")


if __name__ == "__main__":
    main()
