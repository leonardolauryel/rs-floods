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


URGENT_NEED = 100
NEED = 10
AVAILABLE = 1

# Permite habilitar o mapeamento de nomes de suprimtos
# Isso permite agrupar nomes similates como: Agua, Água potável, Agua Mineral
MAP_SUPPLY_NAMES = True

# Esse valor faz o sistema pegar somente os abrigos que foram atualizados nos últimos x dias
MAX_TIME_SHELTER_UPDATE = 14

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

SUPPLY_CATEGORIES_MAP = {
    'Medicamentos': [
        "Antibiótico",
        "Azitotromicina",
        "Caneta Insulina Glargin (glargina)",
        "Colírio",
        "Dersani",
        "Medicamentos Comuns",
        "Medicamentos prescritos",
        "Pomada para assadura",
        "Prednizolona Para Animais",
        "Remédio para piolho",
        "Remédios básicos",
        "Shampoo Para Piolho",
        "Soro",
        "Soro Hospitalar",
        "Vacina Hepatite A",
        "Vacina Para Covid",
        "Vacina Para Influenza",
        "Vermífugo",
        "Vincristina",
        "Xarope Para Gripe"
    ],
    'Cuidados com Animais': [
        "Cobertores Para Pet",
        "Coleiras Para Pet",
        "Insumos Para Internação Veterinário",
        "Peiteira/Coleira Grande",
        "Petisco Para Animais",
        "Ração Senior"
    ],
    'Especialistas e Profissionais': [],
    'Acomodações e Descanso': [
        "Cama De Hospital",
        "Colchão Piramidal",
        "Travesseiros",
        "Colchões",
        "Cama Geriatria",
        "Colchão Solteiro"
    ],
    'Equipamentos de Emergência': [
        "Kits de primeiros socorros",
        "Esparadrapo"
    ],
    'Voluntariado': [
        "Não Precisa De Voluntários (não Considerar Item Acima: \"voluntários - Tarde\")",
        "Voluntários Para Organizar Roupas"
    ],
    'Itens Descartáveis': [
        "Fralda Geriátrica ( Xg)",
        "Luvas Descartáveis",
        "Seringa 3 E 5ml Com Agulha 70x30",
        "Seringa De Insulina",
        "Embalagem descartável para as marmitas",
        "Fraldas"
    ],
    'Higiene Pessoal': [
        "Bucha",
        "Desodorantes",
        "Higiene Pessoal",
        "Repelente",
        "Banheira",
        "Luva G",
        "Pasta De Dente Infantil",
        "Xampu Infantil",
        "Talco Infantil",
        "Escova De Dente"
    ],
    'Alimentos e Água': [
        "Açúcar",
        "Alimentos Não Perecíveis",
        "Cebola",
        "Cesta Básica",
        "Fibra Alimentar Em Pó",
        "Óleo De Cozinha",
        "Polenta",
        "Saladas",
        "Tomate",
        "Enlatados (ervilha e milho)",
        "Oléo",
        "Chá",
        "Suco Em Pó",
        "Fórmula infantil",
        "Leite Materno",
        "Toddy",
        "Erva Mate"
    ],
    'Material de Limpeza': [
        "Álcool Em Gel Potes Médios Para Espalha",
        "Itens de limpeza",
        "Sabão Em Pó",
        "Sacos de lixo"
    ],
    'Vestuário': [
        "Calça Masculina Geral",
        "Calça Moletom Masculino",
        "Calcinhas Infantis G",
        "Casacos Quentes Para Adultos",
        "Cuecas Adultos G",
        "Roupa De Inverno Infantil",
        "Roupas Maculinas",
        "Roupas Masculinas De Moletom G A Xxg (casacos E Calças)",
        "Meia Infantil",
        "Tênis 36-39",
        "Roupa íntima feminina",
        "Cueca",
        "Blusão G",
        "Calça Com Elástico F E M"
    ],
    'Veículos de Resgate e Transporte': [
        "Gás 45 Kg"
    ],
    'Outros': [
        "Espaçador Infantil Para Bombinha",
        "Protetor Auricular Para Ruídos",
        "Termômetro",
        "Biombos",
        "Bombona Vazia 20l",
        "Bico",
        "Carrinho De Bebe",
        "Fita Adesiva Crepe",
        "Caixa De Transporte"
    ],
    'Mobílias': [
        "Baldes/bacias"
    ],
    'Eletrodomésticos e Eletrônicos': [
        "Ventilador",
        "Balança",
    ],
    'Entretenimento': []
}

