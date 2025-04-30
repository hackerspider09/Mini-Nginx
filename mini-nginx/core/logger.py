from datetime import datetime
from core.config import load_config

def log_request(address, path, status):
    config = load_config()
    log_file = config.get("log_file", "access.log")
    log = f"{datetime.now()} - {address[0]} {path} -> {status}\n"
    print(log.strip())
    with open(log_file, "a") as f:
        f.write(log)

def log_print(message):
    print(f"LOG -> {message}")

def error_print(message):
    print(f"ERROR -> {message}")

def debug_log(msg):
    config = load_config()
    debug = config.get("debug",True)

    if(not debug):
        return
    
    log_file = config.get("log_file", "access.log")
    log = f"DEBUG -> {msg} \n"
    print(log.strip())
    with open(log_file, "a") as f:
        f.write(log)