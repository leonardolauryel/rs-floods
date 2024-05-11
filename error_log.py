import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

error_messages = []

def log_error(message):
    logging.error(message)
    error_messages.append(message)

def get_errors():
    """Retorna uma cópia da lista de mensagens de erro."""
    return error_messages.copy()