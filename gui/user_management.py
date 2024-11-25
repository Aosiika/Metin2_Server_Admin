# user_management.py
import os
import datetime
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QTableWidgetItem, QMessageBox, QWidget, QTableWidget, QLabel, QHeaderView, QLineEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from backend.database import get_all_accounts, get_all_characters
from backend.gm_manager import create_gm
from datetime import datetime

class UserManagementWidget(QWidget):
    def __init__(self):
        super(UserManagementWidget, self).__init__()
        self.all_accounts = []  # Inicializa la lista vacía de cuentas aquí
        self.translations = self.load_translations()  # Cargar las traducciones al inicializar
        self.init_ui()
        self.load_accounts()  # Carga las cuentas cuando se inicializa la interfaz
  
    def update_account_status(self, account_id, new_status):
        """
        Actualiza el estado de la cuenta en la base de datos.
        
        :param account_id: ID de la cuenta a actualizar.
        :param new_status: Nuevo estado (OK o BLOCK).
        """
        from backend.account_manager import update_account_status_in_db
        try:
            update_account_status_in_db(account_id, new_status)
            QMessageBox.information(self, "Éxito", f"Estado de la cuenta {account_id} actualizado a '{new_status}'")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar el estado de la cuenta: {e}") 
        
    def create_gm_action(self, account_name, character_name, authority_level):
        """
        Conecta la lógica para crear o actualizar un GM usando la función `create_gm()` de gm_manager.py.
        """
        create_gm(account_name, character_name, authority_level)
        
    def load_translations(self):
        # Este método se asegura de cargar las traducciones.
        import json
        with open('translations.json', 'r', encoding='utf-8') as file:
            translations = json.load(file)
        return translations.get("es", {})  # Utiliza 'es' como el idioma predeterminado, cambia si es necesario

    def init_ui(self):
        layout = QVBoxLayout()

        # Barra de búsqueda para cuentas
        self.account_search_box = QLineEdit()
        self.account_search_box.setPlaceholderText("Buscar cuenta por usuario...")
        self.account_search_box.textChanged.connect(self.filter_accounts)  # Filtrar en tiempo real mientras se escribe

        # Añadir la barra de búsqueda al layout
        layout.addWidget(self.account_search_box)
    
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
        accounts, error = get_all_accounts()  # Usa tu método para obtener las cuentas

        if error:
            QMessageBox.critical(self, "Error", "No se pudieron cargar las cuentas")
            return

        if not accounts:
            QMessageBox.information(self, "Información", "No se encontraron cuentas.")
            return
        
        self.all_accounts = accounts  # Guardar todas las cuentas en `self.all_accounts` para filtrado
        self.display_accounts(accounts)
        self.accounts_table.setRowCount(len(accounts))
        self.accounts_table.setColumnCount(5)  # Añadir una columna para el botón "Aceptar"
        self.accounts_table.setHorizontalHeaderLabels([
            "ID de Cuenta", "Nombre", "Estado", "Fecha de Creación", "Actualizar Estado"
        ])

        # Ajustar el comportamiento de la tabla para que las celdas se adapten al contenido
        self.accounts_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.accounts_table.horizontalHeader().setStretchLastSection(True)

        # Establecer una altura fija para todas las filas
        self.accounts_table.verticalHeader().setDefaultSectionSize(50)

        for row_idx, account in enumerate(accounts):
            # Añadir el ID de cuenta, nombre, estado y fecha de creación
            self.accounts_table.setItem(row_idx, 0, QTableWidgetItem(str(account.get("id", ""))))
            self.accounts_table.setItem(row_idx, 1, QTableWidgetItem(account.get("login", "")))
            self.accounts_table.setItem(row_idx, 2, QTableWidgetItem(account.get("status", "OK")))

            # Convertir create_time a cadena antes de asignarlo a la tabla
            create_time = account.get("create_time", "")
            if isinstance(create_time, datetime):
                create_time = create_time.strftime("%Y-%m-%d %H:%M:%S")  # Convertir datetime a una cadena legible
            self.accounts_table.setItem(row_idx, 3, QTableWidgetItem(str(create_time)))

            # Añadir el botón y el desplegable para actualizar el estado
            update_status_button = QPushButton("Aceptar")
            update_status_button.setFixedSize(100, 40)  # Establecer un tamaño fijo para el botón

            status_combobox = QComboBox()
            status_combobox.addItems(["OK", "BLOCK"])
            status_combobox.setFixedSize(100, 40)  # Establecer un tamaño fijo para el combo box

            # Crear un layout horizontal para el control del estado
            control_layout = QHBoxLayout()
            control_layout.addWidget(update_status_button)
            control_layout.addWidget(status_combobox)
            control_layout.setContentsMargins(5, 5, 5, 5)  # Añadir márgenes para dar espacio alrededor
            control_layout.setSpacing(10)  # Espaciado entre el botón y el combo box

            # Crear un QWidget para contener el layout y añadirlo a la celda de la tabla
            control_widget = QWidget()
            control_widget.setLayout(control_layout)
            self.accounts_table.setCellWidget(row_idx, 4, control_widget)

            # Conectar la lógica del botón al método update_account_status
            update_status_button.clicked.connect(lambda _, acc_id=account["id"], new_status=status_combobox: 
                                                self.update_account_status(acc_id, new_status.currentText()))

        # Forzar el refresco de la tabla
        self.accounts_table.viewport().update()

    def display_accounts(self, accounts):
            self.accounts_table.setRowCount(len(accounts))
            self.accounts_table.setColumnCount(4)
            self.accounts_table.setHorizontalHeaderLabels(["ID de Cuenta", "Nombre", "Estado", "Fecha de Creación"])
            for row_idx, account in enumerate(accounts):
                self.accounts_table.setItem(row_idx, 0, QTableWidgetItem(str(account["id"])))
                self.accounts_table.setItem(row_idx, 1, QTableWidgetItem(account["login"]))
                self.accounts_table.setItem(row_idx, 2, QTableWidgetItem(account["status"]))
                create_time_str = account["create_time"].strftime("%Y-%m-%d %H:%M:%S") if isinstance(account["create_time"], datetime) else "N/A"
                self.accounts_table.setItem(row_idx, 3, QTableWidgetItem(create_time_str))

    def filter_accounts(self):
        """Filtra las cuentas según el término de búsqueda ingresado."""
        search_term = self.account_search_box.text().strip().lower()
        filtered_accounts = [account for account in self.all_accounts if search_term in account["login"].lower()]
        self.display_accounts(filtered_accounts)

    def load_characters(self, row, column):
        account_id = self.accounts_table.item(row, 0).text()
        account_name = self.accounts_table.item(row, 1).text()  # Obtener el nombre de la cuenta
        characters, error = get_all_characters(account_id)
        

        if error:
            QMessageBox.critical(self, "Error", self.translations["error_fetching_characters"])
            return

        if not characters:
            QMessageBox.information(self, "Información", self.translations["error_no_characters"])
            return

        self.characters_table.setRowCount(len(characters))
        self.characters_table.setColumnCount(5)
        self.characters_table.setHorizontalHeaderLabels([
            self.translations["character_name"],
            self.translations["character_type"],
            self.translations["character_gender_label"],
            self.translations["character_last_play"],
            "Crear GM"
        ])

        # Ajustar el comportamiento de la tabla para que las celdas se adapten al contenido
        self.characters_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.characters_table.horizontalHeader().setStretchLastSection(True)

        # Establecer una altura fija para todas las filas (opción 1)
        self.characters_table.verticalHeader().setDefaultSectionSize(50)
    
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
            if isinstance(last_play, datetime):
                last_play = last_play.strftime("%Y-%m-%d %H:%M:%S")
            self.characters_table.setItem(row_idx, 3, QTableWidgetItem(last_play))

            #Añadir el botón y el desplegable para Crear GM
            create_gm_button = QPushButton("Crear GM")
            create_gm_button.setFixedSize(120, 40)  # Establecer un tamaño fijo para el botón

            authority_combobox = QComboBox()
            authority_combobox.addItems(["IMPLEMENTOR", "GOD", "LOW_WIZARD", "PLAYER"])
            authority_combobox.setFixedSize(120, 40)  # Establecer un tamaño fijo para el combo box

            # Crear un layout horizontal para el control de GM
            control_layout = QHBoxLayout()
            control_layout.addWidget(create_gm_button)
            control_layout.addWidget(authority_combobox)
            control_layout.setContentsMargins(5, 5, 5, 5)  # Añadir márgenes para dar espacio alrededor
            control_layout.setSpacing(10)  # Espaciado entre el botón y el desplegable

            # Crear un QWidget para contener el layout y añadirlo a la celda de la tabla
            control_widget = QWidget()
            control_widget.setLayout(control_layout)
            self.characters_table.setCellWidget(row_idx, 4, control_widget)

            # Conectar la lógica del botón al método create_gm
            create_gm_button.clicked.connect(lambda _, acc_name=account_name, char_name=character["name"], auth_level=authority_combobox: 
                                            self.create_gm_action(acc_name, char_name, auth_level.currentText()))
                         
    # Dentro de la función que carga los personajes de una cuenta:
    def add_character_controls(self, character, layout):
        create_gm_button = QPushButton("Crear GM")
        authority_combobox = QComboBox()
        authority_combobox.addItems(["IMPLEMENTOR", "GOD", "LOW_WIZARD", "PLAYER"])
        
        control_layout = QHBoxLayout()
        control_layout.addWidget(create_gm_button)
        control_layout.addWidget(authority_combobox)
        layout.addLayout(control_layout)
        
        # Conectar la lógica para crear o actualizar un GM al botón
        create_gm_button.clicked.connect(lambda: create_gm(character['name'], authority_combobox.currentText()))

     
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
            
    