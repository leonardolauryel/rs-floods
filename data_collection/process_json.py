import json
from collections import defaultdict

from save_data_sos_rs import fetch_raw_data
from utils import save_json, find_closest_key, find_key, fetch_json
from constants import *

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

def process_json(input_json, map_supply_names):
    # Parse the input JSON
    data = json.loads(input_json)
    
    # Create a dictionary to hold the supply categories and their items
    category_dict = defaultdict(list)
    
    # Populate the dictionary
    txt = []
    for item in data:
        category_name = item['supplyCategory']['name']

        item_name = item['name']
        
        if map_supply_names:
            # Mapeia o nome de suprimentos
            item_name_mapped = find_closest_key(item['name'], SUPPLIES_NAMES_MAP, confidence_threshold=0.9)
            if item_name_mapped is not None:
                item_name = item_name_mapped
                txt.append(f"{item['name']:<30} ->   {item_name_mapped}")

            # Coloca suprimentos na categoria correta
            closest_key = find_key(item_name, SUPPLY_CATEGORIES_MAP)
            # Encontrou uma categoria
            if closest_key is not None:
                category_name = closest_key
            
        category_dict[category_name].append(item_name)
    
    nome_arquivo = "./data_collection/relationship_data/name_map_0.9.txt"
    # Abrir o arquivo em modo de escrita e salvar o conteúdo
    with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
        for item in txt:
            arquivo.write(item + '\n')

    if map_supply_names:
        for category in category_dict:
            category_dict[category] = sorted(set(category_dict[category]))
    else:
        for category in category_dict:
            category_dict[category].sort()

    # Convert the dictionary to a regular dict and sort the keys
    sorted_category_dict = dict(sorted(category_dict.items()))

    return sorted_category_dict


supply_categories, shelters, supplies = fetch_raw_data()
fetch_location_and_name_mapping_data()

input_json = json.dumps(supplies)

output_json = process_json(input_json, False)
save_json(output_json, "./data_collection/relationship_data/category-supply_relationship_data.json")

output_json_mapped = process_json(input_json, True)
save_json(output_json_mapped, "./data_collection/relationship_data/category-supply_relationship_data_mapped.json")
