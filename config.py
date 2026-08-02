"""
Business Finder Italia
Configurazione generale
"""

# Località da cercare
LOCATION = "Milano"

# Modalità disponibili:
# "comune"
# "provincia"
# "regione"
SEARCH_MODE = "comune"

OUTPUT_FOLDER = "output"

OUTPUT_EXCEL = True
OUTPUT_CSV = True
OUTPUT_JSON = True

REQUEST_TIMEOUT = 60
RETRY = 3
PAUSE_SECONDS = 5

OVERPASS_SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
]
