import random
import unicodedata
import re
import json
from datetime import datetime, timedelta
import pytz
import difflib
import urllib.parse
import requests


def is_valid_coordinates(latitude, longitude):
    # Check if the coordinates are not None
    if latitude is None or longitude is None:
        return False
    
    # Check if the latitude and longitude are within valid ranges
    if -90 <= latitude <= 90 and -180 <= longitude <= 180:
        return True
    else:
        return False

def is_valid_tag_id_location_id(tag_id, location_id):
    if tag_id is not None and location_id is not None:
        return True
    else:
        False

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

def remove_accents(text):
    # Normalize the string to the NFD form (where accents are separated from letters)
    normalized_text = unicodedata.normalize('NFD', text)
    # Filter out all characters that are combining marks (accents)
    text_without_accents = ''.join(char for char in normalized_text if not unicodedata.combining(char))
    return text_without_accents

def generate_random_hex_color():
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

def fetch_json(url, local_file):
    try:
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path
        file_name_remote = path.split('/')[-1]

        # Try to download the JSON data from the URL
        print(f"Acessando {file_name_remote} remoto")

        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
        data = response.json()
    except (requests.exceptions.RequestException, json.JSONDecodeError):
        # If downloading fails or JSON decoding fails, try to read the local file
        print(f"Falha ao acessar {file_name_remote} remoto")
        print(f"Acessando {local_file} local")
        try:
            with open(local_file, 'r') as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # If the local file is not found or JSON decoding fails, raise an error
            raise RuntimeError(f"Failed to load JSON data from both URL and local file: {e}")
    return data

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

def create_link_google_maps(latitude, longitude):
    base_url = "https://www.google.com/maps/?q="
    return f"{base_url}{latitude},{longitude}"

def converter_utc_para_brasilia(utc_time_str):
    """
    Converte uma data e hora em formato UTC para o horário de Brasília e retorna em formato legível.

    Args:
    utc_time_str (str): Data e hora em formato UTC (ex: "2024-05-07T17:32:49.810Z").

    Returns:
    str: Data e hora no formato DD/MM/YYYY HH:MM:SS no horário de Brasília.
    """
    # Converter a string para um objeto datetime em UTC
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")

    # Definir o fuso horário de Brasília
    brasilia_tz = pytz.timezone("America/Sao_Paulo")

    # Converter a hora UTC para hora de Brasília
    brasilia_time = utc_time.replace(tzinfo=pytz.utc).astimezone(brasilia_tz)

    # Formatar a data e hora de forma mais legível
    legible_time_str = brasilia_time.strftime("%d/%m/%Y %H:%M:%S")
    
    return legible_time_str

def normalize_text(text):
    # Normaliza o texto para remover acentos e converter para minúsculas
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII').lower()

def find_closest_key(search_word, dictionary, confidence_threshold=0.75):
    search_word = normalize_text(search_word)  # Normaliza a palavra de busca
    best_match_key = None
    best_match_ratio = 0  # Armazena a melhor correspondência de semelhança encontrada

    for key, values in dictionary.items():
        normalized_values = [normalize_text(value) for value in values]
        # Obtém as correspondências mais próximas na lista de valores normalizados e limita a uma correspondência
        matches = difflib.get_close_matches(search_word, normalized_values, n=1, cutoff=0.1)
        if matches:
            # Calcula a razão de semelhança para a melhor correspondência
            ratio = difflib.SequenceMatcher(None, search_word, matches[0]).ratio()
            if ratio > best_match_ratio:
                best_match_ratio = ratio
                if best_match_ratio >= confidence_threshold:
                    best_match_key = key
                else:
                    best_match_key = None

    return best_match_key

def is_within_days(date_str, days):
    # Convert the date string to a datetime object
    input_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    
    # Get the current date and time
    current_date = datetime.utcnow()
    
    # Calculate the difference in days
    delta = current_date - input_date
    
    # Check if the difference is within the specified days
    return delta <= timedelta(days=days)