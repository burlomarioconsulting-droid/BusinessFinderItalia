"""
Business Finder Italia
Esportazione dati
"""

import pandas as pd
from pathlib import Path


def export_results(records, output_folder="output", filename="BusinessFinder"):

    Path(output_folder).mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(records)

    # Elimina record senza nome
    df = df[df["Nome attività"].fillna("").str.strip() != ""]

    # Elimina duplicati
    df = df.drop_duplicates(
        subset=["Nome attività", "Telefono", "Indirizzo"],
        keep="first"
    )

    excel_file = Path(output_folder) / f"{filename}.xlsx"
    csv_file = Path(output_folder) / f"{filename}.csv"
    json_file = Path(output_folder) / f"{filename}.json"

    df.to_excel(excel_file, index=False)
    df.to_csv(csv_file, index=False, encoding="utf-8-sig")
    df.to_json(
        json_file,
        orient="records",
        force_ascii=False,
        indent=4
    )

    print(f"Excel: {excel_file}")
    print(f"CSV: {csv_file}")
    print(f"JSON: {json_file}")

    return df
