"""
Business Finder Italia
Interfaccia web Streamlit.
"""

from __future__ import annotations

import io
import json
import time

import pandas as pd
import streamlit as st

from categories import CATEGORIES
from osm_client import OverpassClient
from parser import parse_elements


st.set_page_config(
    page_title="Business Finder Italia",
    page_icon="🏢",
    layout="wide",
)


def element_identifier(element: dict) -> tuple:
    """
    Identifica un elemento OpenStreetMap per evitare duplicati
    provenienti da più query della stessa categoria.
    """
    return (
        element.get("type", ""),
        element.get("id", ""),
    )


def prepare_dataframe(records: list[dict]) -> pd.DataFrame:
    """
    Trasforma i record in una tabella pulita.
    """

    columns = [
        "Nome attività",
        "Settore",
        "Categoria OSM",
        "Indirizzo",
        "CAP",
        "Città",
        "Provincia",
        "Telefono",
        "Email",
        "Sito web",
        "Stato contatto",
    ]

    if not records:
        return pd.DataFrame(columns=columns)

    df = pd.DataFrame(records)

    # Aggiunge eventuali colonne mancanti.
    for column in columns:
        if column not in df.columns:
            df[column] = ""

    # Mantiene l’ordine desiderato.
    df = df[columns]

    # Rimuove le attività senza nome.
    df["Nome attività"] = df["Nome attività"].fillna("").astype(str)

    df = df[
        df["Nome attività"].str.strip() != ""
    ].copy()

    # Elimina i duplicati.
    df = df.drop_duplicates(
        subset=[
            "Nome attività",
            "Telefono",
            "Indirizzo",
        ],
        keep="first",
    )

    # Ordina la tabella.
    df = df.sort_values(
        by=["Settore", "Nome attività"],
        na_position="last",
    )

    return df.reset_index(drop=True)


def dataframe_to_excel(df: pd.DataFrame) -> bytes:
    """
    Crea il file Excel in memoria.
    """

    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl",
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Attività",
        )

        worksheet = writer.sheets["Attività"]

        worksheet.freeze_panes = "A2"
        worksheet.auto_filter.ref = worksheet.dimensions

        # Adatta la larghezza delle colonne.
        for column_cells in worksheet.columns:

            max_length = 0
            column_letter = column_cells[0].column_letter

            for cell in column_cells:

                value = "" if cell.value is None else str(cell.value)
                max_length = max(max_length, len(value))

            worksheet.column_dimensions[column_letter].width = min(
                max_length + 2,
                45,
            )

    output.seek(0)

    return output.getvalue()


def search_businesses(
    location: str,
    search_mode: str,
    selected_labels: list[str],
) -> pd.DataFrame:
    """
    Esegue la ricerca per le categorie selezionate.
    """

    client = OverpassClient()
    all_records = []

    selected_categories = [
        category
        for category in CATEGORIES
        if category["label"] in selected_labels
    ]

    progress_bar = st.progress(0)

    status_box = st.empty()

    total_categories = len(selected_categories)

    for category_index, category in enumerate(
        selected_categories,
        start=1,
    ):

        label = category["label"]
        queries = category["queries"]

        status_box.info(
            f"Ricerca in corso: {label} "
            f"({category_index}/{total_categories})"
        )

        category_elements = []
        seen_elements = set()

        for query_data in queries:

            key = query_data["key"]
            value = query_data["value"]

            try:
                elements = client.search(
                    location=location,
                    search_mode=search_mode,
                    key=key,
                    value=value,
                )

                for element in elements:

                    identifier = element_identifier(element)

                    if identifier not in seen_elements:

                        seen_elements.add(identifier)
                        category_elements.append(element)

            except Exception as error:

                st.warning(
                    f"{label}: la query "
                    f"{key}={value} non è stata completata.\n\n"
                    f"Dettaglio: {error}"
                )

            # Piccola pausa per non sovraccaricare Overpass.
            time.sleep(2)

        records = parse_elements(
            category_elements,
            label,
        )

        all_records.extend(records)

        progress_bar.progress(
            category_index / total_categories
        )

    status_box.success("Ricerca completata.")

    return prepare_dataframe(all_records)


