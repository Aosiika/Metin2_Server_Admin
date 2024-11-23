# server_config.py
import json
import os

# Configuración del servidor de Metin2
CONFIG_FILE = os.path.join("config", "server_config.json")

def load_server_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        return {
            "host": "127.0.0.1",  # Dirección IP del servidor
            "port": 3306,           # Puerto de conexión (por ejemplo, para MySQL)
            "user": "admin",       # Usuario para la base de datos
            "password": "password", # Contraseña de la base de datos
            "database": "player",  # Base de datos del servidor de Metin2
            "theme": "light",      # Tema de la aplicación, 'light' o 'dark'
            "language": "es"       # Idioma de la aplicación, 'es' o 'en'
        }

def save_server_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def save_version_config(config):
    with open("server_config.json", "w") as f:
        json.dump(config, f, indent=4)