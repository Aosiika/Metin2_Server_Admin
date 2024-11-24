# Archivo: backend/update_manager.py
import requests
from PyQt5.QtCore import QThread, pyqtSignal

class UpdateThread(QThread):
    update_progress = pyqtSignal(int)
    update_complete = pyqtSignal(bool)

    def __init__(self, update_url, output_path):
        super(UpdateThread, self).__init__()
        self.update_url = update_url
        self.output_path = output_path

    def run(self):
        try:
            response = requests.get(self.update_url, stream=True)
            total_length = response.headers.get('content-length')

            if total_length is None:
                # No se pudo obtener el tamaño del archivo
                self.update_complete.emit(False)
                return

            total_length = int(total_length)
            downloaded_size = 0

            with open(self.output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=4096):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        progress = int(100 * downloaded_size / total_length)
                        self.update_progress.emit(progress)

            # Descarga completa
            self.update_complete.emit(True)

        except Exception as e:
            print(f"Error al intentar descargar la actualización: {str(e)}")
            self.update_complete.emit(False)
