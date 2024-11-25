# Archivo: server_config_gui.py
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout, QLineEdit, QPushButton, QMessageBox
from backend.server_config import load_server_config, save_server_config


class ServerConfigWidget(QWidget):
    def __init__(self, config=None):
        super().__init__()
        self.config = config
        self.init_ui()
        if self.config is None:
            self.load_config()
        else:
            self.apply_config(self.config)

    def init_ui(self):
        self.setWindowTitle("Configuración del Servidor")
        self.layout = QFormLayout()

        # Campos para la configuración del servidor
        self.host_input = QLineEdit()
        self.port_input = QLineEdit()
        self.user_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.db_account_name_input = QLineEdit()
        self.db_common_name_input = QLineEdit()
        self.db_player_name_input = QLineEdit()

        # Botón para guardar la configuración
        self.save_button = QPushButton("Guardar Configuración")
        self.save_button.clicked.connect(self.save_config)

        # Añadir campos al layout en el orden deseado
        self.layout.addRow("Host del Servidor", self.host_input)
        self.layout.addRow("Puerto de BD", self.port_input)
        self.layout.addRow("Usuario de BD", self.user_input)
        self.layout.addRow("Contraseña de BD", self.password_input)
        self.layout.addRow("Nombre de Base de Datos de Cuentas", self.db_account_name_input)
        self.layout.addRow("Nombre de Base de Datos GM", self.db_common_name_input)
        self.layout.addRow("Nombre de Base de Datos de Player", self.db_player_name_input)
        self.layout.addRow(self.save_button)

        self.setLayout(self.layout)
        self.load_config()

    def load_config(self):
        config = load_server_config()
        if config:
            self.host_input.setText(config.get("host", ""))
            self.port_input.setText(str(config.get("port", "")))
            self.user_input.setText(config.get("user", ""))
            self.password_input.setText(config.get("password", ""))
            self.db_account_name_input.setText(config.get("db_account_name", ""))
            self.db_common_name_input.setText(config.get("db_common_name", ""))
            self.db_player_name_input.setText(config.get("db_player_name", ""))

    def save_config(self):
        config = {
            "host": self.host_input.text(),
            "port": int(self.port_input.text()),
            "user": self.user_input.text(),
            "password": self.password_input.text(),
            "db_account_name": self.db_account_name_input.text(),
            "db_common_name": self.db_common_name_input.text(),
            "db_player_name": self.db_player_name_input.text(),
            "theme": "light",  # Este valor se puede ajustar según la aplicación
            "language": "es"   # Este valor se puede ajustar según la aplicación
        }
        save_server_config(config)
        QMessageBox.information(self, "Éxito", "Configuración guardada correctamente.")
    
    def apply_config(self, config):
        if config:
            self.host_input.setText(config.get("host", ""))
            self.port_input.setText(str(config.get("port", "")))
            self.user_input.setText(config.get("user", ""))
            self.password_input.setText(config.get("password", ""))
            self.db_account_name_input.setText(config.get("db_account_name", ""))
            self.db_common_name_input.setText(config.get("db_common_name", ""))
            self.db_player_name_input.setText(config.get("db_player_name", ""))