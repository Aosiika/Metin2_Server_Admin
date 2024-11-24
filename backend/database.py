# database.py (actualizado)

import pymysql
import json
import os
import hashlib
from backend.server_config import load_server_config
from datetime import datetime, timedelta

# Ruta al archivo de configuración 'server_config.json' en la carpeta 'config'
CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'server_config.json')

def load_db_config():
    """Carga la configuración de la base de datos desde el archivo 'server_config.json'."""
    try:
        with open(CONFIG_FILE_PATH, 'r') as config_file:
            db_config = json.load(config_file)
        return db_config
    except Exception as e:
        print(f"Error al cargar la configuración de la base de datos: {e}")
        return None

def connect_to_database(db_name):
    """Conecta a la base de datos usando la configuración cargada desde 'server_config.json'."""
    db_config = load_db_config()

    if not db_config:
        return None, "No se pudo cargar la configuración de la base de datos"

    try:
        connection = pymysql.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            port=db_config['port'],
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection, None
    except Exception as e:
        return None, str(e)

def get_all_accounts():
    connection, error = connect_to_database("srv1_account")

    if error:
        # Si hay un error, retornarlo para manejarlo en la lógica de carga de cuentas
        return None, error

    try:
        with connection.cursor() as cursor:
            # Consultar todas las cuentas
            cursor.execute("SELECT id, login, status, create_time FROM account")
            accounts = cursor.fetchall()
        return accounts, None
    except Exception as e:
        return None, f"Error fetching accounts: {str(e)}"
    finally:
        if connection:
            connection.close()

def get_all_characters(account_id):
    # Cambiar a la base de datos srv1_player para obtener los personajes
    config = load_server_config()
    config["database"] = "srv1_player"
    connection = pymysql.connect(
        host=config["host"],
        user=config["user"],
        password=config["password"],
        database=config["database"],
        port=config["port"],
        cursorclass=pymysql.cursors.DictCursor
    )
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, name, job, last_play FROM player WHERE account_id = %s", (account_id,))
                characters = cursor.fetchall()
                return characters, None
        except Exception as e:
            print(f"Error al obtener personajes: {e}")
            return None, str(e)
        finally:
            connection.close()
    return None, "No se pudo conectar a la base de datos"

def create_account(login, password):
    # Generar hash SHA1 doble en mayúsculas
    first_sha1 = hashlib.sha1(password.encode()).digest()
    double_sha1 = hashlib.sha1(first_sha1).hexdigest().upper()
    formatted_password = f"*{double_sha1}"

    connection = connect_to_database()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO account (login, password, status) VALUES (%s, %s, %s)", (login, formatted_password, 'OK'))
                connection.commit()
                return True, None
        except Exception as e:
            print(f"Error al crear la cuenta: {e}")
            return False, str(e)
        finally:
            connection.close()
    return False, "No se pudo conectar a la base de datos"

def get_server_statistics():
    try:
        # Conectar a la base de datos srv1_account
        connection_account, error_account = connect_to_database("srv1_account")
        if error_account:
            return None, error_account

        # Obtener el total de cuentas creadas
        with connection_account.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS total_accounts FROM account")
            total_accounts = cursor.fetchone()['total_accounts']

            # Obtener el total de cuentas creadas en los últimos 10 minutos
            ten_minutes_ago = datetime.now() - timedelta(minutes=10)
            cursor.execute("SELECT COUNT(*) AS accounts_created_last_10_min FROM account WHERE create_at >= %s", (ten_minutes_ago,))
            accounts_created_last_10_min = cursor.fetchone()['accounts_created_last_10_min']

        connection_account.close()

        # Conectar a la base de datos srv1_player para obtener el total de personajes
        connection_player, error_player = connect_to_database("srv1_player")
        if error_player:
            return None, error_player

        with connection_player.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS total_characters FROM player")
            total_characters = cursor.fetchone()['total_characters']

        connection_player.close()

        # Obtener el total de usuarios activos en los últimos 10 minutos
        # Esto dependerá de cómo se está definiendo "usuario activo"
        # Aquí voy a asumir que tenemos una columna `availDt` en la tabla `account`
        connection_account, error_account = connect_to_database("srv1_account")
        if error_account:
            return None, error_account

        with connection_account.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS active_users_last_10_min FROM account WHERE availDt >= %s", (ten_minutes_ago,))
            active_users_last_10_min = cursor.fetchone()['active_users_last_10_min']

        connection_account.close()

        # Devolver los datos obtenidos
        return {
            "total_accounts": total_accounts,
            "total_characters": total_characters,
            "accounts_created_last_10_min": accounts_created_last_10_min,
            "active_users_last_10_min": active_users_last_10_min
        }, None

    except Exception as e:
        return None, str(e)

def update_account_status(account_id, new_status):
    connection = connect_to_database()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE account SET status = %s WHERE id = %s", (new_status, account_id))
                connection.commit()
                return True
        except Exception as e:
            print(f"Error updating account status: {e}")
            return False
        finally:
            connection.close()
    return False