st.title("🏢 Business Finder Italia")

st.write(
    "Cerca attività commerciali per comune, provincia "
    "o regione ed esporta i risultati."
)

with st.sidebar:

    st.header("Impostazioni")

    location = st.text_input(
        "Località",
        value="Milano",
        placeholder="Esempio: Milano",
    )

    search_mode = st.radio(
        "Area di ricerca",
        options=[
            "comune",
            "provincia",
            "regione",
        ],
        format_func=lambda value: {
            "comune": "Comune",
            "provincia": "Provincia / Città metropolitana",
            "regione": "Regione",
        }[value],
    )

    category_labels = [
        category["label"]
        for category in CATEGORIES
    ]

    selected_labels = st.multiselect(
        "Categorie",
        options=category_labels,
        default=category_labels,
    )

    start_search = st.button(
        "🔍 Avvia ricerca",
        type="primary",
        use_container_width=True,
    )


if start_search:

    if not location.strip():

        st.error("Inserisci una località.")

    elif not selected_labels:

        st.error("Seleziona almeno una categoria.")

    else:

        with st.spinner(
            "Ricerca delle attività in corso..."
        ):

            results_df = search_businesses(
                location=location.strip(),
                search_mode=search_mode,
                selected_labels=selected_labels,
            )

        st.session_state["results_df"] = results_df
        st.session_state["location"] = location.strip()
        st.session_state["search_mode"] = search_mode


if "results_df" in st.session_state:

    df = st.session_state["results_df"]

    current_location = st.session_state["location"]
    current_mode = st.session_state["search_mode"]

    st.subheader("Risultati")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Attività trovate",
        len(df),
    )

    col2.metric(
        "Con telefono",
        int(
            df["Telefono"]
            .fillna("")
            .astype(str)
            .str.strip()
            .ne("")
            .sum()
        ),
    )

    col3.metric(
        "Con sito web",
        int(
            df["Sito web"]
            .fillna("")
            .astype(str)
            .str.strip()
            .ne("")
            .sum()
        ),
    )

    filter_contact = st.checkbox(
        "Mostra solo attività con almeno un contatto",
        value=False,
    )

    displayed_df = df.copy()

    if filter_contact:

        has_phone = (
            displayed_df["Telefono"]
            .fillna("")
            .astype(str)
            .str.strip()
            .ne("")
        )

        has_email = (
            displayed_df["Email"]
            .fillna("")
            .astype(str)
            .str.strip()
            .ne("")
        )

        has_website = (
            displayed_df["Sito web"]
            .fillna("")
            .astype(str)
            .str.strip()
            .ne("")
        )

        displayed_df = displayed_df[
            has_phone | has_email | has_website
        ]

    st.dataframe(
        displayed_df,
        use_container_width=True,
        hide_index=True,
    )

    safe_location = current_location.replace(" ", "_")

    filename_base = (
        f"BusinessFinder_"
        f"{safe_location}_"
        f"{current_mode}"
    )

    excel_data = dataframe_to_excel(displayed_df)

    csv_data = displayed_df.to_csv(
        index=False,
        encoding="utf-8-sig",
    ).encode("utf-8-sig")

    json_data = json.dumps(
        displayed_df.fillna("").to_dict(
            orient="records"
        ),
        ensure_ascii=False,
        indent=4,
    ).encode("utf-8")

    st.subheader("Download")

    download_col1, download_col2, download_col3 = st.columns(3)

    download_col1.download_button(
        label="📊 Scarica Excel",
        data=excel_data,
        file_name=f"{filename_base}.xlsx",
        mime=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        ),
        use_container_width=True,
    )

    download_col2.download_button(
        label="📄 Scarica CSV",
        data=csv_data,
        file_name=f"{filename_base}.csv",
        mime="text/csv",
        use_container_width=True,
    )

    download_col3.download_button(
        label="📋 Scarica JSON",
        data=json_data,
        file_name=f"{filename_base}.json",
        mime="application/json",
        use_container_width=True,
    )