SUPPLIES_TAG_COLOR = {'Achocolatado': '#7198c9', 'Alface': '#eac6bb', 'Alho': '#b37ce7', 'Alimentos Diversos': '#c68dc8', 'Alimentos Não Perecíveis': '#81b6f4', 'Alimentos Perecíveis': '#e1f69e', 'Alimentos para consumo rápido': '#dbeccd', 'Arroz': '#a71fd9', 'Atum': '#d49a0e', 'Aveia': '#d2b2eb', 'Azeite': '#f4ecc1', 'Açúcar': '#d3f9fb', 'Banana': '#56fc9d', 'Batata': '#f0537d', 'Bolacha': '#317e31', 'Bolacha Doce': '#98cbf8', 'Bolacha Salgada': '#e1da8e', 'Bolinho': '#bbc5f4', 'Bombona Vazia': '#dee8fd', 'Cafeteira Industrial': '#f8f7e2', 'Café': '#9268fe', 'Carne': '#4337f6', 'Carne Moída': '#af4b30', 'Carne de Frango': '#62e0b4', 'Carne de Gado': '#f0f1fd', 'Cebola': '#21c48a', 'Cestas Básicas': '#b60f10', 'Chá': '#8f3ce3', 'Embalagens descartáveis para marmitas': '#20c020', 'Farinha': '#7df7a3', 'Farinha Láctea': '#bfeeee', 'Farinha de Milho': '#effdcb', 'Farinha de Polenta': '#c4fbdc', 'Farinha de Trigo': '#e6e0f4', 'Feijão': '#dbb898', 'Fibra Alimentar': '#ea9070', 'Frios': '#b1905c', 'Frutas': '#ed6252', 'Fórmula Infantil': '#d5f9af', 'Fórmula Infantil Número 1 (0-6)': '#fdec22', 'Galão De Água Vazio': '#ace0fe', 'Gelo': '#e2e4ef', 'Geléia': '#b40947', 'Iogurte': '#c1bb01', 'Isotônicos': '#433dcb', 'Lanches': '#f3fef3', 'Legumes': '#fbd7c1', 'Leite': '#f69059', 'Leite Condensado': '#7499c2', 'Leite em Pó': '#bff1cd', 'Lentilha': '#d2bde8', 'Macarrão': '#bc3df1', 'Mamão': '#4aa8b0', 'Margarina': '#d96715', 'Marmitas': '#99dcbe', 'Massa': '#6e7c2c', 'Massa de Bolo': '#7dd1d8', 'Maçã': '#75d02b', 'Molho de Tomate': '#7c7823', 'Mucilon': '#948937', 'Neston': '#934fc5', 'Ovos': '#5a40cc', 'Pipoca': '#f7fefe', 'Polenta': '#4be0a0', 'Proteínas': '#b77c63', 'Pão de Sanduíche': '#defcf6', 'Ração para Gato': '#82a80e', 'Sal': '#704730', 'Saladas': '#c0b9f7', 'Sardinha': '#e759cb', 'Suco em Pó': '#c2c0f0', 'Sucos': '#3bb89a', 'Sucos de Caixinha': '#717dc4', 'Temperos': '#ad58d5', 'Toddynho': '#e6e2fa', 'Tomate': '#629bdc', 'Verduras': '#9c41df', 'Vinagre': '#3904b7', 'Água': '#c7eeb8', 'Água Não Potável': '#b0b166', 'Óleo de Cozinha': '#b9ed4f'}