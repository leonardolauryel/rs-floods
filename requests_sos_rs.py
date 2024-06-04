from constants import *

import requests

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
