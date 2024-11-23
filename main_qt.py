# main_qt.py
from PyQt5 import QtWidgets
import sys
from gui.gui_qt import ServerAdminApp

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = ServerAdminApp()
    main_window.show()
    sys.exit(app.exec_())