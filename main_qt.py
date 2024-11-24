# main_qt.py
from PyQt5 import QtWidgets
import sys
from gui.main_window import ServerAdminApp  # Cambiar la importación a main_window.py, donde está ServerAdminApp

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = ServerAdminApp()
    main_window.show()
    sys.exit(app.exec_())
