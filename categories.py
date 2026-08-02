"""
Business Finder Italia
Categorie commerciali e relativi tag OpenStreetMap.
"""

CATEGORIES = [
    {
        "label": "Ristoranti",
        "queries": [
            {"key": "amenity", "value": "restaurant"},
        ],
    },
    {
        "label": "Bar e caffè",
        "queries": [
            {"key": "amenity", "value": "cafe"},
            {"key": "amenity", "value": "bar"},
        ],
    },
    {
        "label": "Hotel",
        "queries": [
            {"key": "tourism", "value": "hotel"},
        ],
    },
    {
        "label": "Panifici",
        "queries": [
            {"key": "shop", "value": "bakery"},
        ],
    },
    {
        "label": "Ferramenta",
        "queries": [
            {"key": "shop", "value": "hardware"},
            {"key": "shop", "value": "doityourself"},
        ],
    },
    {
        "label": "Mobilifici",
        "queries": [
            {"key": "shop", "value": "furniture"},
        ],
    },
    {
        "label": "Negozi di elettronica",
        "queries": [
            {"key": "shop", "value": "electronics"},
            {"key": "shop", "value": "computer"},
        ],
    },
    {
        "label": "Parrucchieri",
        "queries": [
            {"key": "shop", "value": "hairdresser"},
        ],
    },
    {
        "label": "Centri estetici",
        "queries": [
            {"key": "shop", "value": "beauty"},
        ],
    },
    {
        "label": "Autofficine",
        "queries": [
            {"key": "shop", "value": "car_repair"},
        ],
    },
    {
        "label": "Autolavaggi",
        "queries": [
            {"key": "amenity", "value": "car_wash"},
        ],
    },
    {
        "label": "Gommisti",
        "queries": [
            {"key": "shop", "value": "tyres"},
        ],
    },
    {
        "label": "Carrozzerie",
        "queries": [
            {"key": "craft", "value": "car_painter"},
            {"key": "service:vehicle:body_repair", "value": "yes"},
            {"key": "service:vehicle:painting", "value": "yes"},
        ],
    },
    {
        "label": "Idraulici",
        "queries": [
            {"key": "craft", "value": "plumber"},
        ],
    },
    {
        "label": "Elettricisti",
        "queries": [
            {"key": "craft", "value": "electrician"},
        ],
    },
    {
        "label": "Imprese edili",
        "queries": [
            {"key": "craft", "value": "builder"},
            {"key": "office", "value": "construction_company"},
        ],
    },
    {
        "label": "Imprese di pulizia",
        "queries": [
            {"key": "craft", "value": "cleaning"},
            {"key": "office", "value": "cleaning"},
        ],
    },
    {
        "label": "Imprese di decorazione",
        "queries": [
            {"key": "craft", "value": "interior_decorator"},
            {"key": "office", "value": "interior_design"},
        ],
    },
    {
        "label": "Imbianchini",
        "queries": [
            {"key": "craft", "value": "painter"},
        ],
    },
    {
        "label": "Trasporti e logistica",
        "queries": [
            {"key": "office", "value": "logistics"},
            {"key": "office", "value": "transport"},
        ],
    },
    {
        "label": "Industrie manifatturiere",
        "queries": [
            {"key": "man_made", "value": "works"},
            {"key": "industrial", "value": "factory"},
            {"key": "building", "value": "industrial"},
        ],
    },
]
