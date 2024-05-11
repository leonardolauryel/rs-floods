import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Desativa o logging
logging.disable(logging.DEBUG)
#logging.disable(logging.INFO)
#logging.disable(logging.WARNING)
#logging.disable(logging.ERROR)
#logging.disable(logging.CRITICAL)

debug_messages = []
info_messages = []
warning_messages = []
error_messages = []
critical_messages = []

def create_log(type, message):
    match type:
        case "debug":
            logging.debug(message)
            debug_messages.append(message)
        case "info":
            logging.info(message)
            info_messages.append(message)
        case "warning":
            logging.warning(message)
            warning_messages.append(message)
        case "error":
            logging.error(message)
            error_messages.append(message)
        case "critical":
            logging.critical(message)
            critical_messages.append(message)
        case _:
            msg = "Tipo informado para o log incorreto"
            logging.error(msg)
            error_messages.append(msg)

def get_logs(type):
    match type:
        case "debug":
            return debug_messages.copy()
        case "info":
            return info_messages.copy()
        case "warning":
            return warning_messages.copy()
        case "error":
            return error_messages.copy()
        case "critical":
            return critical_messages.copy()

    