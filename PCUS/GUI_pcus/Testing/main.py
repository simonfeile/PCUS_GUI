from pcus_GUI import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
import sys

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = Ui_MainWindow_functionality()
    w.show()
    sys.exit(app.exec_())
