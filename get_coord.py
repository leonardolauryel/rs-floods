import requests
import utils
import json
import unicodedata
import re

def sanitize_key(s):
    # Normaliza para forma NFKD e depois converte para ASCII ignorando erros de conversão
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
    # Substitui qualquer coisa que não seja letra, número ou sublinhado por uma string vazia
    return re.sub(r'[^\w]+', '', s)

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

def get_location_google_api(api_key, endereco):
    """
    Busca as coordenadas geográficas de um endereço usando a Google Geocoding API com a biblioteca requests.

    Args:
        api_key (str): Chave de API do Google Maps.
        endereco (str): Endereço para o qual as coordenadas serão buscadas.

    Returns:
        tuple: Retorna um par (latitude, longitude) se encontrado, caso contrário retorna None.
    """
    # URL base da API de Geocoding
    url_base = "https://maps.googleapis.com/maps/api/geocode/json"

    # Parâmetros para a requisição GET
    parametros = {
        'address': endereco,
        'key': api_key
    }

    # Realizar a requisição GET
    resposta = requests.get(url_base, params=parametros)



    # Processar a resposta
    if resposta.status_code == 200:
        resultado = resposta.json()
        if resultado['results']:
            results = resultado['results']
            return results
        else:
            return None
    else:
        print("Erro na requisição:", resposta.status_code)
        return None


loc_coord = {}
errors = []
chave_api = 'TOKEN'  # Substitua por sua chave de API real

filename = "coordinates_data.json"

locations = {'EspacoPetIgrejaAuxiliadora': {'name': 'Espaço Pet Igreja Auxiliadora', 'address': 'Rua 24 de outubro 1751'}}







try:
    location_lat_lng = read_json(filename)
    print("Dados json de location_lat_lng carregados com sucesso.\n")
except Exception as e:
    print("Falha ao ler o arquivo JSON.\n")


loc_many_coord = {}

for location in locations.values():
    try:
        results = get_location_google_api(chave_api, f"{location['name']} - {location['address']} - RS")

        if (len(results) == 1):
            loc_coord[sanitize_key(location['name'])] = {
                'name': location['name'],
                'address': results[0]['formatted_address'],
                'lat': results[0]['geometry']['location']['lat'],
                'lng': results[0]['geometry']['location']['lng']
            }
        elif (len(results) == 0):
            print(f"Nenhuma localização encontrada para o local: {location}")
            errors.append(location)
        else:
            print(results)
            loc_many_coord[sanitize_key(location['name'])] = []
            for result in results:
                loc_many_coord[sanitize_key(location['name'])].append(
                    {
                        'name': location['name'],
                        'address': result['formatted_address'],
                        'lat': result['geometry']['location']['lat'],
                        'lng': result['geometry']['location']['lng']
                    }
                )
            
            print(f"Mais de uma localização encontrada para o local: {location}")

    except Exception as e:
        print(f"Erro {location}")
        print(e)
        errors.append(location)

print("\n\nMuitas localizações encontradas:")
print(loc_many_coord)

print("\n\nFalha ao obter as coordenadas de:")
print(errors)

save_json(loc_coord, filename)
