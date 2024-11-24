# Archivo: server_config_gui.py
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QVBoxLayout, QGroupBox, QFormLayout, QLineEdit, QPushButton, QMessageBox
from backend.server_config import save_server_config

class ServerConfigWidget(QtWidgets.QWidget):
    def __init__(self, config):
        super(ServerConfigWidget, self).__init__()
        self.config = config

        layout = QVBoxLayout()
        group_box = QGroupBox("Configuración del Servidor")
        group_box_layout = QFormLayout()

        self.input_db_host = QLineEdit(self.config.get("host", ""))
        self.input_db_user = QLineEdit(self.config.get("user", ""))
        self.input_db_password = QLineEdit(self.config.get("password", ""))
        self.input_db_password.setEchoMode(QLineEdit.Password)
        self.input_db_port = QLineEdit(str(self.config.get("port", "3306")))
        self.input_db_name = QLineEdit(self.config.get("database", ""))

        group_box_layout.addRow("Host del Servidor", self.input_db_host)
        group_box_layout.addRow("Usuario de BD", self.input_db_user)
        group_box_layout.addRow("Contraseña de BD", self.input_db_password)
        group_box_layout.addRow("Puerto de BD", self.input_db_port)
        group_box_layout.addRow("Nombre de la Base de Datos", self.input_db_name)

        self.btn_save_config = QPushButton("Guardar Configuración")
        self.btn_save_config.clicked.connect(self.save_server_config)
        group_box_layout.addRow(self.btn_save_config)

        group_box.setLayout(group_box_layout)
        layout.addWidget(group_box)
        self.setLayout(layout)

    def save_server_config(self):
        self.config["host"] = self.input_db_host.text()
        self.config["user"] = self.input_db_user.text()
        self.config["password"] = self.input_db_password.text()
        self.config["port"] = int(self.input_db_port.text())
        self.config["database"] = self.input_db_name.text()
        save_server_config(self.config)
        QMessageBox.information(self, "Configuración del Servidor", "Configuración guardada exitosamente.")
