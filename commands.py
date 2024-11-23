# commands.py
import os

def execute_server_command(command):
    # Esta función ejecutará comandos en el servidor
    try:
        result = os.popen(command).read()
        return result
    except Exception as e:
        return f"Error al ejecutar el comando: {e}"

def restart_server():
    print("Reiniciando el servidor de Metin2...")
    result = execute_server_command("/etc/init.d/metin2 restart")
    print(result)
