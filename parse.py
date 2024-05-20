from utils import *
from constants import *
from logs_message import *

import requests
import logging
import time
from pprint import pprint

# -------------- Requisições -------------- 
def fetch_supply_categories_data():
    url = f"{API_URL}/supply-categories"
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
        url = f"{API_URL}/shelters?page={page}&perPage={perPage}"
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
    url = f"{API_URL}/shelters/{id}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data['data']
    else:
        print("Falha na requisição:", response.status_code)
        return None

def fetch_supplies_data():
    url = f"{API_URL}/supplies"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data['data']
    else:
        print("Falha na requisição:", response.status_code)
        return None


def fetch_json(url, local_file):
    try:
        # Try to download the JSON data from the URL
        print("Acessando supplyNamesMap remoto")
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
        data = response.json()
    except (requests.exceptions.RequestException, json.JSONDecodeError):
        # If downloading fails or JSON decoding fails, try to read the local file
        print("Falha ao acessar supplyNamesMap remoto")
        print("Acessando supplyNamesMap local")
        try:
            with open(local_file, 'r') as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # If the local file is not found or JSON decoding fails, raise an error
            raise RuntimeError(f"Failed to load JSON data from both URL and local file: {e}")
    return data

def get_parent_menu_by_key(menus, menu_key):
    parent_menu = menus.get(menu_key)
    if(parent_menu is not None):
        return parent_menu
    else:
        return False


def correct_supply_assignments(supply, supply_categories):

    supply_name = supply['supply']['name']
    closest_key = find_closest_key(supply_name, SUPPLY_CATEGORIES_MAP, confidence_threshold=0.7)

    # Encontrou uma categoria
    if closest_key is not None:
        menu_name = closest_key
        menu_id = supply_categories.get(menu_name)['id']

        # Encontrou o ID do menu
        if menu_id is not None:
            menu_key = f"{menu_id}_{supply['priority']}"
            print(f"{supply_name:<30} ->   {closest_key}")

            return menu_key

    return None


# --------------  Criação de objetos Menus, Locations e Tags -------------- 
def create_menus_group_obj():
    menus_group = {}

    menu_group_id = 0
    for priority_key, priority in PRIORITIES.items():
        menus_group[priority_key] = {
            'menu_group_id': menu_group_id,
            'name': priority['name'],
            'priority': priority['priority']
        }
        menu_group_id += 1

    return menus_group

def create_menus_obj(menus_group):
    menus = {}
    supply_categories = fetch_supply_categories_data()

    hierarchy_level = "1"
    active = True

    menu_id = 0

    for menu_group in menus_group.values():
        for supply_category in supply_categories:
            menu_key = f"{supply_category['id']}_{menu_group['priority']}"

            menus[menu_key] = {
                'menu_id': menu_id,
                'name': escape_sql_string(supply_category['name']),
                'menu_group_id': menu_group['menu_group_id'], 
                'hierarchy_level': hierarchy_level,
                'active': active,
                'tags': []
            }

            menu_id += 1
    
    return menus

