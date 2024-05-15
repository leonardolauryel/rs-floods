# CONFIGURAÇÕES DO MAPA
MAP_NAME = "Locais para doação - RS"
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
        'name': 'Disponível p/ doação',
        'priority': AVAILABLE
    }
}
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
        "Talco Infantil"
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
        "Fórmula infantil"
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
        "Fita Adesiva Crepe"
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
