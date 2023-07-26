# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'settingWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_motorSettings(object):
    def setupUi(self, motorSettings):
        motorSettings.setObjectName("motorSettings")
        motorSettings.resize(800, 290)
        motorSettings.setMinimumSize(QtCore.QSize(500, 200))
        motorSettings.setMaximumSize(QtCore.QSize(800, 290))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Robot.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        motorSettings.setWindowIcon(icon)
        motorSettings.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.gridLayout_2 = QtWidgets.QGridLayout(motorSettings)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.frame2 = QtWidgets.QFrame(motorSettings)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame2.sizePolicy().hasHeightForWidth())
        self.frame2.setSizePolicy(sizePolicy)
        self.frame2.setStyleSheet("background-color: rgb(179, 182, 183);\n"
"border: 2px solid rgb(255, 255, 255);\n"
"border-radius: 5px\n"
"")
        self.frame2.setFrameShape(QtWidgets.QFrame.Panel)
        self.frame2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame2.setLineWidth(2)
        self.frame2.setMidLineWidth(0)
        self.frame2.setObjectName("frame2")
        self.gridLayout = QtWidgets.QGridLayout(self.frame2)
        self.gridLayout.setObjectName("gridLayout")
        self.label_39 = QtWidgets.QLabel(self.frame2)
        self.label_39.setStyleSheet("background-color: rgb(130, 130, 130);\n"
"font: 75 14pt \"Arial\" bold;\n"
"color: rgb(255, 255, 255);\n"
"border: 1px solid rgb(255, 255, 255);\n"
"border-radius: 5px")
        self.label_39.setObjectName("label_39")
        self.gridLayout.addWidget(self.label_39, 0, 0, 1, 1)
        self.tableWidget = QtWidgets.QTableWidget(self.frame2)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.tableWidget.setFont(font)
        self.tableWidget.setStyleSheet("background-color: rgb(156, 156, 156);\n"
"border: 1px solid rgb(255, 255, 255);")
        self.tableWidget.setFrameShape(QtWidgets.QFrame.Box)
        self.tableWidget.setFrameShadow(QtWidgets.QFrame.Raised)
        self.tableWidget.setLineWidth(2)
        self.tableWidget.setRowCount(3)
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setObjectName("tableWidget")
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(5, item)
        self.gridLayout.addWidget(self.tableWidget, 1, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.frame2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        font.setKerning(True)
        self.buttonBox.setFont(font)
        self.buttonBox.setStyleSheet("background-color: rgb(200, 196, 190);\n"
"")
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close|QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)
        self.gridLayout_2.addWidget(self.frame2, 0, 0, 1, 1)

        self.retranslateUi(motorSettings)
        QtCore.QMetaObject.connectSlotsByName(motorSettings)

    def retranslateUi(self, motorSettings):
        _translate = QtCore.QCoreApplication.translate
        motorSettings.setWindowTitle(_translate("motorSettings", "Parameter Settings"))
        self.label_39.setText(_translate("motorSettings", "<html><head/><body><p align=\"center\"><span style=\" font-weight:600;\">MOTOR SETTINGS</span></p></body></html>"))
        item = self.tableWidget.verticalHeaderItem(0)
        item.setText(_translate("motorSettings", "GearBox"))
        item = self.tableWidget.verticalHeaderItem(1)
        item.setText(_translate("motorSettings", "MicroStep"))
        item = self.tableWidget.verticalHeaderItem(2)
        item.setText(_translate("motorSettings", "Diameter"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("motorSettings", "Motor X"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("motorSettings", "Motor Y"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("motorSettings", "Motor Z"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("motorSettings", "MotorA"))
        item = self.tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("motorSettings", "Motor B"))
        item = self.tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("motorSettings", "Motor C"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    motorSettings = QtWidgets.QWidget()
    ui = Ui_motorSettings()
    ui.setupUi(motorSettings)
    motorSettings.show()
    sys.exit(app.exec_())
