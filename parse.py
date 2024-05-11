import requests
import re
import unicodedata
import json
import random
import logging
import time

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Desativa o logging
#logging.disable(logging.CRITICAL)


# CONSTANTES

# CONFIGURAÇÕES DO MAPA
MAP_NAME = "Abrigos"
INITIAL_ZOOM_LEVEL = 8
INITIAL_LATITUDE = -29.8739445
INITIAL_LONGITUDE = -51.1227169

# NOME ARQUIVO SQL DE SAIDA
OUTPUT_FILE = "sos-rs.sql"

def escape_sql_string(value):
    """
    Escapa caracteres especiais em uma string para uso em uma instrução SQL, minimizando o risco de injeção de SQL.

    Args:
        value (str): A string original que precisa ser escapada.

    Returns:
        str: A string com caracteres especiais escapados.
    """
    replacements = {
        "'": "''",       # Escapa aspas simples
        "\"": "\\\"",    # Escapa aspas duplas
        ";": "\\;",      # Escapa ponto e vírgula
        "--": "\\--",    # Escapa comentários SQL
        "\\": "\\\\"     # Escapa backslashes
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return value

def sanitize_key(s):
    # Normaliza para forma NFKD e depois converte para ASCII ignorando erros de conversão
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
    # Substitui qualquer coisa que não seja letra, número ou sublinhado por uma string vazia
    return re.sub(r'[^\w]+', '', s)

def gerar_cor_hex_aleatoria():
    """
    Gera uma cor hexadecimal aleatória.

    Returns:
        str: Uma string representando a cor hexadecimal.
    """
    # Gera três números aleatórios entre 0 e 255
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)

    # Formata os números como hexadecimal e retorna
    return f'#{r:02x}{g:02x}{b:02x}'

