from datetime import datetime
from core.config import load_config

def log_request(address, path, status):
    config = load_config()
    log_file = config.get("log_file", "access.log")
    log = f"{datetime.now().strftime('%Y/%m-%d %H:%M')} - {address[0]} {path} -> {status}\n"
    print(log.strip())
    with open(log_file, "a") as f:
        f.write(log)

def log_print(message):
    
    log = f"LOG -> [{datetime.now().strftime('%Y/%m/%d %H:%M:%S')}] {message}"
    print(f"{log}")

    append_log(log)

def error_print(message):
    config = load_config()
    debug = config.get("debug",True)

    if(not debug):
        return
    
    log = f"ERROR -> [{datetime.now().strftime('%Y/%m/%d %H:%M:%S')}] {message}"
    print(f"{log}")
    append_log(log)

def debug_log(message):
    config = load_config()
    debug = config.get("debug",True)

    if(not debug):
        return
    
    log = f"DEBUG -> {message}"
    print(log)

    append_log(log)


def append_log(message):
    config = load_config()
    debug = config.get("debug",True)
    
    log_file = config.get("log_file", "access.log")
    with open(log_file, "a") as f:
        f.write(message+'\n')

def clear_log():
    config = load_config()
    clear_log = config.get("clear_log",False)
    
    log_file = config.get("log_file", "access.log")
    with open(log_file, "w") as f:
        pass