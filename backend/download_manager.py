# download_manager.py
import requests
import os

def download_file(url, path, progress_callback=None):
    """
    Descarga un archivo desde una URL y lo guarda en la ruta especificada.
    :param url: URL del archivo a descargar.
    :param path: Ruta donde se guardará el archivo descargado.
    :param progress_callback: Función callback opcional para monitorear el progreso.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Levanta una excepción para códigos de error HTTP

        total_length = int(response.headers.get('content-length', 0))
        chunk_size = 1024
        downloaded = 0

        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback:
                        progress_callback(int((downloaded / total_length) * 100))

        return True, None  # Éxito

    except requests.exceptions.RequestException as e:
        return False, str(e)  # Error de red u otro problema

    except Exception as e:
        return False, str(e)  # Error general

