import sys
import os

# Adiciona o diretório pai ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from requests_sos_rs import *
from utils import save_json

def fetch_raw_data():
    # Menus
    supply_categories = fetch_supply_categories_data()

    # Locations
    shelters = fetch_shelter_data()

    # Tags
    supplies = fetch_supplies_data()

    return supply_categories, shelters, supplies

def save_raw_data(supply_categories, shelters, supplies):
    save_json(supply_categories, "./data_collection/raw_data/supply_categories.json")
    save_json(shelters, "./data_collection/raw_data/shelters.json")
    save_json(supplies, "./data_collection/raw_data/supplies.json")


if __name__ == "__main__":
    supply_categories, shelters, supplies = fetch_raw_data()
    save_raw_data(supply_categories, shelters, supplies)