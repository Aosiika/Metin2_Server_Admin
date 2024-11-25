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

# Función para crear o actualizar GM en la base de datos
def create_gm(account_name, character_name, authority_level):
    """
    Función para crear o actualizar un GM en la base de datos.
    
    :param account_name: Nombre de la cuenta del usuario
    :param character_name: Nombre del personaje
    :param authority_level: Nivel de autoridad que se le asignará
    """
    # Cargar configuración desde el archivo JSON
    config = load_server_config()
    if config is None:
        print("No se pudo cargar la configuración del servidor.")
        return
    
    # Conectar a la base de datos común
    connection = pymysql.connect(
        host=config["host"],
        user=config["user"],
        password=config["password"],
        database=config["db_common_name"],  # Usar la base de datos común
        port=config["port"],
        cursorclass=pymysql.cursors.DictCursor
    )
    
    try:
        with connection.cursor() as cursor:
            # Verificar si el personaje ya está en la tabla gmlist
            cursor.execute("SELECT * FROM gmlist WHERE mAccount = %s", (account_name,))
            existing_gm = cursor.fetchone()
            
            if existing_gm:
                # Actualizar el nivel de autoridad si ya existe
                cursor.execute(
                    "UPDATE gmlist SET mAuthority = %s WHERE mAccount = %s",
                    (authority_level, account_name)
                )
            else:
                # Insertar un nuevo registro en gmlist si no existe
                cursor.execute(
                    "INSERT INTO gmlist (mAccount, mName, mContactIP, mServerIP, mAuthority) VALUES (%s, %s, %s, %s, %s)",
                    (account_name, character_name, "ALL", "ALL", authority_level)
                )
            
            # Guardar cambios
            connection.commit()
            print(f"Personaje '{character_name}' actualizado como {authority_level} para la cuenta '{account_name}'")
    
    except Exception as e:
        print(f"Error al actualizar la base de datos: {e}")
    
    finally:
        connection.close()