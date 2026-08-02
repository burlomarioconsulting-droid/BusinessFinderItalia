"""
Business Finder Italia
Configurazione generale del progetto.
"""

# ==========================================================
# IMPOSTAZIONI PREDEFINITE
# ==========================================================

# Questi valori vengono usati da main.py.
# Nell'app Streamlit la località viene scelta direttamente dall'utente.

LOCATION = "Milano"

# Valori disponibili:
# "comune"
# "provincia"
# "regione"

SEARCH_MODE = "provincia"


# ==========================================================
# ESPORTAZIONE
# ==========================================================

OUTPUT_FOLDER = "output"

OUTPUT_EXCEL = True
OUTPUT_CSV = True
OUTPUT_JSON = True


# ==========================================================
# RETE E TENTATIVI
# ==========================================================

# Tempo massimo concesso a una richiesta Overpass.
REQUEST_TIMEOUT = 180

# Numero di tentativi per ciascun server.
RETRY = 4

# Pausa tra una query e la successiva.
PAUSE_SECONDS = 6


# ==========================================================
# SERVER OVERPASS
# ==========================================================

OVERPASS_SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]
