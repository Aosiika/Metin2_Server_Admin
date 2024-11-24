# Archivo: main_window.py
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QProgressBar, QMessageBox, QInputDialog
from PyQt5.QtGui import QIcon
import qtawesome as qta
from gui.statistics_dashboard import StatisticsDashboard
from backend.server_config import load_server_config, save_server_config
from backend.update_manager import UpdateThread  # Importar el módulo de actualización
from gui.statistics_dashboard import StatisticsDashboard  # Asegúrate de importar StatisticsDashboard correctamente
import json
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Configura el ícono personalizado para la ventana
        icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'logo.ico')  # Utiliza logo.ico desde resources
        self.setWindowIcon(QIcon(icon_path))

        # Otros elementos de la UI...
        self.setWindowTitle('Administración del Servidor de Metin2')
        self.setGeometry(100, 100, 800, 600)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

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
        self.setWindowIcon(QIcon("resources/logo.ico"))  # Añadir el ícono a la ventana
        self.resize(1000, 600)

        self.is_dark_mode = self.config.get("theme", "light") == "dark"
        self.apply_theme()

        menubar = self.menuBar()
        config_menu = menubar.addMenu(self.trans["config_menu"])
        config_menu.addAction(self.trans["server_config_menu"], self.show_server_config)
        config_menu.addAction(self.trans["theme_menu"], self.choose_theme)
        config_menu.addSeparator()
        config_menu.addAction(self.trans["language_menu"], self.choose_language)

        about_menu = menubar.addMenu(self.trans["about_menu"])
        about_menu.addAction(self.trans["about_menu"], self.about_program)
        about_menu.addAction(self.trans.get("check_for_updates", "Comprobar Actualizaciones"), self.check_for_updates)

        main_layout = QHBoxLayout()
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        button_layout = QVBoxLayout()
        self.btn_manage_users = QPushButton(qta.icon('fa.users', color='black'), self.trans.get("btn_manage_users", "Gestión de Usuarios"))
        self.btn_manage_users.clicked.connect(self.show_manage_users)
        button_layout.addWidget(self.btn_manage_users)

        self.btn_create_account = QPushButton(qta.icon('fa.user-plus', color='black'), self.trans.get("btn_create_account", "Crear nueva cuenta de usuario"))
        self.btn_create_account.clicked.connect(self.show_create_account)
        button_layout.addWidget(self.btn_create_account)

        # Botón para mostrar estadísticas del servidor
        self.btn_show_statistics = QPushButton(qta.icon('fa.bar-chart', color='black'), self.trans.get("server_statistics", "Mostrar estadísticas del servidor"))
        self.btn_show_statistics.clicked.connect(self.show_statistics_dashboard)  # Conectar al método que muestra el panel de estadísticas
        button_layout.addWidget(self.btn_show_statistics)

        button_layout.addStretch()

        self.stack = QStackedWidget()
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.stack)

        self.update_thread = None
        self.progress_bar = None

    def check_for_updates(self):
        update_url = self.config.get("update_url")
        if not update_url:
            QMessageBox.information(self, "Actualización", "No se encontró una URL de actualización.")
            return

        reply = QMessageBox.question(self, "Nueva actualización", "Hay una nueva versión disponible. ¿Desea actualizar ahora?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.download_update(update_url)

    def download_update(self, update_url):
        output_path = os.path.join(os.getcwd(), "metin2_admin_update.exe")
        self.update_thread = UpdateThread(update_url, output_path)
        self.update_thread.update_progress.connect(self.show_update_progress)
        self.update_thread.update_complete.connect(self.on_update_complete)
        self.update_thread.start()

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(300, 300, 400, 30)
        self.progress_bar.setMaximum(100)
        self.progress_bar.show()

    def show_update_progress(self, progress):
        if self.progress_bar:
            self.progress_bar.setValue(progress)

    def on_update_complete(self, success):
        if self.progress_bar:
            self.progress_bar.hide()

        if success:
            QMessageBox.information(self, "Actualización", "La actualización se ha descargado y aplicado exitosamente. Reinicie la aplicación.")
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

    def show_manage_users(self):
        from gui.user_management import UserManagementWidget
        widget = UserManagementWidget()
        self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)

    def show_create_account(self):
        from gui.create_account import CreateAccountWidget
        widget = CreateAccountWidget()
        self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)

    def show_statistics_dashboard(self):
        # Método que muestra el panel de estadísticas
        from gui.statistics_dashboard import StatisticsDashboard
        statistics_widget = StatisticsDashboard()
        self.stack.addWidget(statistics_widget)
        self.stack.setCurrentWidget(statistics_widget)

    def show_server_config(self):
        from gui.server_config_gui import ServerConfigWidget
        widget = ServerConfigWidget(self.config)
        self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)

    def show_statistics_dashboard(self):
        # Crear y mostrar el panel de estadísticas con gráficos mejorados
        statistics_widget = StatisticsDashboard()
        self.stack.addWidget(statistics_widget)
        self.stack.setCurrentWidget(statistics_widget)

    def about_program(self):
        QMessageBox.information(self, self.trans["about_menu"], "Administración del Servidor de Metin2 - Versión 1.0")
        

    