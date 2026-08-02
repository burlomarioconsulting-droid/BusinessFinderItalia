"""
Business Finder Italia
Categorie commerciali da ricercare.
"""

CATEGORIES = [

    # Ristorazione e ricettività
    {"label": "Ristoranti", "key": "amenity", "value": "restaurant"},
    {"label": "Bar e caffè", "key": "amenity", "value": "cafe"},
    {"label": "Hotel", "key": "tourism", "value": "hotel"},
    {"label": "Panifici", "key": "shop", "value": "bakery"},

    # Commercio
    {"label": "Ferramenta", "key": "shop", "value": "hardware"},
    {"label": "Mobilifici", "key": "shop", "value": "furniture"},
    {"label": "Negozi di elettronica", "key": "shop", "value": "electronics"},

    # Cura personale
    {"label": "Parrucchieri", "key": "shop", "value": "hairdresser"},
    {"label": "Centri estetici", "key": "shop", "value": "beauty"},

    # Settore automobilistico
    {"label": "Autofficine", "key": "shop", "value": "car_repair"},
    {"label": "Autolavaggi", "key": "amenity", "value": "car_wash"},
    {"label": "Gommisti", "key": "shop", "value": "tyres"},
    {"label": "Carrozzerie", "key": "craft", "value": "car_painter"},

    # Artigiani e imprese
    {"label": "Idraulici", "key": "craft", "value": "plumber"},
    {"label": "Elettricisti", "key": "craft", "value": "electrician"},
    {"label": "Imprese edili", "key": "craft", "value": "builder"},
    {"label": "Imprese di pulizia", "key": "craft", "value": "cleaning"},
    {"label": "Imprese di decorazione", "key": "craft", "value": "interior_decorator"},
    {"label": "Imbianchini", "key": "craft", "value": "painter"},

    # Trasporti
    {"label": "Trasporti e logistica", "key": "office", "value": "logistics"},

    # Industria
    {"label": "Industrie manifatturiere", "key": "landuse", "value": "industrial"},
]
