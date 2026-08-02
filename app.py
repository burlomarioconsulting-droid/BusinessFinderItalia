"""
Business Finder Italia
Interfaccia web Streamlit.
"""

from __future__ import annotations

import io
import json
import time
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from categories import CATEGORIES
from config import PAUSE_SECONDS
from osm_client import OverpassClient
from parser import parse_elements


# ==========================================================
# CONFIGURAZIONE PAGINA
# ==========================================================

st.set_page_config(
    page_title="Business Finder Italia",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================================
# STILE GRAFICO
# ==========================================================

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }

        [data-testid="stSidebar"] {
            min-width: 310px;
            max-width: 310px;
        }

        .business-subtitle {
            font-size: 1.05rem;
            color: #52606d;
            margin-top: -0.5rem;
            margin-bottom: 1.5rem;
        }

        .small-note {
            color: #6b7280;
            font-size: 0.88rem;
        }

        div[data-testid="stMetric"] {
            border: 1px solid #e5e7eb;
            padding: 14px;
            border-radius: 12px;
            background-color: #ffffff;
        }

        div.stButton > button {
            font-weight: 700;
            border-radius: 9px;
        }

        div.stDownloadButton > button {
            width: 100%;
            border-radius: 9px;
            font-weight: 700;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# FUNZIONI DI SUPPORTO
# ==========================================================

def element_identifier(
    element: dict[str, Any],
) -> tuple[Any, Any]:
    """
    Crea un identificativo univoco per ogni elemento OSM.
    """

    return (
        element.get("type", ""),
        element.get("id", ""),
    )


def clean_text_series(
    series: pd.Series,
) -> pd.Series:
    """
    Converte una colonna in testo pulito.
    """

    return (
        series
        .fillna("")
        .astype(str)
        .str.strip()
    )


def prepare_dataframe(
    records: list[dict[str, Any]],
) -> pd.DataFrame:
    """
    Trasforma i risultati in una tabella pulita.
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

    for column in columns:
        if column not in df.columns:
            df[column] = ""

    df = df[columns].copy()

    for column in columns:
        df[column] = clean_text_series(df[column])

    # Elimina righe senza nome.
    df = df[
        df["Nome attività"] != ""
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

    # Ordina per settore e nome.
    df = df.sort_values(
        by=[
            "Settore",
            "Nome attività",
        ],
        na_position="last",
    )

    return df.reset_index(drop=True)


def dataframe_to_excel(
    df: pd.DataFrame,
) -> bytes:
    """
    Crea un file Excel formattato in memoria.
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

        for column_cells in worksheet.columns:

            maximum_length = 0
            column_letter = column_cells[0].column_letter

            for cell in column_cells:

                value = (
                    ""
                    if cell.value is None
                    else str(cell.value)
                )

                maximum_length = max(
                    maximum_length,
                    len(value),
                )

            worksheet.column_dimensions[
                column_letter
            ].width = min(
                maximum_length + 2,
                45,
            )

    output.seek(0)

    return output.getvalue()


def safe_filename(
    value: str,
) -> str:
    """
    Rende il nome della località adatto a un file.
    """

    cleaned = (
        value.strip()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
    )

    return cleaned or "Italia"


def get_category_labels() -> list[str]:
    """
    Restituisce i nomi delle categorie disponibili.
    """

    return [
        category["label"]
        for category in CATEGORIES
    ]


def filter_records_with_contacts(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Mantiene solo le aziende con almeno un contatto.
    """

    has_phone = (
        clean_text_series(df["Telefono"]) != ""
    )

    has_email = (
        clean_text_series(df["Email"]) != ""
    )

    has_website = (
        clean_text_series(df["Sito web"]) != ""
    )

    return df[
        has_phone
        | has_email
        | has_website
    ].copy()


def search_businesses(
    location: str,
    search_mode: str,
    selected_labels: list[str],
) -> tuple[pd.DataFrame, list[str]]:
    """
    Cerca le attività delle categorie selezionate.
    """

    client = OverpassClient()

    all_records: list[dict[str, Any]] = []
    warnings: list[str] = []

    selected_categories = [
        category
        for category in CATEGORIES
        if category["label"] in selected_labels
    ]

    total_categories = len(selected_categories)

    progress_bar = st.progress(0)
    status_box = st.empty()
    results_box = st.empty()

    for category_index, category in enumerate(
        selected_categories,
        start=1,
    ):

        label = category["label"]
        queries = category.get("queries", [])

        status_box.info(
            f"Ricerca in corso: {label} "
            f"({category_index}/{total_categories})"
        )

        category_elements: list[dict[str, Any]] = []
        seen_elements: set[tuple[Any, Any]] = set()

        for query_data in queries:

            key = query_data["key"]
            value = query_data["value"]

            try:

                # IMPORTANTE:
                # osm_client.py usa il parametro "mode",
                # non "search_mode".
                elements = client.search(
                    location=location,
                    mode=search_mode,
                    key=key,
                    value=value,
                )

                for element in elements:

                    identifier = element_identifier(
                        element
                    )

                    if identifier in seen_elements:
                        continue

                    seen_elements.add(identifier)
                    category_elements.append(element)

            except Exception as error:

                warnings.append(
                    f"{label}: la query "
                    f"{key}={value} non è stata completata. "
                    f"Dettaglio: {error}"
                )

            if PAUSE_SECONDS > 0:
                time.sleep(PAUSE_SECONDS)

        category_records = parse_elements(
            category_elements,
            label,
        )

        all_records.extend(category_records)

        results_box.write(
            f"**{label}:** "
            f"{len(category_records)} attività trovate"
        )

        progress_bar.progress(
            category_index / total_categories
        )

    status_box.success(
        "Ricerca completata."
    )

    return (
        prepare_dataframe(all_records),
        warnings,
    )


# ==========================================================
# LOGO E INTESTAZIONE
# ==========================================================

logo_candidates = [
    Path("logo.png"),
    Path("assets/logo.png"),
    Path("logo.jpg"),
    Path("assets/logo.jpg"),
]

logo_path = next(
    (
        path
        for path in logo_candidates
        if path.exists()
    ),
    None,
)

if logo_path is not None:

    logo_column, title_column = st.columns(
        [1, 4],
        vertical_alignment="center",
    )

    with logo_column:
        st.image(
            str(logo_path),
            use_container_width=True,
        )

    with title_column:
        st.title("Business Finder Italia")

else:

    st.title("🔎 Business Finder Italia")

st.markdown(
    """
    <div class="business-subtitle">
        Cerca attività commerciali per comune, provincia
        o regione ed esporta i risultati.
    </div>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# BARRA LATERALE
# ==========================================================

with st.sidebar:

    st.header("Impostazioni")

    location = st.text_input(
        "Località",
        value="Torino",
        placeholder="Esempio: Torino, Milano, Lombardia",
        help=(
            "Scrivi il nome del comune, della provincia "
            "o della regione."
        ),
    )

    search_mode = st.radio(
        "Area di ricerca",
        options=[
            "comune",
            "provincia",
            "regione",
        ],
        format_func=lambda mode: {
            "comune": "Comune",
            "provincia": (
                "Provincia / Città metropolitana"
            ),
            "regione": "Regione",
        }[mode],
    )

    st.divider()

    category_labels = get_category_labels()

    selected_labels = st.multiselect(
        "Categorie",
        options=category_labels,
        default=category_labels,
        placeholder="Seleziona una o più categorie",
    )

    st.divider()

    start_search = st.button(
        "🔍 Avvia ricerca",
        type="primary",
        use_container_width=True,
    )

    st.markdown(
        """
        <div class="small-note">
            I risultati dipendono dai dati disponibili
            su OpenStreetMap e dalla disponibilità
            dei server pubblici Overpass.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==========================================================
# AVVIO RICERCA
# ==========================================================

if start_search:

    clean_location = location.strip()

    if not clean_location:

        st.error(
            "Inserisci una località."
        )

    elif not selected_labels:

        st.error(
            "Seleziona almeno una categoria."
        )

    else:

        st.session_state.pop(
            "results_df",
            None,
        )

        st.session_state.pop(
            "search_warnings",
            None,
        )

        with st.spinner(
            "Ricerca delle attività in corso..."
        ):

            results_df, search_warnings = (
                search_businesses(
                    location=clean_location,
                    search_mode=search_mode,
                    selected_labels=selected_labels,
                )
            )

        st.session_state["results_df"] = results_df
        st.session_state["search_warnings"] = (
            search_warnings
        )

        st.session_state["location"] = clean_location
        st.session_state["search_mode"] = search_mode


# ==========================================================
# RISULTATI
# ==========================================================

if "results_df" in st.session_state:

    df = st.session_state["results_df"]

    current_location = st.session_state.get(
        "location",
        "Italia",
    )

    current_mode = st.session_state.get(
        "search_mode",
        "comune",
    )

    search_warnings = st.session_state.get(
        "search_warnings",
        [],
    )

    st.divider()
    st.subheader("Risultati")

    if df.empty:

        st.warning(
            "Nessuna attività trovata. "
            "Controlla la località, la modalità scelta "
            "oppure riprova selezionando una sola categoria."
        )

    else:

        metric_col1, metric_col2, metric_col3, metric_col4 = (
            st.columns(4)
        )

        total_records = len(df)

        records_with_phone = int(
            (
                clean_text_series(
                    df["Telefono"]
                ) != ""
            ).sum()
        )

        records_with_email = int(
            (
                clean_text_series(
                    df["Email"]
                ) != ""
            ).sum()
        )

        records_with_website = int(
            (
                clean_text_series(
                    df["Sito web"]
                ) != ""
            ).sum()
        )

        metric_col1.metric(
            "Attività trovate",
            total_records,
        )

        metric_col2.metric(
            "Con telefono",
            records_with_phone,
        )

        metric_col3.metric(
            "Con email",
            records_with_email,
        )

        metric_col4.metric(
            "Con sito web",
            records_with_website,
        )

        st.divider()

        filter_contact = st.checkbox(
            "Mostra solo attività con almeno un contatto",
            value=False,
        )

        displayed_df = df.copy()

        if filter_contact:

            displayed_df = (
                filter_records_with_contacts(
                    displayed_df
                )
            )

        st.caption(
            f"Righe visualizzate: {len(displayed_df)}"
        )

        st.dataframe(
            displayed_df,
            use_container_width=True,
            hide_index=True,
            height=520,
        )

        if search_warnings:

            with st.expander(
                f"Avvisi della ricerca "
                f"({len(search_warnings)})"
            ):

                unique_warnings = list(
                    dict.fromkeys(search_warnings)
                )

                for warning in unique_warnings:
                    st.warning(warning)


        # ==================================================
        # DOWNLOAD
        # ==================================================

        st.divider()
        st.subheader("Download")

        filename_location = safe_filename(
            current_location
        )

        filename_base = (
            f"BusinessFinder_"
            f"{filename_location}_"
            f"{current_mode}"
        )

        excel_data = dataframe_to_excel(
            displayed_df
        )

        csv_data = displayed_df.to_csv(
            index=False,
            encoding="utf-8-sig",
        ).encode("utf-8-sig")

        json_data = json.dumps(
            displayed_df
            .fillna("")
            .to_dict(orient="records"),
            ensure_ascii=False,
            indent=4,
        ).encode("utf-8")

        download_col1, download_col2, download_col3 = (
            st.columns(3)
        )

        with download_col1:

            st.download_button(
                label="📊 Scarica Excel",
                data=excel_data,
                file_name=f"{filename_base}.xlsx",
                mime=(
                    "application/vnd.openxmlformats-"
                    "officedocument.spreadsheetml.sheet"
                ),
                use_container_width=True,
            )

        with download_col2:

            st.download_button(
                label="📄 Scarica CSV",
                data=csv_data,
                file_name=f"{filename_base}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with download_col3:

            st.download_button(
                label="📋 Scarica JSON",
                data=json_data,
                file_name=f"{filename_base}.json",
                mime="application/json",
                use_container_width=True,
            )
