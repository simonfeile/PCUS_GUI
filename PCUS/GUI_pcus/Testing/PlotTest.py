import sys
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, uic

uifilename = 'test.ui'
form_class = uic.loadUiType(uifilename)[0] #dirty reading of the ui file. better to convert it to a '.py'


from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys


class MyWindow(QMainWindow):

    def __init__(self):
        super(MyWindow, self).__init__()
        self.initUI()
        self.setGeometry(200, 200, 600, 600)
        self.setWindowTitle("Test")
        self.onInit()

    def initUI(self):
        self.label = QtWidgets.QLabel(self)
        self.label.setText("Label 1")
        self.label.move(50, 50)

        self.b1 = QtWidgets.QPushButton(self)
        self.b1.setText("Unclicked")
        self.b1.clicked.connect(self.clicked)

    def onInit(self):
        self.x_fit = np.linspace(1,10000, 10000)
        self.y_fit = [f(_x) for _x in self.x_fit]
        self.plotwidget.plot(self.x_fit,self.y_fit,symbol='o',pen=None)
        self.plotwidget.setLabel('left',text='toto',units='')
        self.plotwidget.setLabel('top',text='tata',units='')

    def clicked(self):
        self.label.setText("Pressed")
        self.update()

    def update(self):
        self.label.adjustSize()
def f(x):
    return x**2+1

if __name__ == '__main__':
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        app = QtGui.QApplication([])
        pg.setConfigOption('background', 'w')
        win = MyWindow()
        win.show()
        app.exec_()