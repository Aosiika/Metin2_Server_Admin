import pymysql
import json
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox

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
        connection_account, error_account = connect_to_database("srv1_account")
        connection_player, error_player = connect_to_database("srv1_player")

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
