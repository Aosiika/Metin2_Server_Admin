# database.py
import pymysql
import hashlib
from server_config import load_server_config

def connect_to_database():
    config = load_server_config()
    try:
        connection = pymysql.connect(
            host=config["host"],
            user=config["user"],
            password=config["password"],
            database=config["database"],
            port=config["port"],
            cursorclass=pymysql.cursors.DictCursor  # Asegurar que los resultados sean diccionarios
        )
        return connection
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

def get_all_accounts():
    connection = connect_to_database()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, login, status, last_play, create_time FROM account")
                accounts = cursor.fetchall()
                return accounts, None
        except Exception as e:
            print(f"Error al obtener cuentas: {e}")
            return None, str(e)
        finally:
            connection.close()
    return None, "No se pudo conectar a la base de datos"

def update_account_status(account_id, new_status):
    connection = connect_to_database()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE account SET status = %s WHERE id = %s", (new_status, account_id))
                connection.commit()
                return True
        except Exception as e:
            print(f"Error al actualizar el estado de la cuenta: {e}")
        finally:
            connection.close()
    return False

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
                return True
        except Exception as e:
            print(f"Error al crear la cuenta: {e}")
        finally:
            connection.close()
    return False

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
                cursor.execute("SELECT id, name FROM player WHERE account_id = %s", (account_id,))
                characters = cursor.fetchall()
                return characters, None
        except Exception as e:
            print(f"Error al obtener personajes: {e}")
            return None, str(e)
        finally:
            connection.close()
    return None, "No se pudo conectar a la base de datos"

def get_server_statistics():
    # Cambiar a la base de datos srv1_player para obtener las estadísticas
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
                cursor.execute("SELECT COUNT(*) AS online_users FROM srv1_account.account WHERE status = 'online'")
                online_users = cursor.fetchone()

                cursor.execute("SELECT COUNT(*) AS total_characters FROM srv1_player.player")
                total_characters = cursor.fetchone()

                return {
                    "online_users": online_users["online_users"],
                    "total_characters": total_characters["total_characters"]
                }, None
        except Exception as e:
            print(f"Error al obtener estadísticas del servidor: {e}")
            return None, str(e)
        finally:
            connection.close()
    return None, "No se pudo conectar a la base de datos"