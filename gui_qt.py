# gui_qt.py (nuevo archivo para PyQt)
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox, QInputDialog, QMainWindow, QApplication, QDialog, QTabWidget, QLabel, QPushButton, QFormLayout, QVBoxLayout, QLineEdit, QHBoxLayout, QStackedWidget, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView
import sys
import qtawesome as qta  # Importar qtawesome para usar íconos FontAwesome
from database import get_all_accounts, update_account_status, create_account, get_all_characters, get_server_statistics
from server_config import load_server_config, save_server_config
import json

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
        config_menu.addAction(self.trans["server_config_menu"], self.configure_server)
        config_menu.addAction(self.trans["theme_menu"], self.choose_theme)
        config_menu.addSeparator()
        config_menu.addAction(self.trans["language_menu"], self.choose_language)

        # Menú acerca de
        about_menu = menubar.addMenu(self.trans["about_menu"])
        about_action = about_menu.addAction(self.trans["about_menu"], self.about_program)

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
        self.accounts_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.accounts_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.accounts_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        group_box_layout.addWidget(self.accounts_table)

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
        self.stack.setCurrentWidget(widget)

    def show_accounts(self):
        accounts, error = get_all_accounts()
        if error:
            QMessageBox.critical(self, "Error", error)
        else:
            self.accounts_table.setRowCount(len(accounts))
            for row_idx, acc in enumerate(accounts):
                self.accounts_table.setItem(row_idx, 0, QTableWidgetItem(str(acc['id'])))
                self.accounts_table.setItem(row_idx, 1, QTableWidgetItem(acc['login']))
                self.accounts_table.setItem(row_idx, 2, QTableWidgetItem(acc['status']))
                self.accounts_table.setItem(row_idx, 3, QTableWidgetItem(str(acc['last_play'])))
                self.accounts_table.setItem(row_idx, 4, QTableWidgetItem(str(acc['create_time'])))

    def edit_account_status(self):
        selected_row = self.accounts_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Advertencia", "Debe seleccionar una cuenta para editar su estado.")
            return

        account_id = self.accounts_table.item(selected_row, 0).text()
        current_status = self.accounts_table.item(selected_row, 2).text()
        new_status, ok = QInputDialog.getItem(self, "Editar Estado", "Seleccione el nuevo estado:", ["OK", "BLOCK"], 0, False)

        if ok and new_status != current_status:
            success = update_account_status(account_id, new_status)
            if success:
                QMessageBox.information(self, "Éxito", "Estado de la cuenta actualizado correctamente.")
                self.show_accounts()
            else:
                QMessageBox.critical(self, "Error", "Error al actualizar el estado de la cuenta.")

    def view_account_characters(self):
        selected_row = self.accounts_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Advertencia", "Debe seleccionar una cuenta para ver sus personajes asociados.")
            return

        try:
            account_id = self.accounts_table.item(selected_row, 0).text()
            characters, error = get_all_characters(account_id)
            if error:
                QMessageBox.critical(self, "Error", error)
            else:
                if characters:
                    characters_str = "\n".join([f"ID: {char.get('id', 'N/A')}, Nombre: {char.get('name', 'N/A')}, Nivel: {char.get('level', 'N/A')}" for char in characters])
                    QMessageBox.information(self, "Personajes Asociados", characters_str)
                else:
                    QMessageBox.information(self, "Personajes Asociados", "No se encontraron personajes asociados a esta cuenta.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error inesperado: {str(e)}")

    def create_new_account(self):
        login = self.input_login.text()
        password = self.input_password.text()
        if login and password:
            success = create_account(login, password)
            if success:
                QMessageBox.information(self, self.trans.get("create_account_title", "Crear Cuenta"), self.trans.get("create_account_success", "Cuenta creada exitosamente."))
            else:
                QMessageBox.critical(self, self.trans.get("create_account_title", "Crear Cuenta"), self.trans.get("create_account_error", "Error al crear la cuenta."))
        else:
            QMessageBox.warning(self, self.trans.get("create_account_title", "Crear Cuenta"), "Debe ingresar un login y una contraseña.")

    def show_server_statistics(self):
        stats, error = get_server_statistics()
        if error:
            QMessageBox.critical(self, "Error", self.trans.get("server_statistics_error", "Error al obtener las estadísticas del servidor: {error}").format(error=error))
        else:
            stats_str = self.trans.get("server_statistics_success", "Usuarios en línea: {online_users}, Total de personajes: {total_characters}").format(online_users=stats["online_users"], total_characters=stats["total_characters"])
            self.statistics_label.setText(stats_str)

    def save_server_config(self):
        # Guardar la configuración del servidor
        self.config["host"] = self.input_db_host.text()
        self.config["user"] = self.input_db_user.text()
        self.config["password"] = self.input_db_password.text()
        self.config["port"] = int(self.input_db_port.text())
        self.config["database"] = self.input_db_name.text()
        save_server_config(self.config)
        QMessageBox.information(self, self.trans.get("server_config_menu", "Configuración del Servidor"), "Configuración guardada exitosamente.")

    def about_program(self):
        QMessageBox.information(self, self.trans["about_menu"], "Administración del Servidor de Metin2 - Versión 1.0")

    def configure_server(self):
        self.display_widget(self.server_config_widget)