def create_locations_obj():
    locations = {}
    shelters = fetch_shelter_data()
    active = True

    # Abre o json de coordenadas para caso precise
    try:
        json_file = './location_lat_lng.json'
        all_coordinates = read_json(json_file)
        print("Dados json de coorenadas carregados com sucesso.\n")
    except Exception as e:
        print("Falha ao ler o arquivo JSON de coordenadas.\n")

    shelters_without_coordinates = {}

    location_id = 0
    for shelter in shelters:
        if 'DESATIVADO' in shelter['name']:
            create_log("info", f"O abrigo '{shelter['name']}' está desativado")
            continue
        
        if not is_within_days(shelter['updatedAt'], MAX_TIME_SHELTER_UPDATE):
            continue

        url = f"https://sos-rs.com/abrigo/{shelter['id']}\""
        overlayed_popup_content =  f"<div style=\"width: 100%; height: 100vh; margin-top: -104px; border: none; position: relative;\"><iframe style=\"position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;\" title=\"P&aacute;gina Incorporada\" src=\"{url}\"></iframe></div>"

        latitude = shelter['latitude']
        longitude = shelter['longitude']

        if not shelter['id'].endswith('\r'):
            # Se as coordenadas não são validas, tenta obter elas do arquivo local
            if not is_valid_coordinates(latitude, longitude):
                shelter_name_key = sanitize_key(shelter['name'])
                coordinates = all_coordinates.get(shelter_name_key)

                if (coordinates and coordinates['lat'] and coordinates['lng']):
                    latitude = coordinates['lat']
                    longitude = coordinates['lng']
                    create_log("info", f"As coordenadas do abrigo '{shelter['name']}' foram obtidas dos dados locais")
                else:
                    #tentar pegar do google
                    latitude = 0
                    longitude = 0

                    shelters_without_coordinates[sanitize_key(shelter['name'])] = {
                        'name': shelter['name'],
                        'address': shelter['address']
                    }

            description = create_location_description(shelter, latitude, longitude)

            location = {
                'location_id': location_id,
                'name': escape_sql_string(shelter['name']),
                'description': description,
                'overlayed_popup_content': overlayed_popup_content,
                'latitude': latitude,
                'longitude': longitude,
                'active': active,
                'shelterSupplies': [],
                'address': shelter['address']
            }

            for supply in shelter['shelterSupplies']:
                supply_obj = supply
                supply_name = supply['supply']['name']

                # Faz mapeamento dos nomes de suprimentos
                if MAP_SUPPLY_NAMES:
                    supply_name_mapped_static = find_closest_key(supply_obj['supply']['name'], SUPPLIES_NAMES_MAP, confidence_threshold=0.7)
                    
                    if supply_name_mapped_static is not None:
                        supply_obj['supply']['name'] = supply_name_mapped_static

                        msg = f"{supply_name:<30}->\t{supply_name_mapped_static}"
                        create_log("supply_name_mapped", msg)
                    else:
                        msg = f"{supply_name}"
                        create_log("supply_name_not_mapped", msg)

                
                location['shelterSupplies'].append(supply_obj)
                    
            locations[shelter['id']] = location
            location_id += 1
        else:
            pass
            #create_log("error", f"O id do abrigo '{shelter['name']}' termina com /r")

    add_about_location(locations, location_id)

    create_log("error", f"Os abrigos '{shelters_without_coordinates}' não possuem coordenadas.")

    return locations

def create_tags_obj(menus, locations):
    tags = {}
    active = True
    description = ""

    supply_categories = create_supply_categories_obj()

    tag_id = 0
    for location in locations.values():
        if location['shelterSupplies']:
            for supply in location['shelterSupplies']:

                #color = SUPPLIES_TAG_COLOR.get(supply['supply']['name'])
                
                color = generate_random_hex_color()
                if color is None:
                    #color = "#000000"
                    color = generate_random_hex_color()

                # Faz a correção da atribuição de alguns suprimentos com categorias
                menu_key = correct_supply_assignments(supply, supply_categories)

                # Caso nenhuma correção foi feita
                if menu_key is None:
                    menu_key = f"{supply['supply']['supplyCategoryId']}_{supply['priority']}"

                parent_menu = get_parent_menu_by_key(menus, menu_key)

                parent_menu_id = parent_menu['menu_id']
                
                if parent_menu_id is not None:
                    tag_key = f"{sanitize_key(supply['supply']['name'])}_{supply['priority']}"
                    tags[tag_key] = {
                        'tag_id': tag_id,
                        'name': escape_sql_string(supply['supply']['name']),
                        'description': description,
                        'color': color,
                        'active': active,
                        'parent_menu_id': parent_menu_id
                    }

                    menus.get(menu_key)['tags'].append(tag_key)

                    tag_id += 1
                else:
                    create_log("error", f"Não foi possível encontrar o menu da tag '{supply['supply']['name']}' ({supply['supply']['id']})")
        
        else:
            create_log("info", f"O abrigo '{location['name']}' ({location['location_id']}) não possui suprimentos cadastrados.")

    return tags

