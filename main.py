"""
Business Finder Italia
Programma principale
"""

from config import LOCATION, SEARCH_MODE
from categories import CATEGORIES
from osm_client import OverpassClient
from parser import parse_elements
from exporter import export_results


def main():

    client = OverpassClient()

    all_records = []

    print("=" * 50)
    print("BUSINESS FINDER ITALIA")
    print("=" * 50)
    print(f"Località: {LOCATION}")
    print(f"Modalità: {SEARCH_MODE}")
    print()

    for category in CATEGORIES:

        label = category["label"]
        key = category["key"]
        value = category["value"]

        print(f"Cerco {label}...")

        try:

            elements = client.search(
                LOCATION,
                SEARCH_MODE,
                key,
                value
            )

            records = parse_elements(elements, label)

            all_records.extend(records)

            print(f"  Trovati: {len(records)}")

        except Exception as e:

            print(f"  Errore: {e}")

    print()
    print("Esporto i risultati...")

    export_results(
        all_records,
        filename=f"BusinessFinder_{LOCATION}_{SEARCH_MODE}"
    )

    print("Operazione completata.")


if __name__ == "__main__":
    main()
