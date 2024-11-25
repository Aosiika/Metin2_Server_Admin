# statistics_dashboard.py
import pymysql
import json
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout, QLineEdit, QPushButton, QMessageBox, QLabel, QMainWindow


CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'server_config.json')

def load_db_config():
    """Carga la configuración de la base de datos desde el archivo 'server_config.json'."""
    try:
        with open(CONFIG_FILE_PATH, 'r') as config_file:
            db_config = json.load(config_file)
        return db_config
    except Exception as e:
        print(f"Error al cargar la configuración de la base de datos: {e}")
        return None

def connect_to_database(db_name):
    """Conecta a la base de datos usando la configuración cargada desde 'server_config.json'."""
    db_config = load_db_config()

    if not db_config:
        return None, "No se pudo cargar la configuración de la base de datos"

    try:
        connection = pymysql.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            port=db_config['port'],
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection, None
    except Exception as e:
        return None, str(e)
    
def get_server_statistics():
    try:
        connection_account, error_account = connect_to_database(load_db_config()["db_account_name"])
        connection_player, error_player = connect_to_database(load_db_config()["db_player_name"])

        if error_account:
            return None, error_account
        if error_player:
            return None, error_player

        with connection_account.cursor() as cursor:
            # Cuentas creadas
            cursor.execute("SELECT COUNT(*) AS total_accounts FROM account")
            total_accounts = cursor.fetchone()["total_accounts"]

            # Cuentas creadas en los últimos 10 minutos
            ten_minutes_ago = datetime.now() - timedelta(minutes=10)
            cursor.execute("SELECT COUNT(*) AS accounts_created_last_10_min FROM account WHERE create_time >= %s", (ten_minutes_ago,))
            accounts_created_last_10_min = cursor.fetchone()["accounts_created_last_10_min"]

        with connection_player.cursor() as cursor:
            # Total de personajes creados
            cursor.execute("SELECT COUNT(*) AS total_characters FROM player")
            total_characters = cursor.fetchone()["total_characters"]

            # Personajes activos en los últimos 10 minutos
            cursor.execute("SELECT COUNT(DISTINCT account_id) AS active_users_last_10_min FROM player WHERE last_play >= %s", (ten_minutes_ago,))
            active_users_last_10_min = cursor.fetchone()["active_users_last_10_min"]

        return {
            "total_accounts": total_accounts,
            "total_characters": total_characters,
            "accounts_created_last_10_min": accounts_created_last_10_min,
            "active_users_last_10_min": active_users_last_10_min
        }, None

    except Exception as e:
        return None, str(e)
    finally:
        if connection_account:
            connection_account.close()
        if connection_player:
            connection_player.close()

class StatisticsDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.statistics_label = QLabel("Cargando estadísticas del servidor...")
        layout.addWidget(self.statistics_label)

        # Contenedor de diseño para organizar las gráficas horizontalmente
        charts_layout = QHBoxLayout()

        # Espacio para las tres gráficas
        self.canvas_accounts = FigureCanvas(plt.figure())
        self.canvas_characters = FigureCanvas(plt.figure())
        self.canvas_active_players = FigureCanvas(plt.figure())

        # Añadir los gráficos al contenedor horizontal
        charts_layout.addWidget(self.canvas_accounts)
        charts_layout.addWidget(self.canvas_characters)
        charts_layout.addWidget(self.canvas_active_players)

        # Añadir el layout de gráficos al layout principal
        layout.addLayout(charts_layout)

        self.setLayout(layout)
        self.update_statistics()

    def update_statistics(self):
        stats, error = get_server_statistics()
        if error:
            self.statistics_label.setText(f"Error al obtener las estadísticas: {error}")
            return

        self.statistics_label.setText(
            f"Total cuentas creadas: {stats['total_accounts']}\n"
            f"Total personajes creados: {stats['total_characters']}\n"
            f"Usuarios activos (últimos 10 minutos): {stats['active_users_last_10_min']}"
        )

        # Graficar las estadísticas
        self.plot_statistics(stats)

    def plot_statistics(self, stats):
        # Limpiar gráficos anteriores
        self.canvas_accounts.figure.clear()
        self.canvas_characters.figure.clear()
        self.canvas_active_players.figure.clear()

        # Definir un color para las barras
        bar_color = "#333333"

        # Gráfica de cuentas creadas
        ax1 = self.canvas_accounts.figure.add_subplot(111)
        ax1.bar(['Total de cuentas creadas'], [stats['total_accounts']], color=bar_color)
        ax1.set_title('Total de cuentas creadas', fontsize=10, fontweight='bold', pad=10)
        ax1.set_ylabel('Cantidad', fontsize=8)
        ax1.set_xticks([])  # Ocultar las marcas en el eje x
        ax1.title.set_position([.5, 1.05])

        # Gráfica de personajes creados
        ax2 = self.canvas_characters.figure.add_subplot(111)
        ax2.bar(['Total de personajes creados'], [stats['total_characters']], color=bar_color)
        ax2.set_title('Total de personajes creados', fontsize=10, fontweight='bold', pad=10)
        ax2.set_ylabel('Cantidad', fontsize=8)
        ax2.set_xticks([])  # Ocultar las marcas en el eje x
        ax2.title.set_position([.5, 1.05])

        # Gráfica de personajes activos en los últimos 10 minutos
        ax3 = self.canvas_active_players.figure.add_subplot(111)
        ax3.bar(['Personajes activos últimos 10 min'], [stats['active_users_last_10_min']], color=bar_color)
        ax3.set_title('PJ activos  últimos 10 min', fontsize=10, fontweight='bold', pad=10)
        ax3.set_ylabel('Cantidad', fontsize=8)
        ax3.set_xticks([])  # Ocultar las marcas en el eje x
        ax3.title.set_position([.5, 1.05])

        # Añadir etiquetas a las barras para mostrar valores exactos
        ax1.bar_label(ax1.containers[0], label_type='edge', fontsize=8, fontweight='bold', color='white')
        ax2.bar_label(ax2.containers[0], label_type='edge', fontsize=8, fontweight='bold', color='white')
        ax3.bar_label(ax3.containers[0], label_type='edge', fontsize=8, fontweight='bold', color='white')

        # Actualizar los gráficos
        self.canvas_accounts.draw()
        self.canvas_characters.draw()
        self.canvas_active_players.draw()
        
    class ServerConfigWidget(QWidget):
        def __init__(self):
            super().__init__()
            self.init_ui()

        def init_ui(self):
            self.setWindowTitle("Configuración del Servidor")
            self.layout = QFormLayout()

            # Campos para la configuración del servidor
            self.host_input = QLineEdit()
            self.port_input = QLineEdit()
            self.user_input = QLineEdit()
            self.password_input = QLineEdit()
            self.db_account_name_input = QLineEdit()
            self.db_common_name_input = QLineEdit()
            self.db_player_name_input = QLineEdit()

            # Botón para guardar la configuración
            self.save_button = QPushButton("Guardar Configuración")
            self.save_button.clicked.connect(self.save_config)

            # Añadir campos al layout
            self.layout.addRow("Host del Servidor", self.host_input)
            self.layout.addRow("Puerto de BD", self.port_input)
            self.layout.addRow("Usuario de BD", self.user_input)
            self.layout.addRow("Contraseña de BD", self.password_input)
            self.layout.addRow("Nombre de Base de Datos de Cuentas", self.db_account_name_input)
            self.layout.addRow("Nombre de Base de Datos Común", self.db_common_name_input)
            self.layout.addRow("Nombre de Base de Datos de Jugadores", self.db_player_name_input)
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

    class MainApp(QMainWindow):
        def __init__(self):
            super().__init__()
            self.init_ui()

        def init_ui(self):
            self.setWindowTitle("Administración del Servidor de Metin2")
            self.setGeometry(100, 100, 800, 600)

            # Crear menú de configuración
            menubar = self.menuBar()
            config_menu = menubar.addMenu("Configuración")

            # Acción de configuración del servidor
            server_config_action = QAction("Configuración del Servidor", self)
            server_config_action.triggered.connect(self.open_server_config)
            config_menu.addAction(server_config_action)

            # Otras acciones del menú...

        def open_server_config(self):
            self.server_config_widget = ServerConfigWidget()
            self.server_config_widget.show()