def create_tag_related_location_obj(tags, locations):
    tags_related_locations = {}
    tags_related_locations_id = 0

    for location in locations.values():
        # Se tiver suprimetos
        if len(location['shelterSupplies']):
            for supply in location['shelterSupplies']:
                supply_key = f"{sanitize_key(supply['supply']['name'])}_{supply['priority']}"
                tag = tags.get(supply_key)

                if tag:
                    tag_id = tag['tag_id']
                    location_id = location['location_id']

                    if is_valid_tag_id_location_id(tag_id, location_id):
                        key = f"{tag_id}_{location_id}"
                        tags_related_locations[key] = {
                            'tags_related_locations_id': tags_related_locations_id,
                            'tag_id': tag_id,
                            'location_id': location_id
                        }

                        tags_related_locations_id += 1
                    else:
                        create_log("error", f"Não foi encontrada a relação entre o abrigo '{location['name']}' ({location['location_id']}) e o suprimento '{tag['name']}' ({tag['tag_id']}).")
                else:
                    create_log("error", f"Não foi encontrado suprimento com id {supply_key}")

    return tags_related_locations

def create_supply_categories_obj():
    supply_categories = {}
    supply_categories_data = fetch_supply_categories_data()
    
    for supply_category in supply_categories_data:
        supply_categories[supply_category['name']] = supply_category

    # save_json(supply_categories, "./mocks/supply_categories.json")
    return supply_categories

def remove_empty_menus(menus):
    menu_keys = list(menus.keys())

    for menu_key in menu_keys:
        if not menus[menu_key]['tags']:  # Checa se a lista de tags está vazia
            del menus[menu_key]  # Remove o item do dicionário


def create_location_description(shelter, lat, lng):
    location_updatedAt = shelter['updatedAt']
    if location_updatedAt is not None:
        update_text = f"{converter_utc_para_brasilia(location_updatedAt)}"
    else:
        update_text = f"Sem Atualização"
    
    description = f"<h3>Última Atualização: {update_text}</h3> "\
        f"<p><strong>Endereço:</strong> {escape_sql_string(shelter['address'])}</p>" \
        f"<p style=\"text-align: center;\"><a href=\"{create_link_google_maps(lat, lng)}\" target=\"_blank\">Abrir Localização no Maps</a></p>"

    supply_urgent_need = []
    supply_need = []
    supply_available = []

    for supply in shelter['shelterSupplies']:
        if supply['priority'] == PRIORITIES[f"{URGENT_NEED}"]['priority']:
            supply_urgent_need.append(supply)
        if supply['priority'] == PRIORITIES[f"{NEED}"]['priority']:
            supply_need.append(supply)
        if supply['priority'] == PRIORITIES[f"{AVAILABLE}"]['priority']:
            supply_available.append(supply)
    
    
    description += \
    "<p style=\"font-family: Arial, sans-serif; margin: 20px; background: #f4f4f4; color: #333;\">"
    
    # Add lista de "Precisa urgente de:"
    if len(supply_urgent_need) > 0:
        description += "<h2 style=\"color: #444;\">Precisa urgente de:</h2>" \
        "<ul style=\"list-style-type: none; padding: 0;\">"
        
        for supply in supply_urgent_need:
            # updatedAt = supply['supply']['updatedAt']
            # if updatedAt is not None:
            #     update_text = f"(Atualizado em: {converter_utc_para_brasilia(supply['supply']['updatedAt'])})"
            # else:
            #     update_text = f"(Sem Atualização)"
            description += f"<li style=\"padding: 10px 20px; margin: 5px 0; border-radius: 20px; background-color: #f69f9d; color: black; display: flex; justify-content: center; align-items: center;\">{supply['supply']['name']}</li>"
        
        description += "</ul>"
    
    # Add lista de "Precisa de:"
    if len(supply_need) > 0:
        description += "<h2 style=\"color: #444;\">Precisa de:</h2>" \
        "<ul style=\"list-style-type: none; padding: 0;\">"

        for supply in supply_need:
            # updatedAt = supply['supply']['updatedAt']
            # if updatedAt is not None:
            #     update_text = f"(Atualizado em: {converter_utc_para_brasilia(supply['supply']['updatedAt'])})"
            # else:
            #     update_text = f"(Sem Atualização)"
            description += f"<li style=\"padding: 10px 20px; margin: 5px 0; border-radius: 20px; background-color: #f8b993; color: black; display: flex; justify-content: center; align-items: center;\">{supply['supply']['name']}</li>"
        
        description += "</ul>"

    # Add lista de "Disponível para doação:"
    if len(supply_available) > 0:
        description += "<h2 style=\"color: #444;\">Disponível para doação:</h2>" \
        "<ul style=\"list-style-type: none; padding: 0;\">"

        for supply in supply_available:
            # updatedAt = supply['supply']['updatedAt']
            # if updatedAt is not None:
            #     update_text = f"(Atualizado em: {converter_utc_para_brasilia(supply['supply']['updatedAt'])})"
            # else:
            #     update_text = f"(Sem Atualização)"
            description += f"<li style=\"padding: 10px 20px; margin: 5px 0; border-radius: 20px; background-color: #9cd487; color: black; display: flex; justify-content: center; align-items: center;\">{supply['supply']['name']}</li>"
        
        description +="</ul>" 
    
    description += "</p>"
    
    return description

