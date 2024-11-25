import pymysql
import json
import os

# Definir la ruta al archivo de configuración JSON
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'server_config.json')

# Función para cargar la configuración del servidor desde el archivo JSON
def load_server_config():
    """Carga la configuración del servidor desde el archivo JSON."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error al cargar el archivo de configuración: {e}")
        return None

# Función para actualizar el estado de la cuenta en la base de datos
def update_account_status_in_db(account_id, new_status):
    """
    Actualiza el estado de una cuenta en la base de datos.

    :param account_id: ID de la cuenta a actualizar.
    :param new_status: Nuevo estado de la cuenta (OK o BLOCK).
    """
    # Cargar configuración desde el archivo JSON
    config = load_server_config()
    if config is None:
        raise Exception("No se pudo cargar la configuración del servidor.")

    # Conectar a la base de datos
    connection = pymysql.connect(
        host=config["host"],
        user=config["user"],
        password=config["password"],
        database=config["db_account_name"],  # Usar la base de datos de cuentas
        port=config["port"],
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            # Actualizar el estado de la cuenta en la tabla
            cursor.execute("UPDATE account SET status = %s WHERE id = %s", (new_status, account_id))
            connection.commit()
            print(f"Estado de la cuenta con ID {account_id} actualizado a {new_status}")

    except Exception as e:
        print(f"Error al actualizar la base de datos: {e}")
        raise

    finally:
        connection.close()
