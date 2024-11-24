from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFormLayout, QHBoxLayout, QSpacerItem, QSizePolicy
from backend.database import create_account

class CreateAccountWidget(QWidget):
    def __init__(self):
        super(CreateAccountWidget, self).__init__()
        self.translations = self.load_translations()  # Cargar las traducciones
        self.init_ui()

    def load_translations(self):
        import json
        with open('translations.json', 'r', encoding='utf-8') as file:
            translations = json.load(file)
        return translations.get("es", {})  # Utiliza 'es' como el idioma predeterminado

    def init_ui(self):
        # Cambiar el layout a un QFormLayout para mejor alineación
        form_layout = QFormLayout()

        # Etiqueta y campo para el nombre de usuario
        self.login_label = QLabel(self.translations["login_label"])
        self.login_input = QLineEdit()
        form_layout.addRow(self.login_label, self.login_input)

        # Etiqueta y campo para la contraseña
        self.password_label = QLabel(self.translations["password_label"])
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow(self.password_label, self.password_input)

        # Añadir espacio flexible para centrar el botón
        button_layout = QHBoxLayout()
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        button_layout.addSpacerItem(spacer)

        # Botón para crear la cuenta
        self.create_account_button = QPushButton(self.translations["btn_create_account"])
        self.create_account_button.clicked.connect(self.create_account_action)
        button_layout.addWidget(self.create_account_button)

        # Añadir espacio flexible al otro lado del botón
        button_layout.addSpacerItem(spacer)

        # Layout principal que contiene el formulario y el botón
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)

        # Establecer el layout al widget
        self.setLayout(main_layout)

    def create_account_action(self):
        login = self.login_input.text()
        password = self.password_input.text()

        if not login or not password:
            QMessageBox.warning(self, "Advertencia", self.translations["create_account_error"])
            return

        success, error = create_account(login, password)

        if success:
            QMessageBox.information(self, "Éxito", self.translations["create_account_success"])
        else:
            QMessageBox.critical(self, "Error", self.translations["create_account_error"] + f": {error}")