def add_about_location(locations, location_id):
    overlayed_popup_content = """
        <div style="width: 100%; margin: auto; margin-top: -28px; background: #fff; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
        <p>&nbsp;</p>
        <div style="margin: 1px 20px 0px 10px;">
        <p>O Mapa Interativo de Doa&ccedil;&otilde;es &eacute; uma iniciativa de alunos do Instituto de Inform&aacute;tica da UFRGS e volunt&aacute;rios, com apoio limitado da RNP. Este mapa visa facilitar a visualiza&ccedil;&atilde;o dos itens de doa&ccedil;&atilde;o que os locais necessitam, proporcionando uma plataforma centralizada e acess&iacute;vel para quem deseja ajudar.</p>
        <h2 style="color: #0056b3;"><span style="color: #000000;">Contato</span></h2>
        <p>Para mais informa&ccedil;&otilde;es, entre em contato conosco pelo email: <a style="color: #0056b3; text-decoration: none;" href="mailto:inserir_email">inserir_email</a></p>
        <h2 style="color: #0056b3;"><span style="color: #000000;">Agradecimentos</span></h2>
        <p>Agradecemos &agrave; equipe do <a target="_blank" href="https://sos-rs.com/">SOS-RS</a> pela disponibiliza&ccedil;&atilde;o dos dados para este mapa de filtros.</p>
        </div>
        </div>
        """

    locations['Sobreestemapa'] = {
        'location_id': location_id,
        'name': 'Sobre este mapa',
        'description': '',
        'overlayed_popup_content': overlayed_popup_content,
        'latitude': 0,
        'longitude': 0,
        'active': True,
        'shelterSupplies': [],
        'address': ''
    }
    
# -------------- Cria os comandos sql --------------
def create_settings_sql():
    settings_sql = ["-- Use this SQL to completely cleanse the map database. The result will be as if the database had been created again"\
    "\nTRUNCATE TABLE Location, Menu, Menugroup, Tag, Link, Links_group, Tag_related_locations, Tag_relationship;"\
    "\n\nalter sequence administration_location_id_seq restart with 1;"\
    "\nalter sequence administration_menu_id_seq restart with 1;"\
    "\nalter sequence menugroup_id_seq restart with 1;"
    "\nalter sequence administration_tag_id_seq restart with 1;"\
    "\nalter sequence administration_tag_related_locations_id_seq restart with 1;"\
    "\nalter sequence administration_tag_relationship_id_seq restart with 1;"\
    "\n\n-- Setting map settings for Pontos de coleta"\
    f"\nUPDATE map_config SET map_name = '{MAP_NAME}';"\
    f"\nUPDATE map_config SET initial_zoom_level = {INITIAL_ZOOM_LEVEL};"\
    f"\nUPDATE map_config SET initial_latitude = {INITIAL_LATITUDE};"\
    f"\nUPDATE map_config SET initial_longitude = {INITIAL_LONGITUDE};\n\n"]

    return settings_sql


