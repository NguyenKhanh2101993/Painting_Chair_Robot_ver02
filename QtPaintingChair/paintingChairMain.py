# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QWidget
from comWindow import Ui_ComportWindow
from workWindow import Ui_MainWindow
from initSerial import Read_Write_to_Serial

#from PySide2.QtWidgets import QApplication, QWidget
#from PySide2.QtCore import QFile
#from PySide2.QtUiTools import QUiLoader

#class Widget(QWidget):
#    def __init__(self):
#        super(Widget, self).__init__()  # kế thừa init của QWidget
#        self.load_ui()
#
#    def load_ui(self):
#        loader = QUiLoader()
#        path = os.fspath(Path(__file__).resolve().parent / "GUIPaintingChair.ui")
#        ui_file = QFile(path)
#        ui_file.open(QFile.ReadOnly)
#        loader.load(ui_file, self)
#        ui_file.close()

class startWindow:
    def __init__(self):
        
        self.workSerial = Read_Write_to_Serial()
        self.startWindow = QWidget()
        self.uic = Ui_ComportWindow()
        self.uic.setupUi(self.startWindow)
        
        self.reset_comports()
        self.uic.pushButton.clicked.connect(self.choose_comports)
        self.uic.pushButton_2.clicked.connect(self.reset_comports)

        self.mainWindow = 0

        self.showStartWindow() 

    def showStartWindow(self):
        self.startWindow.show()

    def detroyStartWindow(self):
        self.startWindow.destroy()
    
    def reset_comports(self):
        comports = self.workSerial.detect_comports()
        print(comports)
        self.uic.comboBox.clear()
        self.uic.comboBox.addItems(comports)  

    def choose_comports(self):
        com = self.uic.comboBox.currentText()
        print(com)
        self.mainWindow = self.workSerial.choose_comports(115200,com)
        if self.mainWindow: 
            main_window.showWorkingWindow()
            self.detroyStartWindow()

class workingWindow:
    def __init__(self):
        self.workingWindow = QMainWindow()
        self.uiWorking = Ui_MainWindow()
        self.uiWorking.setupUi(self.workingWindow)

    def showWorkingWindow(self):
        self.workingWindow.show()
 

if __name__ == "__main__": # define điểm bắt đầu chạy chương trình
    app = QApplication([])
    widget = startWindow()
    main_window = workingWindow()
    sys.exit(app.exec_())
