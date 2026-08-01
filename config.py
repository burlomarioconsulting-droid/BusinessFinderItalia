"""
Business Finder Italia
Configurazione generale
"""

# ==========================
# CITTÀ
# ==========================

CITY = "Milano"

# ==========================
# OUTPUT
# ==========================

OUTPUT_FOLDER = "output"

OUTPUT_EXCEL = True
OUTPUT_CSV = True
OUTPUT_JSON = True

# ==========================
# RETE
# ==========================

REQUEST_TIMEOUT = 60

RETRY = 3

PAUSE_SECONDS = 5

# ==========================
# SERVER OVERPASS
# ==========================

OVERPASS_SERVERS = [

    "https://overpass-api.de/api/interpreter",

    "https://overpass.kumi.systems/api/interpreter",

    "https://lz4.overpass-api.de/api/interpreter"

]
