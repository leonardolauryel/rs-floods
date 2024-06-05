from utils import *
from constants import *
from logs_message import *
from requests_sos_rs import *
from sql_builder import *

import logging
import time
import sys
from pprint import pprint

def get_parent_menu_by_key(menus, menu_key):
    parent_menu = menus.get(menu_key)
    if(parent_menu is not None):
        return parent_menu
    else:
        return False


def correct_supply_assignments(supply, supply_categories):

    supply_name = supply['supply']['name']
    #closest_key = find_closest_key(supply_name, SUPPLY_CATEGORIES_MAP, confidence_threshold=0.7)
    closest_key = find_key(supply_name, SUPPLY_CATEGORIES_MAP)

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

    shelters_without_coordinates = {}

    location_id = 0
    for shelter in shelters:
        if 'desativado' in shelter['name'].lower() or 'apagar' in shelter['name'].lower():
            create_log("info", f"O abrigo '{shelter['name']}' está desativado ou apagado")
            continue
        
        if not is_within_days(shelter['updatedAt'], MAX_TIME_SHELTER_UPDATE):
            continue
        
        latitude = shelter['latitude']
        longitude = shelter['longitude']

        if not shelter['id'].endswith('\r'):
            # Se as coordenadas não são validas, tenta obter elas do arquivo local
            if not is_valid_coordinates(latitude, longitude):
                shelter_name_key = sanitize_key(shelter['name'])
                coordinates = LOCATION_COORDINATES.get(shelter_name_key)

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
            overlayed_popup_content = create_location_overlayed_popup_content(shelter['id'])

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
                    supply_name_mapped_static = find_closest_key(supply_obj['supply']['name'], SUPPLIES_NAMES_MAP, confidence_threshold=0.9)
                    
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

def create_all_objects(save_processed_data):
    menus_group = create_menus_group_obj()
    menus = create_menus_obj(menus_group)
    locations = create_locations_obj()
    tags = create_tags_obj(menus, locations)   
    tags_related_locations = create_tag_related_location_obj(tags, locations)

    remove_empty_menus(menus)

    if save_processed_data:
        save_json(menus_group, "./data_collection/processed_data/menus_group.json")
        save_json(menus, "./data_collection/processed_data/menus.json")
        save_json(locations, "./data_collection/processed_data/locations.json")
        save_json(tags, "./data_collection/processed_data/tags.json")
        save_json(tags_related_locations, "./data_collection/processed_data/tags_related_locations.json")

    print(f"\nMenus: {len(menus)}")
    print(f"Locations: {len(locations)}")
    print(f"Tags: {len(tags)}")

    return menus_group, menus, locations, tags, tags_related_locations


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

def create_location_overlayed_popup_content(location_id):
    url = f"https://sos-rs.com/abrigo/{location_id}\""
    overlayed_popup_content = f"<div><iframe style=\"position: absolute; border: none; width: 100%; height: 100% !important;\" title=\"P&aacute;gina Incorporada\" src=\"{url}\"></iframe></div>"

    return overlayed_popup_content

def add_about_location(locations, location_id):
    overlayed_popup_content = """
        <div style="position: absolute; border: none; width: 100%; height: 100% !important; overflow-y: auto;">
        <p style="text-align: left;">&nbsp;</p>
        <div style="margin: 1px 35px 0px 35px;">
        <p style="text-align: left;">O Mapa Interativo de Doa&ccedil;&otilde;es &eacute; uma iniciativa de alunos do Instituto de Inform&aacute;tica da UFRGS e volunt&aacute;rios, com apoio limitado da RNP. Este mapa visa facilitar a visualiza&ccedil;&atilde;o dos itens de doa&ccedil;&atilde;o que os locais necessitam, proporcionando uma plataforma centralizada e acess&iacute;vel para quem deseja ajudar.</p>
        <h3 style="text-align: left;">Volunt&aacute;rios e Apoiadores</h3>
        <ul style="text-align: left;">
        <li>Ana Laura Lumertz Schardosim (INF-UFRGS)</li>
        <li>Eduardo Raupp Peretto (INF-UFRGS)</li>
        <li>Fernanda da Silva Bonetti</li>
        <li>Gabriel Vassoler (RNP)</li>
        <li>Gustavo Hermínio de Araújo (RNP)</li>
        <li>Iara Machado (RNP)</li>
        <li>Leonardo Lauryel Batista dos Santos</li>
        <li>Lisandro Zambenedetti Granville (RNP)</li>
        <li>Luciano Paschoal Gaspary (INF-UFRGS)</li>
        <li>Manoel Narciso Reis Soares Filho (INF-UFRGS)</li>
        <li>Marcos Schwarz (RNP)</li>
        </ul>
        <h3 style="color: #0056b3; text-align: left;"><span style="color: #000000;">Contato</span></h3>
        <p style="text-align: left;">Para mais informa&ccedil;&otilde;es, entre em contato conosco pelo email: <a style="color: #0056b3; text-decoration: none;" href="mailto:gabriel.vassoler@rnp.br">gabriel.vassoler@rnp.br</a></p>
        <h3 style="color: #0056b3; text-align: left;"><span style="color: #000000;">Agradecimentos</span></h3>
        <p style="text-align: left;">Agradecemos &agrave; equipe do <a href="https://sos-rs.com/" target="_blank" rel="noopener">SOS-RS</a> pela disponibiliza&ccedil;&atilde;o dos dados para este mapa de filtros.</p>
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

def fetch_location_and_name_mapping_data():
    try:
        global SUPPLIES_NAMES_MAP
        SUPPLIES_NAMES_MAP = fetch_json(SUPPLY_NAMES_MAP_URL, SUPPLY_NAMES_MAP_LOCAL)
        print("Dados de supplyNamesMap obtidos com sucesso\n")
    except RuntimeError as e:
        print(e)
    
    try:
        global SUPPLY_CATEGORIES_MAP
        SUPPLY_CATEGORIES_MAP = fetch_json(SUPPLY_CATEGORIES_MAP_URL, SUPPLY_CATEGORIES_MAP_LOCAL)
        print("Dados de supplyCategoriesMap obtidos com sucesso\n")
    except RuntimeError as e:
        print(e)
    
    try:
        global LOCATION_COORDINATES
        LOCATION_COORDINATES = fetch_json(LOCATION_COORDINATES_URL, LOCATION_COORDINATES_LOCAL)
        print("Dados de supplyCategoriesMap obtidos com sucesso\n")
    except RuntimeError as e:
        print(e)


if __name__ == '__main__':
    save_processed_data = False

    if 'save-processed-data' in sys.argv:
        save_processed_data = True

    fetch_location_and_name_mapping_data()
    menus_group, menus, locations, tags, tags_related_locations = create_all_objects(save_processed_data)

    sql_commands = create_all_sql_commands(menus_group, menus, locations, tags, tags_related_locations)
    write_sql_commands(sql_commands, OUTPUT_FILE)

    save_logs('all')