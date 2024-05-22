# CONFIGURAÇÕES DO MAPA
MAP_NAME = "Locais para doação - RS"
INITIAL_ZOOM_LEVEL = 8
INITIAL_LATITUDE = -29.8739445
INITIAL_LONGITUDE = -51.1227169

# NOME ARQUIVO SQL DE SAIDA
OUTPUT_FILE = "sos-rs.sql"

LOGS_FOLDER = "./execution_logs"
API_URL = "https://api.sos-rs.com"

SUPPLY_NAMES_MAP_URL = "https://raw.githubusercontent.com/leonardolauryel/map-data/main/data/supplyNamesMap.json"
SUPPLY_NAMES_MAP_LOCAL = "./local_data/supplyNamesMap.json"

SUPPLY_CATEGORIES_MAP_URL = "https://raw.githubusercontent.com/leonardolauryel/map-data/main/data/supplyCategoriesMap.json"
SUPPLY_CATEGORIES_MAP_LOCAL = "./local_data/supplyCategoriesMap.json"

LOCATION_COORDINATES_URL = "https://raw.githubusercontent.com/leonardolauryel/map-data/main/data/locationCoordinates.json"
LOCATION_COORDINATES_LOCAL = "./local_data/locationCoordinates.json"

URGENT_NEED = 100
NEED = 10
AVAILABLE = 1

# Permite habilitar o mapeamento de nomes de suprimtos
# Isso permite agrupar nomes similates como: Agua, Água potável, Agua Mineral
MAP_SUPPLY_NAMES = True

# Esse valor faz o sistema pegar somente os abrigos que foram atualizados nos últimos x dias
MAX_TIME_SHELTER_UPDATE = 7

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
        'name': 'Disponível p/ doação',
        'priority': AVAILABLE
    }
}

SUPPLIES_NAMES_MAP = {}

SUPPLY_CATEGORIES_MAP = {}

LOCATION_COORDINATES = {}

SUPPLIES_TAG_COLOR = {'Achocolatado': '#7198c9', 'Alface': '#eac6bb', 'Alho': '#b37ce7', 'Alimentos Diversos': '#c68dc8', 'Alimentos Não Perecíveis': '#81b6f4', 'Alimentos Perecíveis': '#e1f69e', 'Alimentos para consumo rápido': '#dbeccd', 'Arroz': '#a71fd9', 'Atum': '#d49a0e', 'Aveia': '#d2b2eb', 'Azeite': '#f4ecc1', 'Açúcar': '#d3f9fb', 'Banana': '#56fc9d', 'Batata': '#f0537d', 'Bolacha': '#317e31', 'Bolacha Doce': '#98cbf8', 'Bolacha Salgada': '#e1da8e', 'Bolinho': '#bbc5f4', 'Bombona Vazia': '#dee8fd', 'Cafeteira Industrial': '#f8f7e2', 'Café': '#9268fe', 'Carne': '#4337f6', 'Carne Moída': '#af4b30', 'Carne de Frango': '#62e0b4', 'Carne de Gado': '#f0f1fd', 'Cebola': '#21c48a', 'Cestas Básicas': '#b60f10', 'Chá': '#8f3ce3', 'Embalagens descartáveis para marmitas': '#20c020', 'Farinha': '#7df7a3', 'Farinha Láctea': '#bfeeee', 'Farinha de Milho': '#effdcb', 'Farinha de Polenta': '#c4fbdc', 'Farinha de Trigo': '#e6e0f4', 'Feijão': '#dbb898', 'Fibra Alimentar': '#ea9070', 'Frios': '#b1905c', 'Frutas': '#ed6252', 'Fórmula Infantil': '#d5f9af', 'Fórmula Infantil Número 1 (0-6)': '#fdec22', 'Galão De Água Vazio': '#ace0fe', 'Gelo': '#e2e4ef', 'Geléia': '#b40947', 'Iogurte': '#c1bb01', 'Isotônicos': '#433dcb', 'Lanches': '#f3fef3', 'Legumes': '#fbd7c1', 'Leite': '#f69059', 'Leite Condensado': '#7499c2', 'Leite em Pó': '#bff1cd', 'Lentilha': '#d2bde8', 'Macarrão': '#bc3df1', 'Mamão': '#4aa8b0', 'Margarina': '#d96715', 'Marmitas': '#99dcbe', 'Massa': '#6e7c2c', 'Massa de Bolo': '#7dd1d8', 'Maçã': '#75d02b', 'Molho de Tomate': '#7c7823', 'Mucilon': '#948937', 'Neston': '#934fc5', 'Ovos': '#5a40cc', 'Pipoca': '#f7fefe', 'Polenta': '#4be0a0', 'Proteínas': '#b77c63', 'Pão de Sanduíche': '#defcf6', 'Ração para Gato': '#82a80e', 'Sal': '#704730', 'Saladas': '#c0b9f7', 'Sardinha': '#e759cb', 'Suco em Pó': '#c2c0f0', 'Sucos': '#3bb89a', 'Sucos de Caixinha': '#717dc4', 'Temperos': '#ad58d5', 'Toddynho': '#e6e2fa', 'Tomate': '#629bdc', 'Verduras': '#9c41df', 'Vinagre': '#3904b7', 'Água': '#c7eeb8', 'Água Não Potável': '#b0b166', 'Óleo de Cozinha': '#b9ed4f'}