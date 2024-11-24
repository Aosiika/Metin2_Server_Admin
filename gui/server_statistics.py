# Archivo: server_statistics.py
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QVBoxLayout, QGroupBox, QLabel, QPushButton, QMessageBox
from backend.database import get_server_statistics

class ServerStatisticsWidget(QtWidgets.QWidget):
    def __init__(self):
        super(ServerStatisticsWidget, self).__init__()
        layout = QVBoxLayout()
        group_box = QGroupBox("Estadísticas del Servidor")
        group_box_layout = QVBoxLayout()

        self.btn_fetch_statistics = QPushButton("Mostrar estadísticas del servidor")
        self.btn_fetch_statistics.clicked.connect(self.show_server_statistics)
        group_box_layout.addWidget(self.btn_fetch_statistics)

        self.statistics_label = QLabel("")
        group_box_layout.addWidget(self.statistics_label)

        group_box.setLayout(group_box_layout)
        layout.addWidget(group_box)
        self.setLayout(layout)

    def show_server_statistics(self):
        stats, error = get_server_statistics()
        if error:
            QMessageBox.critical(self, "Error", f"Error al obtener las estadísticas del servidor: {error}")
        else:
            stats_str = f"Usuarios en línea: {stats['online_users']}, Total de personajes: {stats['total_characters']}"
            self.statistics_label.setText(stats_str)