def create_menus_group_sql(menus_group):
    menus_group_sql = []
    menus_group_sql.append("-- Inserting Menus Group")

    for menu_group in menus_group.values():
        menus_group_sql.append(f"INSERT INTO MenuGroup (id,name) VALUES" \
                                f"('{menu_group['menu_group_id']}','{menu_group['name']}');")
    
    menus_group_sql.append(f"\nalter sequence menugroup_id_seq restart with {len(menus_group)};\n\n")

    return menus_group_sql


def create_menus_sql(menus):
    menus_sql = []
    menus_sql.append("-- Inserting Menus")

    # latest_menus = {}

    # Ordena os menus por ordem alfabetica
    sorted_menus = dict(sorted(menus.items(), key=lambda item: item[1]["name"]))

    for menu_key, menu in sorted_menus.items():
        # if(menu['name'] == "Medicamentos"):
        #     latest_menus[menu_key] = menu
        # else:
        menus_sql.append(f"INSERT INTO Menu (id,name,group_id,hierarchy_level,active) VALUES" \
                            f"('{menu['menu_id']}','{menu['name']}', '{menu['menu_group_id']}', '{menu['hierarchy_level']}', {menu['active']});")
    
    # Adiciona o menu de Medicamentos por último
    # for menu in latest_menus.values():
    #     menus_sql.append(f"INSERT INTO Menu (id,name,group_id,hierarchy_level,active) VALUES" \
    #                         f"('{menu['menu_id']}','{menu['name']}', '{menu['menu_group_id']}', '{menu['hierarchy_level']}', {menu['active']});")

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

    try:
        global SUPPLIES_NAMES_MAP
        SUPPLIES_NAMES_MAP = fetch_json(SUPPLY_NAMES_MAP_URL, SUPPLY_NAMES_MAP_LOCAL)
        print("Dados de supplyNamesMap obtidos com sucesso")
    except RuntimeError as e:
        print(e)

    menus_group = create_menus_group_obj()
    menus = create_menus_obj(menus_group)
    locations = create_locations_obj()
    tags = create_tags_obj(menus, locations)   
    tags_related_locations = create_tag_related_location_obj(tags, locations)

    remove_empty_menus(menus)

    # save_json(menus_group, "./mocks/menus_group.json")
    # save_json(menus, "./mocks/menus.json")
    # save_json(locations, "./mocks/locations.json")
    # save_json(tags, "./mocks/tags.json")
    # save_json(tags_related_locations, "./mocks/tags_related_locations.json")

    print(f"Menus: {len(menus)}")
    print(f"Locations: {len(locations)}")
    print(f"Tags: {len(tags)}")


    # #Configurações iniciais do mapa
    sql_commands.extend(create_settings_sql())

    sql_commands.extend(create_menus_group_sql(menus_group))
    sql_commands.extend(create_menus_sql(menus))
    sql_commands.extend(create_locations_sql(locations))
    sql_commands.extend(create_tags_sql(tags))
    sql_commands.extend(create_tags_related_locations_sql(tags_related_locations))


    save_logs('all')
    
    return sql_commands


def write_sql_commands(sql_commands, output_file):
    with open(output_file, 'w') as file:
        for command in sql_commands:
            file.write(command + '\n')




if __name__ == '__main__':
    # shelter_data = fetch_shelter_data()

    sql_commands = create_sql_commands()
    write_sql_commands(sql_commands, OUTPUT_FILE)