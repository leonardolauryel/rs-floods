import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Desativa o logging
logging.disable(logging.DEBUG)
logging.disable(logging.INFO)
logging.disable(logging.WARNING)
logging.disable(logging.ERROR)
logging.disable(logging.CRITICAL)

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
    data = []
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
        case "all":
            if len(debug_messages):
                data.append("\n\nDEBUG")
                for debug_message in sorted(debug_messages):
                    data.append(debug_message)
            
            if len(info_messages):
                data.append("\n\nINFO")
                for info_message in sorted(info_messages):
                    data.append(info_message)
            
            if len(warning_messages):
                data.append("\n\nWARNING")
                for warning_message in sorted(warning_messages):
                    data.append(warning_message)
                
            if len(error_messages):
                data.append("\n\nERROR")
                for error_message in sorted(error_messages):
                    data.append(error_message)
            
            if len(critical_messages):
                data.append("\n\nCRITICAL")
                for critical_message in sorted(critical_messages):
                    data.append(critical_message)

    with open('logs.txt', 'w') as file:
        for log in data:
            file.write(f"{log}\n")

    