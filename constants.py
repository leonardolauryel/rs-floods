# CONFIGURAÇÕES DO MAPA
MAP_NAME = "Abrigos"
INITIAL_ZOOM_LEVEL = 8
INITIAL_LATITUDE = -29.8739445
INITIAL_LONGITUDE = -51.1227169

# NOME ARQUIVO SQL DE SAIDA
OUTPUT_FILE = "sos-rs.sql"

API_URL = "https://api.sos-rs.com"

URGENT_NEED = 100
NEED = 10
AVAILABLE = 1

PRIORITIES = {
    '100': {
        'name': 'Precisa Urgente',
        'priority': URGENT_NEED
    },
    '10': {
        'name': 'Precisa',
        'priority': NEED
    },
    '1': {
        'name': 'Sobrando',
        'priority': AVAILABLE
    }
}