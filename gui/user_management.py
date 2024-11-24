import os
import datetime
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from backend.database import get_all_accounts, get_all_characters

class UserManagementWidget(QWidget):
    def __init__(self):
        super(UserManagementWidget, self).__init__()
        self.translations = self.load_translations()  # Cargar las traducciones al inicializar
        self.init_ui()

    def load_translations(self):
        # Este método se asegura de cargar las traducciones.
        import json
        with open('translations.json', 'r', encoding='utf-8') as file:
            translations = json.load(file)
        return translations.get("es", {})  # Utiliza 'es' como el idioma predeterminado, cambia si es necesario

    def init_ui(self):
        layout = QVBoxLayout()

        # Botón para cargar cuentas
        self.load_accounts_button = QPushButton(self.translations["load_accounts_button"])
        self.load_accounts_button.clicked.connect(self.load_accounts)
        layout.addWidget(self.load_accounts_button)

        # Tabla de cuentas
        self.accounts_table = QTableWidget()
        self.accounts_table.setColumnCount(4)
        self.accounts_table.setHorizontalHeaderLabels([
            self.translations["account_id"],
            self.translations["name"],
            self.translations["status_label"],
            self.translations["created_at"],
        ])
        self.accounts_table.cellClicked.connect(self.load_characters)
        layout.addWidget(self.accounts_table)

        # Tabla de personajes asociados
        self.characters_table = QTableWidget()
        layout.addWidget(QLabel(self.translations["associated_characters"]))
        layout.addWidget(self.characters_table)

        # Establecer el layout al widget
        self.setLayout(layout)

    def load_accounts(self):
        accounts, error = get_all_accounts()

        if error:
            QMessageBox.critical(self, "Error", self.translations["error_fetching_accounts"].format(error=error))
            return

        self.accounts_table.setRowCount(len(accounts))
        for row, account in enumerate(accounts):
            self.accounts_table.setItem(row, 0, QTableWidgetItem(str(account["id"])))
            self.accounts_table.setItem(row, 1, QTableWidgetItem(account["login"]))
            self.accounts_table.setItem(row, 2, QTableWidgetItem(account["status"]))
            created_at = account.get("create_time", "N/A")
            if isinstance(created_at, datetime.datetime):
                created_at = created_at.strftime("%Y-%m-%d %H:%M:%S")
            self.accounts_table.setItem(row, 3, QTableWidgetItem(created_at))

    def load_characters(self, row, column):
        account_id = self.accounts_table.item(row, 0).text()
        characters, error = get_all_characters(account_id)

        if error:
            QMessageBox.critical(self, "Error", self.translations["error_fetching_characters"])
            return

        if not characters:
            QMessageBox.information(self, "Información", self.translations["error_no_characters"])
            return

        self.characters_table.setRowCount(len(characters))
        self.characters_table.setColumnCount(4)
        self.characters_table.setHorizontalHeaderLabels([
            self.translations["character_name"],
            self.translations["character_type"],
            self.translations["character_gender_label"],
            self.translations["character_last_play"],
        ])

        # Mapeo de los valores de job a imágenes y nombres de personajes
        job_mapping = {
            0: ("warrior", "Guerrero", "m"),
            4: ("warrior", "Guerrera", "w"),
            5: ("assassin", "Ninja", "m"),
            1: ("assassin", "Ninja", "w"),
            2: ("sura", "Sura", "m"),
            6: ("sura", "Sura", "w"),
            7: ("shaman", "Chamán", "m"),
            3: ("shaman", "Chamán", "w"),
            8: ("wolfman", "Lycan", "m")
        }

        for row_idx, character in enumerate(characters):
            character_job = character.get("job", -1)
            
            # Validar si el `job` es reconocido, de lo contrario, mostrar un mensaje y usar valores predeterminados
            if character_job in job_mapping:
                job_type, job_name, gender_suffix = job_mapping[character_job]
                image_path = os.path.join("resources", "characters", f"{job_type}_{gender_suffix}.jpg")

                # Verificar si la imagen existe
                if not os.path.exists(image_path):
                    print(f"Imagen no encontrada: {image_path}. Cargando imagen por defecto.")
                    image_path = os.path.join("resources", "characters", "default.jpg")
            else:
                # Mostrar un mensaje si el `job` no es reconocido y cargar valores predeterminados
                print(f"Trabajo no reconocido: {character_job}. Cargando imagen por defecto.")
                job_name = "Desconocido"
                image_path = os.path.join("resources", "characters", "default.jpg")

            # Añadir la imagen al widget
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                print(f"Error al cargar la imagen: {image_path}. Verifique la ruta y el archivo.")
                image_path = os.path.join("resources", "characters", "default.jpg")
                pixmap = QPixmap(image_path)

            pixmap = pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label = QLabel()
            image_label.setPixmap(pixmap)
            self.characters_table.setCellWidget(row_idx, 0, image_label)

            # Añadir el nombre, tipo y última conexión
            self.characters_table.setItem(row_idx, 1, QTableWidgetItem(character.get("name", "Desconocido")))
            self.characters_table.setItem(row_idx, 2, QTableWidgetItem(job_name))
            last_play = character.get("last_play", "N/A")
            if isinstance(last_play, datetime.datetime):
                last_play = last_play.strftime("%Y-%m-%d %H:%M:%S")
            self.characters_table.setItem(row_idx, 3, QTableWidgetItem(last_play))


     
    def update_status(self):
        selected_row = self.accounts_table.currentRow()
        if selected_row == -1:
            error_label = QLabel("Please select an account to update status.")
            self.layout.addWidget(error_label)
            return

        account_id = self.accounts_table.item(selected_row, 0).text()
        current_status = self.accounts_table.item(selected_row, 2).text()

        # Cambiar el estado
        new_status = "BLOCK" if current_status == "OK" else "OK"

        # Actualizar el estado de la cuenta
        success = update_account_status(account_id, new_status)
        if success:
            self.accounts_table.setItem(selected_row, 2, QTableWidgetItem(new_status))
        else:
            error_label = QLabel("Failed to update account status.")
            self.layout.addWidget(error_label)