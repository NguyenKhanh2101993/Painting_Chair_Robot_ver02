from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    #def setupUi(self, MainWindow):
    def setupUi(self, communication):
        communication.setObjectName("communication")
        communication.resize(400, 300)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(communication.sizePolicy().hasHeightForWidth())
        communication.setSizePolicy(sizePolicy)
        communication.setMinimumSize(QtCore.QSize(400, 300))
        communication.setMaximumSize(QtCore.QSize(400, 300))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Robot.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        communication.setWindowIcon(icon)
        self.frame2 = QtWidgets.QFrame(communication)
        self.frame2.setGeometry(QtCore.QRect(0, 0, 401, 301))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame2.sizePolicy().hasHeightForWidth())
        self.frame2.setSizePolicy(sizePolicy)
        self.frame2.setStyleSheet("background-color: rgb(170, 170, 127);")
        self.frame2.setFrameShape(QtWidgets.QFrame.Panel)
        self.frame2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame2.setLineWidth(2)
        self.frame2.setMidLineWidth(0)
        self.frame2.setObjectName("frame2")
        self.comboBox_comPort = QtWidgets.QComboBox(self.frame2)
        self.comboBox_comPort.setGeometry(QtCore.QRect(20, 160, 141, 41))
        self.comboBox_comPort.setStyleSheet("font: 75 16pt \"Arial\";\n"
    "background-color: rgb(159, 159, 159);\n"
    "border: 1px solid rgb(255, 255, 255);\n"
    "border-radius: 5px")
        self.comboBox_comPort.setObjectName("comboBox_comPort")
        self.pushButton = QtWidgets.QPushButton(self.frame2)
        self.pushButton.setGeometry(QtCore.QRect(180, 240, 93, 36))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton.setFont(font)
        self.pushButton.setMouseTracking(False)
        self.pushButton.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.pushButton.setAutoFillBackground(False)
        self.pushButton.setStyleSheet("background-color: rgb(0, 170, 127);\n"
    "border: 1px solid rgb(255, 255, 255);\n"
    "border-radius: 5px")
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.frame2)
        self.pushButton_2.setGeometry(QtCore.QRect(290, 240, 93, 36))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setMouseTracking(False)
        self.pushButton_2.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.pushButton_2.setAutoFillBackground(False)
        self.pushButton_2.setStyleSheet("background-color: rgb(255, 0, 0);\n"
    "border: 1px solid rgb(255, 255, 255);\n"
    "border-radius: 5px")
        self.pushButton_2.setObjectName("pushButton_2")
        self.label_39 = QtWidgets.QLabel(self.frame2)
        self.label_39.setGeometry(QtCore.QRect(20, 10, 351, 51))
        self.label_39.setStyleSheet("background-color: rgb(130, 130, 130);\n"
    "font: 75 14pt \"Arial\" bold;\n"
    "color: rgb(255, 255, 255);\n"
    "border: 1px solid rgb(255, 255, 255);\n"
    "border-radius: 5px")
        self.label_39.setObjectName("label_39")
        self.comboBox_baudRate = QtWidgets.QComboBox(self.frame2)
        self.comboBox_baudRate.setGeometry(QtCore.QRect(230, 160, 141, 41))
        self.comboBox_baudRate.setStyleSheet("font: 75 16pt \"Arial\";\n"
    "background-color: rgb(159, 159, 159);\n"
    "border: 1px solid rgb(255, 255, 255);\n"
    "border-radius: 5px")
        self.comboBox_baudRate.setObjectName("comboBox_baudRate")
        self.label_40 = QtWidgets.QLabel(self.frame2)
        self.label_40.setGeometry(QtCore.QRect(230, 100, 141, 51))
        self.label_40.setStyleSheet("background-color: rgb(130, 130, 130);\n"
    "font: 75 14pt \"Arial\" bold;\n"
    "color: rgb(255, 255, 255);\n"
    "border: 1px solid rgb(255, 255, 255);\n"
    "border-radius: 5px")
        self.label_40.setObjectName("label_40")
        self.label_41 = QtWidgets.QLabel(self.frame2)
        self.label_41.setGeometry(QtCore.QRect(20, 100, 141, 51))
        self.label_41.setStyleSheet("background-color: rgb(130, 130, 130);\n"
    "font: 75 14pt \"Arial\" bold;\n"
    "color: rgb(255, 255, 255);\n"
    "border: 1px solid rgb(255, 255, 255);\n"
    "border-radius: 5px")
        self.label_41.setObjectName("label_41")
        self.pushButton_2.raise_()
        self.comboBox_comPort.raise_()
        self.pushButton.raise_()
        self.label_39.raise_()
        self.comboBox_baudRate.raise_()
        self.label_40.raise_()
        self.label_41.raise_()

        self.retranslateUi(communication)
        QtCore.QMetaObject.connectSlotsByName(communication)

    def retranslateUi(self, communication):
        _translate = QtCore.QCoreApplication.translate
        communication.setWindowTitle(_translate("communication", "Communication"))
        self.pushButton.setText(_translate("communication", "OK"))
        self.pushButton_2.setText(_translate("communication", "RESET"))
        self.label_39.setText(_translate("communication", "<html><head/><body><p align=\"center\"><span style=\" font-weight:600;\">COMMUNICATION</span></p></body></html>"))
        self.label_40.setText(_translate("communication", "<html><head/><body><p align=\"center\"><span style=\" font-weight:600;\">BAUDRATE</span></p></body></html>"))
        self.label_41.setText(_translate("communication", "<html><head/><body><p align=\"center\"><span style=\" font-weight:600;\">COM PORT</span></p></body></html>"))



class MyWindow(QtWidgets.QMainWindow):

    def closeEvent(self,event):
        result = QtWidgets.QMessageBox.question(self,
                      "Confirm Exit...",
                      "Are you sure you want to exit ?",
                      QtWidgets.QMessageBox.Yes| QtWidgets.QMessageBox.No)
        event.ignore()

        if result == QtWidgets.QMessageBox.Yes:
            event.accept()

    def helooo(self):
        print("hellooo")

class workingWindow:
    def __init__(self):
        self.MainWindow = MyWindow()
        ui = Ui_MainWindow()
        ui.setupUi(self.MainWindow)
    def showWin(self): 
        self.MainWindow.show()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    demo = workingWindow()
    demo.showWin()
    sys.exit(app.exec_())