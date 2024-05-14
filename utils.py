import random
import unicodedata
import re
import json
from datetime import datetime
import pytz


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