def save_json(data, filename):
    """
    Salva um objeto de dados em formato JSON em um arquivo.

    Args:
    data (dict or list): Dados que serão serializados para JSON.
    filename (str): Caminho para o arquivo onde o JSON será salvo.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"\n\nDados salvos com sucesso em {filename}")
    except Exception as e:
        print(f"\n\nErro ao salvar os dados: {e}")

def read_json(arquivo_json):
    """
    Lê um arquivo JSON e retorna os dados como um dicionário.

    Args:
        arquivo_json (str): Caminho para o arquivo JSON.

    Returns:
        dict: Dicionário contendo os dados do JSON.

    Raises:
        FileNotFoundError: Se o arquivo não for encontrado.
        json.JSONDecodeError: Se o arquivo não estiver em formato JSON válido.
        Exception: Para outros erros inesperados.
    """
    try:
        with open(arquivo_json, 'r', encoding='utf-8') as arquivo:
            dados = json.load(arquivo)
            return dados
    except FileNotFoundError as e:
        print(f"Erro: O arquivo {arquivo_json} não foi encontrado.")
        raise
    except json.JSONDecodeError as e:
        print("Erro: O arquivo não está em formato JSON válido.")
        raise
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        raise

def get_supply_category_relationship(locations):
    filename = 'supply_category_relationship.json'
    tag_related_location = {}

    counter = 1
    try:
        for key in locations:
            print(counter)
            print(f"Obtendo dado do abrigo com id {key}")
            shelter = fetch_shelter_data_by_id(key)
            print(f"Dados do abrigo {shelter['name']} foram obtidos")
            print()
            counter += 1
            for supply in shelter['shelterSupplies']:

                supply_name_key = sanitize_key(supply['supply']['name'])

                key = tag_related_location.get(supply_name_key)
                if(key is None):
                    tag_related_location[supply_name_key] = {
                        'supply_id': supply['supply']['id'],
                        'supply_name': supply['supply']['name'],
                        'supply_category_id': supply['supply']['supplyCategory']['id'],
                        'supply_category_name': supply['supply']['supplyCategory']['name'],
                    }
    except Exception as e:
        # Executado para qualquer outro erro
        print(f"Ocorreu um erro inesperado: {e}")

    save_json(tag_related_location, filename)

    


# -------------- Requisições -------------- 
def fetch_supply_categories_data():
    url = 'https://api.sos-rs.com/supply-categories'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['data']
    else:
        print("Falha na requisição:", response.status_code)
        return None

def fetch_shelter_data():
    perPage = 100
    page = 1
    all_data = []

    while True:
        url = f"https://api.sos-rs.com/shelters?page={page}&perPage={perPage}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if len(data['data']['results']) == 0:
                break  # Sai do loop se o array de resultados estiver vazio
            all_data.extend(data['data']['results'])
            page += 1
        else:
            print("Falha na requisição:", response.status_code)
            break

    return all_data

def fetch_shelter_data_by_id(id):
    url = f"https://api.sos-rs.com/shelters/{id}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data['data']
    else:
        print("Falha na requisição:", response.status_code)
        return None




# --------------  Criação de objetos Menus, Locations e Tags -------------- 
def create_menus_obj():
    menus = {}
    supply_categories = fetch_supply_categories_data()

    hierarchy_level = "1"
    active = True

    menu_id = 0
    for supply_category in supply_categories:
        menus[supply_category['id']] = {
            'menu_id': menu_id,
            'name': escape_sql_string(supply_category['name']),
            'hierarchy_level': hierarchy_level,
            'active': active
        }

        menu_id += 1
    
    return menus

def create_locations_obj():
    locations = {}
    shelters = fetch_shelter_data()
    active = True

    try:
        json_file = 'location_lat_lng.json'
        location_lat_lng = read_json(json_file)
        print("Dados json de location_lat_lng carregados com sucesso.\n")
    except Exception as e:
        print("Falha ao ler o arquivo JSON.\n")

    location_id = 0
    for shelter in shelters:
        description = shelter['address']

        shelter_name_key = sanitize_key(shelter['name'])

        loc = location_lat_lng.get(shelter_name_key)

        url = f"src=\"https://sos-rs.com/abrigo/{shelter['id']}\""
        overlayed_popup_content = f"<p><iframe style=\"position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;\" title=\"P&aacute;gina Incorporada\" {url}></iframe></p>"

        if (loc and loc['lat'] and loc['lng']):
            latitude = loc['lat']
            longitude = loc['lng']
        else:
            latitude = 0
            longitude = 0

        locations[shelter['id']] = {
            'location_id': location_id,
            'name': escape_sql_string(shelter['name']),
            'description': escape_sql_string(description),
            'overlayed_popup_content': overlayed_popup_content,
            'latitude': latitude,
            'longitude': longitude,
            'active': active,
            'shelterSupplies': shelter['shelterSupplies'],
            'address': shelter['address']
        }

        location_id += 1

    return locations

def create_tags_obj(locations, menus):
    tags = {}

    description = ''
    active = True
 

    # Ler json de relação entre Supply e Category Supply
    try:
        json_file = 'supply_category_relationship.json'
        tag_related_location = read_json(json_file)
        print("Dados json carregados com sucesso.\n")
    except Exception as e:
        print("Falha ao ler o arquivo JSON.\n")
    

    tag_id = 0
    for location in locations.values():
        
        for supply in location['shelterSupplies']:
            supply_name_key = sanitize_key(supply['supply']['name'])

            # obter o id do menu
            try:
                supply_category_id = tag_related_location.get(supply_name_key)['supply_category_id']
            except Exception as e:
                logging.info(f"Não encontrado a relação do supply {supply['supply']['name']}")
            
            if(supply_category_id is not None):
                parent_menu_id = menus.get(supply_category_id)['menu_id']

                color = gerar_cor_hex_aleatoria()

                supply_name_key = sanitize_key(supply['supply']['name'])
                key = tags.get(supply_name_key)
                
                if(key is None):
                    tags[supply_name_key] = {
                        'tag_id': tag_id,
                        'name': supply['supply']['name'],
                        'description': description,
                        'color': color,
                        'active': active,
                        'parent_menu_id': parent_menu_id
                    }
                    tag_id += 1

    # tags['nosupplierinfo'] = {
    #     'tag_id': tag_id,
    #     'name': "Sem informações de itens",
    #     'description': description,
    #     'color': '#808080',
    #     'active': active,
    #     'parent_menu_id': parent_menu_id,
    # }

    return tags

def create_tag_related_location_obj(tags, locations):
    tags_related_locations = {}
    tags_related_locations_id = 0

    for location in locations.values():
        # Se tiver suprimetos
        if len(location['shelterSupplies']):
            for supply in location['shelterSupplies']:
                supply_name_key = sanitize_key(supply['supply']['name'])
                tag = tags[supply_name_key]
                tag_id = tag['tag_id']
                location_id = location['location_id']
                key = f"{tag_id}_{location_id}"

                if tags_related_locations.get(key) is None:
                    tags_related_locations[key] = {
                        'tags_related_locations_id': tags_related_locations_id,
                        'tag_id': tag_id,
                        'location_id': location_id
                    }

                    tags_related_locations_id += 1

    return tags_related_locations





# -------------- Cria os comandos sql --------------
def create_settings_sql():
    settings_sql = ["-- Use this SQL to completely cleanse the map database. The result will be as if the database had been created again"\
    "\nTRUNCATE TABLE Location, Menu, Tag, Link, Links_group, Tag_related_locations, Tag_relationship;"\
    "\n\nalter sequence administration_location_id_seq restart with 1;"\
    "\nalter sequence administration_menu_id_seq restart with 1;"\
    "\nalter sequence administration_tag_id_seq restart with 1;"\
    "\nalter sequence administration_tag_related_locations_id_seq restart with 1;"\
    "\nalter sequence administration_tag_relationship_id_seq restart with 1;"\
    "\n\n-- Setting map settings for Pontos de coleta"\
    f"\nUPDATE map_config SET map_name = '{MAP_NAME}';"\
    f"\nUPDATE map_config SET initial_zoom_level = {INITIAL_ZOOM_LEVEL};"\
    f"\nUPDATE map_config SET initial_latitude = {INITIAL_LATITUDE};"\
    f"\nUPDATE map_config SET initial_longitude = {INITIAL_LONGITUDE};\n\n"]

    return settings_sql


def create_menus_sql(menus):
    menus_sql = []
    menus_sql.append("-- Inserting Menus")

    for menu in menus.values():
        
        menus_sql.append(f"INSERT INTO Menu (id,name,hierarchy_level,active) VALUES" \
                            f"('{menu['menu_id']}','{menu['name']}', '{menu['hierarchy_level']}', {menu['active']});")

    menus_sql.append(f"\nalter sequence administration_menu_id_seq restart with {len(menus)};\n\n")
    return menus_sql


def create_locations_sql(locations):
    locations_sql = []
    locations_sql.append("-- Inserting Locations")

    for location in locations.values():
        locations_sql.append(f"INSERT INTO Location (id, name, description, overlayed_popup_content, latitude, longitude, active) VALUES " \
                        f"('{location['location_id']}', '{location['name']}', '{location['description']}', '{location['overlayed_popup_content']}', '{location['latitude']}', '{location['longitude']}', {location['active']});")

    
    locations_sql.append(f"\nalter sequence administration_location_id_seq restart with {len(locations)};\n\n")
    return locations_sql


def create_tags_sql(tags):
    tags_sql = []
    tags_sql.append(f"-- Inserting Tags")

    for tag in tags.values():
        tags_sql.append(f"INSERT INTO Tag (id,name,description,color,active,parent_menu_id) VALUES " \
                            f"('{tag['tag_id']}', '{tag['name']}', '{tag['description']}', '{tag['color']}', {tag['active']}, '{tag['parent_menu_id']}');")

    tags_sql.append(f"\nalter sequence administration_tag_id_seq restart with {len(tags)};\n\n")

    return tags_sql


def create_tags_related_locations_sql(tags_related_locations):
    tags_related_locations_sql = []

    tags_related_locations_sql.append(f"-- Tags relationship with Locations")

    for tag_related_location in tags_related_locations.values():
        tags_related_locations_sql.append(f"INSERT INTO Tag_related_locations (id, tag_id, location_id) VALUES " \
                                    f"('{tag_related_location['tags_related_locations_id']}', '{tag_related_location['tag_id']}', '{tag_related_location['location_id']}');")

    tags_related_locations_sql.append(f"\nalter sequence administration_tag_related_locations_id_seq restart with {len(tags_related_locations)};\n\n")

    return tags_related_locations_sql



def create_sql_commands():
    sql_commands = []

    menus = create_menus_obj()
    locations = create_locations_obj()


    # Deixar comentado. Isso é usado somente quando for preciso
    # obter as relações de supply e category supply
    #get_supply_category_relationship(locations)
    
    tags = create_tags_obj(locations, menus)
    tags_related_locations = create_tag_related_location_obj(tags, locations)

    

    #Configurações iniciais do mapa
    sql_commands.extend(create_settings_sql())

    sql_commands.extend(create_menus_sql(menus))
    sql_commands.extend(create_locations_sql(locations))
    sql_commands.extend(create_tags_sql(tags))
    sql_commands.extend(create_tags_related_locations_sql(tags_related_locations))
    
    return sql_commands


def write_sql_commands(sql_commands, output_file):
    with open(output_file, 'w') as file:
        for command in sql_commands:
            file.write(command + '\n')




if __name__ == '__main__':
    # shelter_data = fetch_shelter_data()

    sql_commands = create_sql_commands()
    write_sql_commands(sql_commands, OUTPUT_FILE)