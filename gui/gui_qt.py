from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox, QInputDialog, QMainWindow, QApplication, QDialog, QTabWidget, QLabel, QPushButton, QFormLayout, QVBoxLayout, QLineEdit, QHBoxLayout, QStackedWidget, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar
from PyQt5.QtCore import QThread, pyqtSignal
import sys
import qtawesome as qta  # Importar qtawesome para usar íconos FontAwesome
from backend.database import get_all_accounts, update_account_status, create_account, get_all_characters, get_server_statistics
from backend.server_config import load_server_config, save_server_config
from backend.update_manager import UpdateThread
import json
import os

# Cargar traducciones desde archivo JSON
TRANSLATIONS_FILE = "translations.json"
def load_translations():
    with open(TRANSLATIONS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

class ServerAdminApp(QMainWindow):
    def __init__(self):
        super(ServerAdminApp, self).__init__()
        self.config = load_server_config()
        self.language = self.config.get("language", "es")
        self.translations = load_translations()
        self.trans = self.translations[self.language]
        
        self.setWindowTitle(self.trans["app_title"])
        self.resize(1000, 600)

        # Cargar configuración para el tema
        self.is_dark_mode = self.config.get("theme", "light") == "dark"
        self.apply_theme()

        # Menú superior
        menubar = self.menuBar()

        # Menú de configuración
        config_menu = menubar.addMenu(self.trans["config_menu"])
        config_menu.addAction(self.trans["server_config_menu"], self.create_server_config_widget)
        config_menu.addAction(self.trans["theme_menu"], self.choose_theme)
        config_menu.addSeparator()
        config_menu.addAction(self.trans["language_menu"], self.choose_language)

        # Menú acerca de
        about_menu = menubar.addMenu(self.trans["about_menu"])
        about_menu.addAction(self.trans["about_menu"], self.about_program)

        # Añadir la opción para comprobar actualizaciones
        check_update_action = about_menu.addAction(self.trans.get("check_for_updates", "Comprobar Actualizaciones"), self.check_for_updates)

        # Diseño principal
        main_layout = QHBoxLayout()
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Botones laterales
        button_layout = QVBoxLayout()
        self.btn_manage_users = QPushButton(qta.icon('fa.users', color='black'), self.trans.get("btn_manage_users", "Gestión de Usuarios"))
        self.btn_manage_users.clicked.connect(lambda: self.display_widget(self.accounts_widget))
        button_layout.addWidget(self.btn_manage_users)

        self.btn_create_account = QPushButton(qta.icon('fa.user-plus', color='black'), self.trans.get("btn_create_account", "Crear nueva cuenta de usuario"))
        self.btn_create_account.clicked.connect(lambda: self.display_widget(self.create_account_widget))
        button_layout.addWidget(self.btn_create_account)

        self.btn_show_statistics = QPushButton(qta.icon('fa.bar-chart', color='black'), self.trans.get("server_statistics", "Mostrar estadísticas del servidor"))
        self.btn_show_statistics.clicked.connect(lambda: self.display_widget(self.statistics_widget))
        button_layout.addWidget(self.btn_show_statistics)

        button_layout.addStretch()

        # Widgets apilados para mostrar contenido según el botón
        self.stack = QStackedWidget()
        self.accounts_widget = self.create_accounts_widget()
        self.create_account_widget = self.create_create_account_widget()
        self.statistics_widget = self.create_statistics_widget()
        self.server_config_widget = self.create_server_config_widget()

        self.stack.addWidget(self.accounts_widget)
        self.stack.addWidget(self.create_account_widget)
        self.stack.addWidget(self.statistics_widget)
        self.stack.addWidget(self.server_config_widget)

        # Agregar layouts al layout principal
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.stack)

        # Añadir una propiedad para el hilo de actualización
        self.update_thread = None
        self.progress_bar = None

    def check_for_updates(self):
        # Verificar si hay una actualización
        update_url = self.config.get("update_url")
        if not update_url:
            QMessageBox.information(self, "Actualización", "No se encontró una URL de actualización.")
            return

        reply = QMessageBox.question(self, "Nueva actualización", "Hay una nueva versión disponible. ¿Desea actualizar ahora?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.download_update(update_url)

    def download_update(self, update_url):
        # Iniciar el hilo de actualización
        output_path = os.path.join(os.getcwd(), "metin2_admin_update.exe")
        self.update_thread = UpdateThread(update_url, output_path)
        self.update_thread.update_progress.connect(self.show_update_progress)
        self.update_thread.update_complete.connect(self.on_update_complete)
        self.update_thread.start()

        # Crear una barra de progreso para mostrar el progreso de la descarga
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(300, 300, 400, 30)
        self.progress_bar.setMaximum(100)
        self.progress_bar.show()

    def show_update_progress(self, progress):
        # Actualizar la barra de progreso
        if self.progress_bar:
            self.progress_bar.setValue(progress)

    def on_update_complete(self, success):
        if self.progress_bar:
            self.progress_bar.hide()

        if success:
            QMessageBox.information(self, "Actualización", "La actualización se ha descargado y aplicado exitosamente. Reinicie la aplicación.")
            # Aquí podrías agregar la lógica para reemplazar el .exe actual y reiniciar el programa.
        else:
            QMessageBox.critical(self, "Error", "Ocurrió un error al intentar descargar la actualización.")

    def change_language(self, lang):
        self.config["language"] = lang
        save_server_config(self.config)
        QMessageBox.information(self, self.trans["about_menu"], f"El idioma ha cambiado a {lang}. Reinicie la aplicación para aplicar los cambios.")

    def apply_theme(self):
        if self.is_dark_mode:
            dark_stylesheet = """
                QMainWindow {
                    background-color: #2d2d2d;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #3c3f41;
                    color: #ffffff;
                    border-radius: 4px;
                    padding: 10px;
                }
                QTabWidget::pane {
                    border: 1px solid #444;
                }
                QTabBar::tab {
                    background: #3c3f41;
                    color: #ffffff;
                    padding: 10px;
                }
                QTabBar::tab:selected {
                    background: #5a5e62;
                }
                QMenuBar {
                    background-color: #2d2d2d;
                    color: #ffffff;
                }
                QMenuBar::item:selected {
                    background-color: #5a5e62;
                }
            """
            self.setStyleSheet(dark_stylesheet)
        else:
            self.setStyleSheet("")

    def choose_theme(self):
        theme, ok = QInputDialog.getItem(self, self.trans["theme_menu"], "Seleccione el tema:", [self.trans["light_theme"], self.trans["dark_theme"]], 0, False)
        if ok:
            self.is_dark_mode = (theme == self.trans["dark_theme"])
            self.config["theme"] = "dark" if self.is_dark_mode else "light"
            save_server_config(self.config)
            self.apply_theme()

    def choose_language(self):
        lang, ok = QInputDialog.getItem(self, self.trans["language_menu"], "Seleccione el idioma:", ["es", "en"], 0, False)
        if ok:
            self.change_language(lang)

    def create_accounts_widget(self):
        widget = QtWidgets.QWidget()
        layout = QVBoxLayout()
        group_box = QGroupBox(self.trans.get("gestion_usuarios_title", "Gestión de Usuarios"))
        group_box_layout = QVBoxLayout()

        # Tabla para mostrar cuentas de usuario
        self.accounts_table = QTableWidget()
        self.accounts_table.setColumnCount(5)
        self.accounts_table.setHorizontalHeaderLabels(["ID", "Login", "Status", "Última Conexión", "Creado en"])
        self.accounts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.accounts_table.set

        # Botones para acciones
        buttons_layout = QHBoxLayout()
        self.btn_edit_status = QPushButton(self.trans.get("btn_edit_status", "Editar Estado"))
        self.btn_edit_status.clicked.connect(self.edit_account_status)
        buttons_layout.addWidget(self.btn_edit_status)

        self.btn_view_characters = QPushButton(self.trans.get("btn_view_characters", "Ver Personajes Asociados"))
        self.btn_view_characters.clicked.connect(self.view_account_characters)
        buttons_layout.addWidget(self.btn_view_characters)

        group_box_layout.addLayout(buttons_layout)

        # Botón para mostrar cuentas de usuario
        self.btn_fetch_accounts = QPushButton(self.trans.get("btn_show_accounts", "Mostrar todas las cuentas de usuario"))
        self.btn_fetch_accounts.clicked.connect(self.show_accounts)
        group_box_layout.addWidget(self.btn_fetch_accounts)

        group_box.setLayout(group_box_layout)
        layout.addWidget(group_box)
        widget.setLayout(layout)
        return widget

    def create_create_account_widget(self):
        widget = QtWidgets.QWidget()
        layout = QVBoxLayout()
        group_box = QGroupBox(self.trans.get("create_account_title", "Crear Cuenta"))
        group_box_layout = QFormLayout()

        self.input_login = QLineEdit()
        self.input_login.setPlaceholderText(self.trans.get("login_label", "Login"))
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setPlaceholderText(self.trans.get("password_label", "Contraseña"))
        self.btn_create_account_confirm = QPushButton(self.trans.get("btn_create_account", "Crear Cuenta"))
        self.btn_create_account_confirm.clicked.connect(self.create_new_account)

        group_box_layout.addRow(self.trans.get("login_label", "Login"), self.input_login)
        group_box_layout.addRow(self.trans.get("password_label", "Contraseña"), self.input_password)
        group_box_layout.addRow(self.btn_create_account_confirm)

        group_box.setLayout(group_box_layout)
        layout.addWidget(group_box)
        widget.setLayout(layout)
        return widget

    def create_statistics_widget(self):
        widget = QtWidgets.QWidget()
        layout = QVBoxLayout()
        group_box = QGroupBox(self.trans.get("server_statistics", "Estadísticas del Servidor"))
        group_box_layout = QVBoxLayout()

        self.btn_fetch_statistics = QPushButton(self.trans.get("server_statistics", "Mostrar estadísticas del servidor"))
        self.btn_fetch_statistics.clicked.connect(self.show_server_statistics)
        group_box_layout.addWidget(self.btn_fetch_statistics)

        self.statistics_label = QLabel("")
        group_box_layout.addWidget(self.statistics_label)

        group_box.setLayout(group_box_layout)
        layout.addWidget(group_box)
        widget.setLayout(layout)
        return widget

    def create_server_config_widget(self):
        widget = QtWidgets.QWidget()
        layout = QVBoxLayout()
        group_box = QGroupBox(self.trans.get("server_config_menu", "Configuración del Servidor"))
        group_box_layout = QFormLayout()

        # Entradas de configuración del servidor
        self.input_db_host = QLineEdit(self.config.get("host", ""))
        self.input_db_user = QLineEdit(self.config.get("user", ""))
        self.input_db_password = QLineEdit(self.config.get("password", ""))
        self.input_db_password.setEchoMode(QLineEdit.Password)
        self.input_db_port = QLineEdit(str(self.config.get("port", "3306")))
        self.input_db_name = QLineEdit(self.config.get("database", ""))

        group_box_layout.addRow(self.trans.get("db_host_label", "Host del Servidor"), self.input_db_host)
        group_box_layout.addRow(self.trans.get("db_user_label", "Usuario de BD"), self.input_db_user)
        group_box_layout.addRow(self.trans.get("db_password_label", "Contraseña de BD"), self.input_db_password)
        group_box_layout.addRow(self.trans.get("db_port_label", "Puerto de BD"), self.input_db_port)
        group_box_layout.addRow(self.trans.get("db_name_label", "Nombre de la Base de Datos"), self.input_db_name)

        # Botón para guardar la configuración
        self.btn_save_config = QPushButton(self.trans.get("btn_save_config", "Guardar Configuración"))
        self.btn_save_config.clicked.connect(self.save_server_config)
        group_box_layout.addRow(self.btn_save_config)

        group_box.setLayout(group_box_layout)
        layout.addWidget(group_box)
        widget.setLayout(layout)
        return widget

    def display_widget(self, widget):
        self.stack
