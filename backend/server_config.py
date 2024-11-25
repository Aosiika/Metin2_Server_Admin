# server_config.py
import json
import os

# Ruta al archivo de configuración del servidor de Metin2
CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config', 'server_config.json')

def load_server_config():
    """Carga la configuración del servidor desde el archivo de configuración."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error al cargar el archivo de configuración: {e}")
            return None
    else:
        # Si no existe el archivo de configuración, devuelve valores predeterminados
        return {
            "host": "127.0.0.1",      # Dirección IP del servidor
            "port": 3306,             # Puerto de conexión (ej. para MySQL)
            "user": "admin",          # Usuario para la base de datos
            "password": "password",   # Contraseña de la base de datos
            "db_account_name": "account",  # Nombre de la base de datos de cuentas
            "db_common_name": "common",    # Nombre de la base de datos común
            "db_player_name": "player",    # Nombre de la base de datos de jugadores
            "theme": "light",         # Tema de la aplicación, 'light' o 'dark'
            "language": "es"          # Idioma de la aplicación, 'es' o 'en'
        }

def save_server_config(config):
    """Guarda la configuración actual en el archivo de configuración."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error al guardar el archivo de configuración: {e}")