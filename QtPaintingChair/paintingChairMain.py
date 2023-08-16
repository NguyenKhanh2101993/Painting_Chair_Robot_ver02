# This Python file uses the following encoding: utf-8
import os
import sys
import time
import math
#import psutil

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget, QDesktopWidget
from PyQt5.QtCore import QDate, QTime ,QObject, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor

from comWindow import Ui_communication
if os.name == "nt":
    from workWindow import Ui_MainWindow
if os.name == "posix":
    from workLinux import Ui_MainWindow

from teachWindow import Ui_teachMode
from settingWindow import Ui_motorSettings
from defineXYWindow import Ui_definePinsXY

from initSerial import Read_Write_to_Serial 
from workFile import workingFile 
from settingMotor import makeJsonSetting
#================================================================================================
# ====> test ok
class checkComWindow():
    def __init__(self):
        
        self.comWindow = QWidget()
        self.uic = Ui_communication()
        self.uic.setupUi(self.comWindow)
        self.workSerial = Read_Write_to_Serial()
        
        self.reset_comports()
        self.uic.pushButton.clicked.connect(self.choose_comports)
        self.uic.pushButton_2.clicked.connect(self.reset_comports)
        self.connectSignal = False

    def center(self):
        qtRectangle = self.comWindow.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.comWindow.move(qtRectangle.topLeft()) 

    def showComWindow(self):
        self.center()
        self.comWindow.show()

    def detroyComWindow(self):
        self.comWindow.close()
    
    def reset_comports(self):
        comports = self.workSerial.detect_comports()
        main_window.showStatus(comports)
        self.uic.comboBox_comPort.clear()
        self.uic.comboBox_baudRate.clear()
        self.uic.comboBox_comPort.addItems(comports)  
        self.uic.comboBox_baudRate.addItems(["9600", "115200"])

    def choose_comports(self):
        com = self.uic.comboBox_comPort.currentText()
        baud = self.uic.comboBox_baudRate.currentText()
        result = self.workSerial.choose_comports(baud,com)
        if result: 
              main_window.showStatus("Kết nối với cổng COM: " + com + "-Baudrate: "+ baud)
              main_window.sendMotorSensorBitPostoArduino()
              main_window.sendOutputBitPostoArduino()
              main_window.startMonitorDataFromArduinoThread()
              main_window.startTeachModeThread()
              main_window.startAutoRunThread()
              self.connectSignal = True
              self.detroyComWindow()
        else: 
              main_window.showStatus("Không nhận được cổng COM (Mất kết nối hoặc bị chặn)")
              pass
#================================================================================================
class setPinsWindow:
    def __init__(self):
        self.pinsWindow = QWidget()
        self.uiPinsWindow = Ui_definePinsXY()
        self.uiPinsWindow.setupUi(self.pinsWindow)
        self.uiPinsWindow.pushButton_Save.clicked.connect(self.saveXYpinsToJson)
        self.uiPinsWindow.pushButton_Edit.clicked.connect(self.editModePins)

        self.pinX = []; self.pinY = [] # luu thu tu cac chan dieu khien input output
        self.xSensor = []; self.yOutput = []
        self.xSensorDefined = []
        self.yCoilDefine = []

        self.pinXspinBox = [self.uiPinsWindow.spinBox_X1, self.uiPinsWindow.spinBox_X2, self.uiPinsWindow.spinBox_X3, self.uiPinsWindow.spinBox_X4,
                             self.uiPinsWindow.spinBox_X5, self.uiPinsWindow.spinBox_X6, self.uiPinsWindow.spinBox_X7, self.uiPinsWindow.spinBox_X8,
                             self.uiPinsWindow.spinBox_X9, self.uiPinsWindow.spinBox_X10, self.uiPinsWindow.spinBox_X11, self.uiPinsWindow.spinBox_X12,
                             self.uiPinsWindow.spinBox_X13, self.uiPinsWindow.spinBox_X14, self.uiPinsWindow.spinBox_X15, self.uiPinsWindow.spinBox_X16]
        
        self.pinYspinBox = [self.uiPinsWindow.spinBox_Y1, self.uiPinsWindow.spinBox_Y2, self.uiPinsWindow.spinBox_Y3, self.uiPinsWindow.spinBox_Y4,
                             self.uiPinsWindow.spinBox_Y5, self.uiPinsWindow.spinBox_Y6, self.uiPinsWindow.spinBox_Y7, self.uiPinsWindow.spinBox_Y8,
                             self.uiPinsWindow.spinBox_Y9, self.uiPinsWindow.spinBox_Y10, self.uiPinsWindow.spinBox_Y11, self.uiPinsWindow.spinBox_Y12,
                             self.uiPinsWindow.spinBox_Y13, self.uiPinsWindow.spinBox_Y14, self.uiPinsWindow.spinBox_Y15, self.uiPinsWindow.spinBox_Y16]
        
        self.xSensorSpinBox = [self.uiPinsWindow.spinBox_xhome, self.uiPinsWindow.spinBox_yhome,self.uiPinsWindow.spinBox_zhome,self.uiPinsWindow.spinBox_ahome,
                               self.uiPinsWindow.spinBox_xlimit,self.uiPinsWindow.spinBox_ylimit,self.uiPinsWindow.spinBox_zlimit,self.uiPinsWindow.spinBox_alimit]
        
        self.yOutputSpinBox = [self.uiPinsWindow.spinBox_spray1, self.uiPinsWindow.spinBox_spray2,self.uiPinsWindow.spinBox_spray3, self.uiPinsWindow.spinBox_spray4,
                               self.uiPinsWindow.spinBox_rotateTable1, self.uiPinsWindow.spinBox_rotateTable2,
                               self.uiPinsWindow.spinBox_rotateTable3, self.uiPinsWindow.spinBox_rotateTable4]

    def closePinsWindow(self):
        self.pinsWindow.close()

    def center(self):
        qtRectangle = self.pinsWindow.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.pinsWindow.move(qtRectangle.topLeft()) 

    def showPinsWindow(self):
        self.getXpinsFromJson()
        self.getYpinsFromJson()
        self.getSensorPinFromJson()
        self.getOutputPinFromJson()
        
        for i in range(len(self.pinXspinBox)):
            self.pinXspinBox[i].setDisabled(True)
        for i in range(len(self.pinYspinBox)):
            self.pinYspinBox[i].setDisabled(True)
        for i in range(len(self.xSensorSpinBox)):
            self.xSensorSpinBox[i].setDisabled(True)
        for i in range(len(self.yOutputSpinBox)):
            self.yOutputSpinBox[i].setDisabled(True)
        
        self.center()
        self.pinsWindow.show()

    def editModePins(self):
        for i in range(len(self.xSensorSpinBox)):
            self.xSensorSpinBox[i].setDisabled(False)
        for i in range(len(self.yOutputSpinBox)):
            self.yOutputSpinBox[i].setDisabled(False)
        main_window.showStatus("===> Enable define X/Y pins")

    def getxSensorBitPositon(self):
        self.xSensorDefined = []
        for i in range(len(self.xSensorSpinBox)):
            pinX = self.xSensorSpinBox[i].value() #truy xuất chân X
            for index in range(len(self.pinXspinBox)):  #index = 0 ... 15
                if pinX == index +1:
                    self.xSensorDefined.append(self.pinXspinBox[index].value())
                    break
    def getyCoilBitPosition(self):
        self.yCoilDefine = []
        for i in range(len(self.yOutputSpinBox)):
            pinY = self.yOutputSpinBox[i].value() #truy xuất chân Y
            for index in range(len(self.pinYspinBox)): #index = 0 ... 15
                if pinY == index +1:
                    self.yCoilDefine.append(self.pinYspinBox[index].value())
                    break

    def getXpinsFromJson(self):
        self.pinX = []
        pinXcomboBox = []

        xPins = main_window.jsonFile.getXpinsInfor()
        if xPins == None:
            main_window.showStatus("- can not read X pins from setting file json")
            return
        else:
            for i in range(len(xPins)):
                self.pinX.append(xPins[i])
                pinXcomboBox.append((xPins[i]))
                self.pinXspinBox[i].setValue(pinXcomboBox[i])

    def setXpinsToJson(self):
        currentXpins = []; result = []; self.pinX = []
        for i in range(len(self.pinXspinBox)):
            currentXpins.append(self.pinXspinBox[i].value())
            result.append(currentXpins[i])
            self.pinX.append(currentXpins[i])
        main_window.jsonFile.setXpinsInfor(result)
    
    def getYpinsFromJson(self):
        self.pinY = []
        pinYcomboBox = []
        yPins = main_window.jsonFile.getYpinsInfor()
        if yPins == None:
            main_window.showStatus("can not read Y pins from setting file json")
            return
        else:
            for i in range(len(yPins)):
                self.pinY.append(yPins[i])
                pinYcomboBox.append((yPins[i]))
                self.pinYspinBox[i].setValue(pinYcomboBox[i])

    def setYpinsToJson(self):
        currentYpins = []; result = []; self.pinY = []
        for i in range(len(self.pinYspinBox)):
            currentYpins.append(self.pinYspinBox[i].value())
            result.append(currentYpins[i])
            self.pinY.append(currentYpins[i])
        main_window.jsonFile.setYpinsInfor(result)
    
    def setSensorPinToJson(self):
        currentSensor = []; result = []; self.xSensor = []
        for i in range(len(self.xSensorSpinBox)):
            currentSensor.append(self.xSensorSpinBox[i].value())
            result.append(currentSensor[i])
            self.xSensor.append(currentSensor[i])
        main_window.jsonFile.setXsensorInfor(result)
    
    def getSensorPinFromJson(self):
        self.xSensor = []
        xSensorSpinBox = []

        xSensor = main_window.jsonFile.getXsensorInfor()
        if xSensor == None:
            main_window.showStatus("- can not read sensor value from json file")
            return
        else:
            for i in range(len(xSensor)):
                self.xSensor.append(xSensor[i])
                xSensorSpinBox.append((xSensor[i]))
                self.xSensorSpinBox[i].setValue(xSensorSpinBox[i])

    def setOutputPinToJson(self):
        currentOutput = []; result = []; self.yOutput = []
        for i in range(len(self.yOutputSpinBox)):
            currentOutput.append(self.yOutputSpinBox[i].value())
            result.append(currentOutput[i])
            self.yOutput.append(currentOutput[i])
        main_window.jsonFile.setYoutputInfor(result)
    
    def getOutputPinFromJson(self):
        self.yOutput = []
        yOutputSpinBox = []

        yOutput = main_window.jsonFile.getYoutputInfor()
        if yOutput == None:
            main_window.showStatus("- can not read output value from json file")
            return
        else:
            for i in range(len(yOutput)):
                self.yOutput.append(yOutput[i])
                yOutputSpinBox.append((yOutput[i]))
                self.yOutputSpinBox[i].setValue(yOutputSpinBox[i])

    def saveXYpinsToJson(self):
        self.setXpinsToJson()
        self.setYpinsToJson()
        self.setSensorPinToJson()
        self.setOutputPinToJson()
        self.getxSensorBitPositon()
        self.getyCoilBitPosition()
        main_window.getSpecsOfSensor() # cập nhật giá trị cảm biến
        main_window.getSpecsOfCoilY()
        try:
            main_window.sendMotorSensorBitPostoArduino()
            main_window.sendOutputBitPostoArduino()
        except:
            pass
        self.closePinsWindow()
#================================================================================================
# ====> test ok
class paramWindow:
    def __init__(self):
       
        self.settingWin = QWidget()
        self.uiSetting = Ui_motorSettings()
        self.uiSetting.setupUi(self.settingWin)

        self.uiSetting.buttonBox.rejected.connect(self.closeParamWindow)
        self.uiSetting.buttonBox.accepted.connect(self.save_settings)

    def closeParamWindow(self):
        self.settingWin.close()

    def center(self):
        qtRectangle = self.settingWin.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.settingWin.move(qtRectangle.topLeft()) 

    def showParamWindow(self):
        self.center()
        self.settingWin.show()
        self.getParameter()

    # truy xuat giá trị cài đặt motor từ file json
    def getParameter(self):
        gearbox_value = []; microStep_value = []; diameter_value = []
        try:
            motorSetting = main_window.jsonFile.getMotorInfo() 

            for i in range(len(motorSetting)):
                gearbox_value.append(motorSetting[i]["gear"]) 
                microStep_value.append(motorSetting[i]["microStep"]) 
                diameter_value.append(motorSetting[i]["diameter"]) 

                index = []
                index = [gearbox_value[i], microStep_value[i], diameter_value[i]]

                for j in range(len(index)):
                    self.uiSetting.tableWidget.setItem( j, i, QtWidgets.QTableWidgetItem(index[j]))
            # các giá trị được define trong self.gearbox_value, ... được tự động lưu trong self.gearbox_X, ...
            # truy xuất bắng cách: self.gearbox_X.get()

        except Exception as error:
            main_window.showStatus("- configFile Motor Error: " + str(error))
            return

    # lưu giá trị cài đặt từ bảng vào file json        
    def save_settings(self):
        gear = []; microstep = []; diameter = []
        for i in range(main_window.MAX_AXIS):
            gear.append(self.uiSetting.tableWidget.item(0, i).text())
            microstep.append(self.uiSetting.tableWidget.item(1, i).text())
            diameter.append(self.uiSetting.tableWidget.item(2, i).text())

        main_window.showStatus("- Tỉ số truyền hộp số, vi bước và đường kính bánh răng: ") 
        main_window.showStatus(gear)
        main_window.showStatus(microstep)
        main_window.showStatus(diameter)

        main_window.jsonFile.setMotorInfor(gear, microstep, diameter)   # lưu các thông số cài đặt motor
        result = self.calculate_gearRatio(gear, microstep, diameter)
        if result != []:
            main_window.jsonFile.setGearInfor(result)                       #lưu giá trị gearratio đã tính toán được
            main_window.saveGearRatio(result)

    def calculate_gearRatio(self, gear, microstep, diameter):
        result = []
        try:
            gear_ratio_X = (float(diameter[0])*math.pi)/(int(microstep[0])*float(gear[0]))
            gear_ratio_Y = (float(diameter[1])*math.pi)/(int(microstep[1])*float(gear[1]))
            gear_ratio_Z = (float(diameter[2])*math.pi)/(int(microstep[2])*float(gear[2]))
            gear_ratio_A = float(diameter[3])/(int(microstep[3])*float(gear[3]))
            gear_ratio_B = float(diameter[4])/(int(microstep[4])*float(gear[4]))
            gear_ratio_C = float(diameter[5])/(int(microstep[5])*float(gear[5]))
            result = [gear_ratio_X, gear_ratio_Y, gear_ratio_Z,gear_ratio_A, gear_ratio_B, gear_ratio_C]

        except Exception as e:
            main_window.showStatus("- wrong number value - check again")

        return result

#================================================================================================
# teaching Window
class MyTeachingWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        pass
    
    def closeEvent(self,event):
      
        teachWindow.closeTeachWindow()

#================================================================================================
class teachingWindow:
    def __init__(self):
        self.teachWin = MyTeachingWindow() 
        self.uiteach = Ui_teachMode()
        self.uiteach.setupUi(self.teachWin)
       
        self.forward = 1
        self.reverse = -1
       
        self.TEACH_X_AXIS = 0  # teach trục X
        self.TEACH_Y_AXIS = 1  # teach truc Y
        self.TEACH_Z_AXIS = 2  # teach truc Z
        self.TEACH_A_AXIS = 3  # teach trục A
        self.TEACH_B_AXIS = 4  # teach trục B
        self.TEACH_C_AXIS = 5  # teach trục C
        self.TEACH_Z1_AXIS = 6 # teach trục C

        self.button_active = 0
        self.teach_axis = -1   # biến lựa chọn trục cần chạy trong teach mode
        self.monitor_off = True

        self.pre_string_value = [(' X'+'0.0'),(' Y'+'0.0'),(' Z'+'0.0'),(' A'+'0.0'),(' B'+'0.0'),(' C'+'0.0'),
                                 (' S'+'0'),(' F'+'0')]
        self.counter_line = 0

        self.defineTeachModeButton()

    def center(self):
        qtRectangle = self.teachWin.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.teachWin.move(qtRectangle.topLeft()) 
   
    def showTeachWindow(self):
        main_window.showStatus("Open Teaching Box")
        main_window.uiWorking.label_directory.clear()
        main_window.uiWorking.textBrowser_showfile.clear()
        main_window.disable_control_option(True)
        main_window.disableMenuButton(True)
        self.reInitTeachMode()
        self.center()
        self.teachWin.show()

    def closeTeachWindow(self):
        if comWindow.connectSignal == True:
            self.monitor_off = True
        else:
            self.monitor_off = True
            self.teachWin.close()
            main_window.disable_control_option(False)
            main_window.disableMenuButton(False)
            main_window.showStatus("Close Teaching Box")
        
    def defineTeachModeButton(self):

        teach_command_deactive = [self.deactive, self.deactive, self.deactive, self.deactive, 
                                   self.deactive, self.deactive, self.deactive]

        self.teachModeButton_Fw = [self.uiteach.pushButton_xFw, self.uiteach.pushButton_yFw, self.uiteach.pushButton_zFw,
                                    self.uiteach.pushButton_aFw, self.uiteach.pushButton_bFw, self.uiteach.pushButton_cFw,
                                    self.uiteach.pushButton_z1Up] 

        teachModeButtonFwCommand = [self.buttonX_forward, self.buttonY_forward, self.buttonZ_forward,
                                self.buttonA_forward, self.buttonB_forward, self.buttonC_forward,self.buttonZ1_forward]

        for i in range(len(self.teachModeButton_Fw)): 
            self.teachModeButton_Fw[i].pressed.connect(teachModeButtonFwCommand[i])
            self.teachModeButton_Fw[i].released.connect(teach_command_deactive[i])

        self.teachModeButton_Rw = [ self.uiteach.pushButton_xRw, self.uiteach.pushButton_yRw, self.uiteach.pushButton_zRw,
                                    self.uiteach.pushButton_aRw, self.uiteach.pushButton_bRw, self.uiteach.pushButton_cRw,
                                    self.uiteach.pushButton_z1down]
        
        teachModeButtonRwCommand = [self.buttonX_reverse, self.buttonY_reverse, self.buttonZ_reverse, self.buttonA_reverse,
                                    self.buttonB_reverse, self.buttonC_reverse, self.buttonZ1_reverse]
        
        for i in range(len(self.teachModeButton_Rw)): 
            self.teachModeButton_Rw[i].pressed.connect(teachModeButtonRwCommand[i])
            self.teachModeButton_Rw[i].released.connect(teach_command_deactive[i])

        self.teachModeButton_coil = [self.uiteach.pushButton_tableFw, self.uiteach.pushButton_tableRw,
                                     self.uiteach.pushButton_sprayOn, self.uiteach.pushButton_sprayOff]
        
        teachModeButton_coilCommand = [self.tableRorateFW, self.tableRorateRW, self.sprayON, self.sprayOFF]
        for i in range(len(self.teachModeButton_coil)): 
            self.teachModeButton_coil[i].clicked.connect(teachModeButton_coilCommand[i])

        self.teachModeButton_coilM = [self.uiteach.pushButton_coilM1, self.uiteach.pushButton_coilM2,
                                     self.uiteach.pushButton_coilM3, self.uiteach.pushButton_coilM4]
        teachModeButton_coilMCommand = [self.toggleCoilM1, self.toggleCoilM2, self.toggleCoilM3, self.toggleCoilM4]
        for i in range(len(self.teachModeButton_coilM)): 
            self.teachModeButton_coilM[i].clicked.connect(teachModeButton_coilMCommand[i])

        self.teachModeButton_control = [self.uiteach.pushButton_savePoint, self.uiteach.pushButton_saveFile]
        teachModeButton_controlCommand = [self.setPoint, self.saveTofile]
        for i in range(len(self.teachModeButton_control)): 
            self.teachModeButton_control[i].clicked.connect(teachModeButton_controlCommand[i])
       
    def reInitTeachMode(self):
        self.button_active = 0
        self.teach_axis = -1   # biến lựa chọn trục cần chạy trong teach mode
        self.monitor_off = False
        self.pre_string_value = [(' X'+'0.0'),(' Y'+'0.0'),(' Z'+'0.0'),(' A'+'0.0'),(' B'+'0.0'),(' C'+'0.0'),
                                 (' S'+'0'),(' F'+'0')]
        self.counter_line = 0

    def buttonX_forward(self):
        
        self.teach_axis = self.TEACH_X_AXIS
        self.button_active = self.forward

    def buttonX_reverse(self):
        
        self.teach_axis = self.TEACH_X_AXIS
        self.button_active = self.reverse

    def buttonY_forward(self):
        
        self.teach_axis = self.TEACH_Y_AXIS
        self.button_active = self.forward

    def buttonY_reverse(self):
        
        self.teach_axis = self.TEACH_Y_AXIS
        self.button_active = self.reverse

    def buttonZ_forward(self):
        
        self.teach_axis = self.TEACH_Z_AXIS
        self.button_active = self.forward

    def buttonZ_reverse(self):
        
        self.teach_axis = self.TEACH_Z_AXIS
        self.button_active = self.reverse

    def buttonB_forward(self):
       
        self.teach_axis = self.TEACH_B_AXIS
        self.button_active = self.forward

    def buttonB_reverse(self):
        
        self.teach_axis = self.TEACH_B_AXIS
        self.button_active = self.reverse

    def buttonC_forward(self):
        
        self.teach_axis = self.TEACH_C_AXIS
        self.button_active = self.forward

    def buttonC_reverse(self):
       
        self.teach_axis = self.TEACH_C_AXIS
        self.button_active = self.reverse

    def buttonA_forward(self):
       
        self.teach_axis = self.TEACH_A_AXIS
        self.button_active = self.forward

    def buttonA_reverse(self):
       
        self.teach_axis = self.TEACH_A_AXIS
        self.button_active = self.reverse    

    def buttonZ1_forward(self):
       
        self.teach_axis = self.TEACH_Z1_AXIS
        self.button_active = self.forward

    def buttonZ1_reverse(self):
        
        self.teach_axis = self.TEACH_Z1_AXIS
        self.button_active = self.reverse

    def deactive(self):
        
        self.button_active = 0

    def testGotoZero(self):
        comWindow.workSerial.commandGotoZero()
    
    def getSpeedMotor(self):
        str_result = self.uiteach.lineEdit_speed.text()
        try:
            int_result = int(str_result)
            if int_result <= 0:  int_result = 0
            if int_result >= 200: int_result = 200
        except:
            int_result = 0
        return int_result

    def setPoint(self):
        show_line = (' '+ str(self.counter_line))
        different_value = False
        exceed_limit = False

        # lay gia tri
        #F_speed =  main_window.speedMotor()
        F_speed = self.getSpeedMotor()
    
        X_value = str(round(main_window.currentPos[0],3)); Y_value = str(round(main_window.currentPos[1],3)); Z_value = str(round(main_window.currentPos[2],3))
        A_value = str(round(main_window.currentPos[3],3)); B_value = str(round(main_window.currentPos[4],3)); C_value = str(round(main_window.currentPos[5],3))
            
        Spray_state = 0 

        if  F_speed < 0: F_speed = 0
        if  F_speed > 200: F_speed = 200

        current_string_value = [(' X'+X_value), (' Y'+Y_value), (' Z'+Z_value), (' A'+ A_value), 
                                (' B'+B_value),(' C'+C_value), (' S'+ str(Spray_state)), (' F'+ str(F_speed))]
        try:
            # khi nhấn setpoint, phải đảm bảo trục X,Y,Z không đụng vào cảm biến hành trình đầu cuối
            for ii in range(len(main_window.coilXY.sensor_limmit)):
                if main_window.coilXY.sensor_limmit[ii] == 0:
                    exceed_limit = True
                    break
            if exceed_limit == True:
                main_window.showStatus("- limited: exceed sensor limit")
                pass
        except:
            return
        # so sánh các phần tử để tìm ra phần tử có giá trị khác so với giá trị của phần tử trước đó.
        # sau đó lưu vào chuỗi
        for i in range(len(current_string_value)):
            if (current_string_value[i] != self.pre_string_value[i]):
                self.pre_string_value[i] = current_string_value[i]
                show_line = show_line + current_string_value[i]
                different_value = True
            else:
                pass
        # nếu xuất hiện phần tử có giá trị khác trước đó thì in ra màn hình
        if (different_value == True):
            self.counter_line += 1
            main_window.uiWorking.textBrowser_showfile.append(show_line) 
            main_window.showStatus("- set point: " + show_line)

    def saveTofile(self):
        main_window.showStatus('===> Lưu file.pnt')
        main_window.uiWorking.textBrowser_showfile.append(run.turn_off_spray)
        main_window.uiWorking.textBrowser_showfile.append(run.go_to_1st_point)  # command về vị trí zero
        #main_window.uiWorking.textBrowser_showfile.append(run.table_rotary)     # ghi ký tự command xoay bàn sơn
        main_window.uiWorking.textBrowser_showfile.append(run.end_symbol)       # ghi ký tự nhận diện end file
        retrieve_text = main_window.uiWorking.textBrowser_showfile.toPlainText()
        wFile.save_file(retrieve_text)
        main_window.showStatus(wFile.saveFileStatus)

    def toggleCoilM1(self):
        main_window.uiWorking.textBrowser_showfile.append("- toggle coilM1" )
        main_window.uiWorking.textBrowser_showfile.append(run.toggleCoilM1 )
        run.command_toggle_coilM1()

    def toggleCoilM2(self):
        main_window.uiWorking.textBrowser_showfile.append("- toggle coilM2" )
        main_window.uiWorking.textBrowser_showfile.append(run.toggleCoilM2 )
        run.command_toggle_coilM2()

    def toggleCoilM3(self):
        main_window.uiWorking.textBrowser_showfile.append("- toggle coilM3" )
        main_window.uiWorking.textBrowser_showfile.append(run.toggleCoilM3 )
        run.command_toggle_coilM3()
      
    def toggleCoilM4(self):
        main_window.uiWorking.textBrowser_showfile.append("- Toggle coilM4" )
        main_window.uiWorking.textBrowser_showfile.append(run.toggleCoilM4 )
        run.command_toggle_coilM4()
     
    def tableRorateFW(self):
        main_window.uiWorking.textBrowser_showfile.append("- table rotary" )
        main_window.uiWorking.textBrowser_showfile.append(run.table_rotary )
        run.command_table_rotate()

    def tableRorateRW(self):
        main_window.uiWorking.textBrowser_showfile.append("- table rotary" )
        main_window.uiWorking.textBrowser_showfile.append(run.table_rotary)
        run.command_table_rotate()

    def sprayON(self):
        main_window.uiWorking.textBrowser_showfile.append("- turn on spray" )
        main_window.uiWorking.textBrowser_showfile.append(run.turn_on_spray)
        run.command_run_spray(1)

    def sprayOFF(self):
        main_window.uiWorking.textBrowser_showfile.append("- turn off spray" )
        main_window.uiWorking.textBrowser_showfile.append(run.turn_off_spray)
        run.command_run_spray(0)
#================================================================================================
class workingTeachMode():
    def __init__(self):

        self.pos_Yspray = 6
        self.pos_Zspray = 7
        self.pre_button_state = 0 
        self.no_choise_axis = -1
        self.xAXIS = 0; self.yAXIS = 1; self.zAXIS = 2; self.aAXIS = 3
        self.bAXIS = 4; self.cAXIS = 5; self.z1AXIS = 6
   
    def read_state_button(self):
        state = teachWindow.button_active
        return state

    def read_teach_axis(self):
        state = teachWindow.teach_axis
        return state

    def monitorTeachMode(self): 
        try:
            self.chooseAxis = self.no_choise_axis
            new_pos_X = 0; new_pos_Y = 0; new_pos_A = 0
            new_pos_B = 0; new_pos_C = 0; new_pos_Z = 0
            
            while comWindow.connectSignal == True:
                self.pulse_teach_packet = [0,0,0,0,0,0]
                state_runing = False
                self.chooseAxis = self.read_teach_axis()
                self.button_state = self.read_state_button()
                self.Kinematics_Zaxis_mode_02()
                
                # gửi command quay chiều thuận trục được chọn
                if self.chooseAxis == self.xAXIS:
                    
                    if (self.button_state > self.pre_button_state):  new_pos_X = -1200
                    if (self.button_state < self.pre_button_state):  new_pos_X = 1200
                    pulse_teach = int((new_pos_X - main_window.currentPos[self.xAXIS])/main_window.gearRatio[self.xAXIS])
                    if  main_window.currentPos[self.xAXIS] < -1200 or  main_window.currentPos[self.xAXIS] > 1200: 
                        self.button_state = self.pre_button_state
        
                if self.chooseAxis == self.yAXIS:
                    if (self.button_state > self.pre_button_state):  new_pos_Y = -1600
                    if (self.button_state < self.pre_button_state):  new_pos_Y = 1600
                    pulse_teach = int((new_pos_Y - main_window.currentPos[ self.yAXIS])/main_window.gearRatio[self.yAXIS])
                    if  main_window.currentPos[self.yAXIS] < -1600 or  main_window.currentPos[ self.yAXIS] > 1600: 
                        self.button_state = self.pre_button_state

                if self.chooseAxis == self.zAXIS:
                    if (self.button_state > self.pre_button_state):  new_pos_Z = -1000
                    if (self.button_state < self.pre_button_state):  new_pos_Z = 1000
                    pulse_teach = int((new_pos_Z - main_window.currentPos[self.zAXIS])/main_window.gearRatio[self.zAXIS])
                    if  main_window.currentPos[self.zAXIS] < -1000 or  main_window.currentPos[self.zAXIS] > 1000: 
                        self.button_state = self.pre_button_state

                if self.chooseAxis == self.aAXIS:
                    if (self.button_state > self.pre_button_state):  new_pos_A = 0 #-180
                    if (self.button_state < self.pre_button_state):  new_pos_A = 90 #180
                    pulse_teach = int((new_pos_A -  main_window.currentPos[self.aAXIS])/main_window.gearRatio[self.aAXIS])
                    if main_window.currentPos[self.aAXIS] < 0 or main_window.currentPos[self.aAXIS] > 90: 
                        self.button_state = self.pre_button_state

                if (self.chooseAxis == self.bAXIS): 
                    if (self.button_state > self.pre_button_state):  new_pos_B = -180
                    if (self.button_state < self.pre_button_state):  new_pos_B = 180
                    pulse_teach = int((new_pos_B - main_window.currentPos[self.bAXIS])/main_window.gearRatio[self.bAXIS])
                    if main_window.currentPos[self.bAXIS] < -180 or main_window.currentPos[self.bAXIS] > 180: 
                        self.button_state = self.pre_button_state

                if (self.chooseAxis == self.cAXIS):
                    if (self.button_state > self.pre_button_state):  new_pos_C = -1000
                    if (self.button_state < self.pre_button_state):  new_pos_C = 1000
                    pulse_teach = int((new_pos_C - main_window.currentPos[self.cAXIS])/main_window.gearRatio[self.cAXIS])
                    if main_window.currentPos[self.cAXIS] < -1000 or main_window.currentPos[self.cAXIS] > 1000: 
                        self.button_state = self.pre_button_state

                if self.button_state != self.pre_button_state:
                    self.pulse_teach_packet[self.chooseAxis] = pulse_teach   
                    run.send_to_execute_board(self.pulse_teach_packet,0)
                    state_runing = True
        
                while state_runing:
                    # Đọc giá trị thanh ghi lưu giá trị xung đang phát ra
                    self.button_state = self.read_state_button()
                    if self.button_state == self.pre_button_state:
                        run.stop_motor()
                        state_runing = False
                        break  # thoat khỏi vong lặp while
                    time.sleep(0.1)

                if teachWindow.monitor_off == True:
                    main_window.disable_control_option(False)
                    main_window.disableMenuButton(False)
                    main_window.threadTeachMode.finishedTeachMode.emit()
                    break
                # trường hợp đang trong teachmode nhưng bị lỗi sensor
                if main_window.coilXY.errorSensorSignal == True:
                    main_window.go_machine_home = False
                    main_window.disable_control_option(False)
                    main_window.disableMenuButton(False)
                    
                    main_window.threadTeachMode.finishedTeachMode.emit()
                    break

                time.sleep(0.1)
            
        except Exception as e:
            main_window.window.showText_signal.emit("- teaching mode warning: "+ str(e))
            main_window.threadTeachMode.finishedTeachMode.emit()

    def Kinematics_Zaxis_mode_02(self):
            if self.chooseAxis == self.z1AXIS:
                Yspray_expect = main_window.currentPos[self.pos_Yspray]
                while True:
                    running = False
                    self.button_state = self.read_state_button()
                    if (self.button_state > self.pre_button_state): # nhấn Z1-
                        # tính động học
                        new_pos_A = main_window.currentPos[self.aAXIS] - 2
                        new_pos_Y = Yspray_expect - main_window.spray_axis*math.cos((new_pos_A*math.pi)/180)
                        new_pos_Z = 0
                        pulse_Y_teach = int((new_pos_Y - main_window.currentPos[self.yAXIS])/main_window.gearRatio[self.yAXIS])
                        pulse_A_teach = int((new_pos_A - main_window.currentPos[self.aAXIS])/main_window.gearRatio[self.aAXIS])
                        pulse_Z_teach = int((new_pos_Z - main_window.currentPos[self.zAXIS])/main_window.gearRatio[self.zAXIS])

                        if(main_window.currentPos[self.zAXIS] > 0):  self.pulse_teach_packet = [0,0,pulse_Z_teach,0,0,0]
                        else:                                               self.pulse_teach_packet = [0,pulse_Y_teach,0,pulse_A_teach,0,0]
                        
                    if (self.button_state < self.pre_button_state): # nhấn Z1+
                        
                        new_pos_A = main_window.currentPos[self.aAXIS] + 2 #(góc A của mỗi lần chạy: càng nhỏ chạy càng chính xác)
                        new_pos_Y = Yspray_expect - main_window.spray_axis*math.cos((new_pos_A*math.pi)/180)
                        new_pos_Z = 600
                        pulse_A_teach = int((new_pos_A - main_window.currentPos[self.aAXIS])/main_window.gearRatio[self.aAXIS])
                        pulse_Y_teach = int((new_pos_Y - main_window.currentPos[self.yAXIS])/main_window.gearRatio[self.yAXIS])
                        pulse_Z_teach = int((new_pos_Z - main_window.currentPos[self.zAXIS])/main_window.gearRatio[self.zAXIS])
                        if new_pos_A >= 90: self.pulse_teach_packet = [0,0,pulse_Z_teach,0,0,0]
                        else:               self.pulse_teach_packet = [0,pulse_Y_teach,0,pulse_A_teach,0,0]
                    
                    if self.button_state != self.pre_button_state:
                        run.send_to_execute_board(self.pulse_teach_packet,0)
                        running = True

                    while running:
                        self.button_state = self.read_state_button()
                        if self.button_state == self.pre_button_state:
                            run.stop_motor()
                            running = False
                            break  # thoat khỏi vong lặp while
                        time.sleep(0.1)
                    
                    # nếu disable teach mode thì thoát khỏi 
                    if teachWindow.monitor_off == True | self.chooseAxis != self.zAXIS:
                        break

                    time.sleep(0.1)
            else: pass
#================================================================================================
# Thread trong monitor teach mode/goto zero/ goto Home
class monitorTeachModeThread(QObject):
    finishedTeachMode = pyqtSignal()
    finishedGotoZeroMode = pyqtSignal()
    finishedGotoHomeMode = pyqtSignal()

    def __init__(self, parent=None):
        super(monitorTeachModeThread, self).__init__(parent)

    def run(self):
        main_window.window.showText_signal.emit("Thread: teachMode/gotoZero/gotoHome")
        while True:
            if teachWindow.monitor_off == False:
                teach.monitorTeachMode()
            if main_window.gotoZeroFlag == True:
                main_window.gotoZeroPosition() 
            if main_window.gotoHomeFlag == True:
                main_window.gotoMachinePosition() 
            time.sleep(0.05)

    def stopGotoZero(self):
        main_window.gotoZeroFlag = False
        main_window.window.showText_signal.emit("Exit execute: goto Zero")

    def stopGotoHome(self):
        main_window.gotoHomeFlag = False
        main_window.window.showText_signal.emit("Exit execute: goto Home")
    
    def stopTeachMode(self):
        teachWindow.teachWin.close()
        main_window.window.showText_signal.emit("Exit execute: teaching Mode")
#================================================================================================
# Thread monitor input/ouput and current position
class monitorDatafromArduinoThread(QObject):
    coilValue =  pyqtSignal(tuple)  
    posValue = pyqtSignal(list)

    def __init__(self, parent=None):
        super(monitorDatafromArduinoThread, self).__init__(parent)
    def run(self):
        main_window.window.showText_signal.emit("Thread: Monitor input/output and current position")
        while True:
            coil_Value = main_window.coilXY.read_coilXY()
            pos_Value = main_window.showCurrentPositions()
            self.posValue.emit(pos_Value)
            if coil_Value != None:
                main_window.coilXY.sensor_value = main_window.coilXY.returnXvalue(coil_Value)
                main_window.coilXY.coil_value = main_window.coilXY.returnYvalue(coil_Value)
                self.coilValue.emit(coil_Value)
            else: pass
            
            # Getting all memory using os.popen()
            if os.name == 'posix': # os -> Linux
                total_memory, used_memory, free_memory = map(
                    int, os.popen('free -t -m').readlines()[-1].split()[1:])
                ramUsed = round((used_memory/total_memory) * 100, 1)

                getTime = QTime.currentTime()
                mytime = getTime.toString()
                main_window.uiWorking.label_showtime.setText(mytime +"/"+str(ramUsed)+'%')

            if os.name == 'nt': # neu os -> window
                getTime = QTime.currentTime()
                mytime = getTime.toString()
                main_window.uiWorking.label_showtime.setText(mytime)

            time.sleep(0.05)
#================================================================================================
# Thread trong autoRun
class autoRunThread(QObject):
    finished = pyqtSignal()
    def __init__(self, parent=None):
        super(autoRunThread, self).__init__(parent)
    def run(self):
        main_window.window.showText_signal.emit("Thread: Auto run mode")
        while True:
            if main_window.autoRunFlag == True:
                run.activate_run_mode()
            time.sleep(0.1)

    def stop(self):
        main_window.autoRunFlag = False
        main_window.window.showText_signal.emit("Exit execute: Auto run mode")
#================================================================================================
# Confirm exit workingWindow
class MyWindow(QtWidgets.QMainWindow, QObject):
    showText_signal = pyqtSignal(str)
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)

    def closeEvent(self,event):
        mBox = QtWidgets.QMessageBox()
        mBox.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowStaysOnTopHint)
        result = mBox.question(self,
                      "Confirm Exit...",
                      "Are you sure you want to exit ?",
                      mBox.Yes| mBox.No)
        event.ignore()

        if result == mBox.Yes:   
            
            teachWindow.teachWin.close()
            comWindow.detroyComWindow()
            main_window.definePinsWindow.closePinsWindow()
            setMotor.closeParamWindow()
            
            if comWindow.connectSignal == True:
                comWindow.workSerial.stopSerial()
                main_window.threadTeachMode.finishedTeachMode.emit()
            
            main_window._threadTeachMode.quit(); main_window._threadTeachMode.wait(100)
            main_window._threadMonitorDataFromArduino.quit(); main_window._threadMonitorDataFromArduino.wait(100)
            main_window._threadAutoRun.quit(); main_window._threadAutoRun.wait(100)

            event.accept()
    
#================================================================================================
class workingWindow:
    def __init__(self):
        self.window = MyWindow()
        self.uiWorking = Ui_MainWindow()
        self.uiWorking.setupUi(self.window)
        self.jsonFile = makeJsonSetting()
        self.definePinsWindow = setPinsWindow()
        self.coilXY = monitorInputOutput()
        # Orange pi pc plus su dung Quad-core CPU (4 loi) -> Qthread tao toi da them 3 worker Thread + 1 main Thread
        self.threadTeachMode = monitorTeachModeThread()
        self.threadAutoRun = autoRunThread()
        self.threadMonitorDataFromArduino = monitorDatafromArduinoThread()

        self.window.showText_signal.connect(self.showStatus)

        self.defineControlButton()
        self.defineCheckButton()
        self.defineWarningLabel()
        self.defineSliders()

        self.currentPos = [0,0,0,0,0,0,0,0]
        self.gearRatio = []
        self.MAX_AXIS = 6
        self.spray_axis = 550
        self.go_machine_home = False
        self.checkValue = -1

        self.gotoZeroFlag = False
        self.gotoHomeFlag = False
        self.autoRunFlag = False

        # Khai báo sử dụng đa luồng được quản lý bới Qthread
   
        self.declareThreadMonitorDataFromArduino()
        self.declareThreadTeachingMode()
        self.declareThreadAutoRun()

    def declareThreadAutoRun(self):
        self._threadAutoRun = QThread()
        self.threadAutoRun.moveToThread(self._threadAutoRun)
        self._threadAutoRun.started.connect(self.threadAutoRun.run)
        self.threadAutoRun.finished.connect(self.threadAutoRun.stop)

    def startAutoRunThread(self):
        self._threadAutoRun.start()

    def declareThreadMonitorDataFromArduino(self):
        self._threadMonitorDataFromArduino = QThread()
        self.threadMonitorDataFromArduino.moveToThread(self._threadMonitorDataFromArduino)
        self._threadMonitorDataFromArduino.started.connect(self.threadMonitorDataFromArduino.run)
        self.threadMonitorDataFromArduino.posValue.connect(self.updateLabelPosition)
        self.threadMonitorDataFromArduino.coilValue.connect(self.coilXY.monitor_coil_XY)
        
    def startMonitorDataFromArduinoThread(self):
        self._threadMonitorDataFromArduino.start()

    def declareThreadTeachingMode(self):
        self._threadTeachMode = QThread()
        self.threadTeachMode.moveToThread(self._threadTeachMode)
        self._threadTeachMode.started.connect(self.threadTeachMode.run)
        self.threadTeachMode.finishedTeachMode.connect(self.threadTeachMode.stopTeachMode)
        self.threadTeachMode.finishedGotoZeroMode.connect(self.threadTeachMode.stopGotoZero)
        self.threadTeachMode.finishedGotoHomeMode.connect(self.threadTeachMode.stopGotoHome)
        
    def startTeachModeThread(self):
        self._threadTeachMode.start()

    def center(self):
        qtRectangle = self.window.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.window.move(qtRectangle.topLeft())

    def showWorkingWindow(self):
        self.center()
        self.window.show()

    def defineSliders(self):
        self.uiWorking.verticalSlider_speedMotor.valueChanged.connect(self.speedMotor)
        self.uiWorking.verticalSlider_spray.valueChanged.connect(self.speedSpray)
        self.uiWorking.label_speedMotor.setText("F"+ str(self.uiWorking.verticalSlider_speedMotor.value()))
        self.uiWorking.value_speedSpray.setText("S"+ str(self.uiWorking.verticalSlider_spray.value()))
     
    def defineControlButton(self):

        self.lableG54Position = [self.uiWorking.label_Xposition, self.uiWorking.label_Yposition, self.uiWorking.label_Zposition, 
                                    self.uiWorking.label_Aposition, self.uiWorking.label_Bposition, self.uiWorking.label_Cposition]

        self.lableMachinePosition = [self.uiWorking.label_Xhome, self.uiWorking.label_Yhome, self.uiWorking.label_Zhome, self.uiWorking.label_Ahome,
                                        self.uiWorking.label_Bhome,self.uiWorking.label_Chome]

        self.labelGunPosition = [self.uiWorking.label_xSpray, self.uiWorking.label_ySpray, self.uiWorking.label_zSpray]
        
        self.controlButtonName = [ self.uiWorking.pushButton_gotozero, self.uiWorking.pushButton_machinehome, 
                                self.uiWorking.pushButton_auto,  self.uiWorking.pushButton_jog, self.uiWorking.pushButton_pause,
                                self.uiWorking.pushButton_estop]

        self.controlButtonCommand = [ self.startgotoZeroPosition, self.startgotoMachinePosition, self.runAutoCycle,
                                         self.runJog, self.pauseMotor, self.eStopMotor]
        for i in range(len(self.controlButtonName)):
            self.controlButtonName[i].clicked.connect(self.controlButtonCommand[i])

        self.uiWorking.actionChoose_File_pnt.triggered.connect(self.chooseFile)
        self.uiWorking.actionConnect_to_Slave.triggered.connect(self.chooseComPort)
        self.uiWorking.actionMotor.triggered.connect(self.openSettingMotor)
        self.uiWorking.actionTeachMode.triggered.connect(self.openTeachWindow)
        self.uiWorking.actionDefine_XY.triggered.connect(self.openDefinePinsWindow)

    def defineCheckButton(self):
        self.checkButtonCoilY = [self.uiWorking.checkBoxY1, self.uiWorking.checkBoxY2, self.uiWorking.checkBoxY3, self.uiWorking.checkBoxY4,
                                self.uiWorking.checkBoxY5, self.uiWorking.checkBoxY6, self.uiWorking.checkBoxY7, self.uiWorking.checkBoxY8,
                                self.uiWorking.checkBoxY9, self.uiWorking.checkBoxY10, self.uiWorking.checkBoxY11, self.uiWorking.checkBoxY12, 
                                self.uiWorking.checkBoxY13, self.uiWorking.checkBoxY14, self.uiWorking.checkBoxY15, self.uiWorking.checkBoxY16 ]
        
        getCheckBoxValue = [self.coilXY.returnCoilY1, self.coilXY.returnCoilY2, self.coilXY.returnCoilY3, self.coilXY.returnCoilY4, self.coilXY.returnCoilY5, self.coilXY.returnCoilY6,
                                    self.coilXY.returnCoilY7, self.coilXY.returnCoilY8,self.coilXY.returnCoilY9, self.coilXY.returnCoilY10, self.coilXY.returnCoilY11, self.coilXY.returnCoilY12,
                                    self.coilXY.returnCoilY13, self.coilXY.returnCoilY14, self.coilXY.returnCoilY15, self.coilXY.returnCoilY16 ]

        for i in range(len(self.checkButtonCoilY)):
            self.checkButtonCoilY[i].setChecked(False)
            self.checkButtonCoilY[i].toggled.connect(getCheckBoxValue[i])

        self.labelCoilY = [self.uiWorking.label_y1, self.uiWorking.label_y2, self.uiWorking.label_y3, self.uiWorking.label_y4, 
                           self.uiWorking.label_y5, self.uiWorking.label_y6, self.uiWorking.label_y7, self.uiWorking.label_y8, 
                           self.uiWorking.label_y9, self.uiWorking.label_y10, self.uiWorking.label_y11, self.uiWorking.label_y12,
                           self.uiWorking.label_y13, self.uiWorking.label_y14, self.uiWorking.label_y15, self.uiWorking.label_y16]
        self.orgColorLabelY = []
        for i in range(len(self.labelCoilY)):
            self.orgColorLabelY.append(self.labelCoilY[i].palette().window().color().name())

        self.labelCoilX =  [self.uiWorking.label_x1, self.uiWorking.label_x2, self.uiWorking.label_x3, self.uiWorking.label_x4, 
                           self.uiWorking.label_x5, self.uiWorking.label_x6, self.uiWorking.label_x7, self.uiWorking.label_x8, 
                           self.uiWorking.label_x9, self.uiWorking.label_x10, self.uiWorking.label_x11, self.uiWorking.label_x12,
                           self.uiWorking.label_x13, self.uiWorking.label_x14, self.uiWorking.label_x15, self.uiWorking.label_x16]
        self.orgColorLabelX = []
        for i in range(len(self.labelCoilX)):
            self.orgColorLabelX.append(self.labelCoilX[i].palette().window().color().name())

    def defineWarningLabel(self):
        self.warningLabel = [self.uiWorking.label_xhome, self.uiWorking.label_yhome, self.uiWorking.label_zhome,
                            self.uiWorking.label_ahome, self.uiWorking.label_xlimit, self.uiWorking.label_ylimit,
                            self.uiWorking.label_zlimit, self.uiWorking.label_alimit]
        self.orgColorWarningLabel = []
        for i in range(len(self.warningLabel)):
            self.orgColorWarningLabel.append(self.warningLabel[i].palette().window().color().name())

    # disable when auto running
    def disableMenuButton(self, state):
        self.uiWorking.actionChoose_File_pnt.setDisabled(state)
        self.uiWorking.actionSave_file.setDisabled(state)
        self.uiWorking.actionConnect_to_Slave.setDisabled(state)
        self.uiWorking.actionMotor.setDisabled(state)
        self.uiWorking.actionDefine_XY.setDisabled(state)
        self.uiWorking.actionToggleCoilY.setDisabled(state)
        self.uiWorking.actionTeachMode.setDisabled(state)
        # disable goto zero and goto Home button when auto running
        self.uiWorking.pushButton_gotozero.setDisabled(state)
        self.uiWorking.pushButton_machinehome.setDisabled(state)
        
    def disable_control_option(self, state):
        for i in range(len(self.controlButtonName)):
            self.controlButtonName[i].setDisabled(state)


    def speedMotor(self):
        valueSpeedMotor = self.uiWorking.verticalSlider_speedMotor.value()
        self.uiWorking.label_speedMotor.setText("M"+str(valueSpeedMotor))
        return valueSpeedMotor

    def speedSpray(self):
        valueSpeedSpray = self.uiWorking.verticalSlider_spray.value()
        self.uiWorking.value_speedSpray.setText("S"+str(valueSpeedSpray))
        return valueSpeedSpray

    def chooseFile(self):
        self.showStatus("Open file.pnt")
        try:
            pathFile = wFile.show_initial_directory()
            self.showStatus("- pathFile: "+ pathFile)
            self.uiWorking.label_directory.setText(pathFile)
            content = wFile.get_file(pathFile)
            self.uiWorking.textBrowser_showfile.setText(content)

        except Exception as error: 
            self.uiWorking.label_directory.setText("- no file loaded")
            self.showStatus("- open file error: "+ str(error))
            return

    def chooseComPort(self):
        self.showStatus("Setting COM port mode")
        comWindow.showComWindow()

    def openSettingMotor(self):
        self.showStatus("Setting motor gear ratio")
        setMotor.showParamWindow()

    def openDefinePinsWindow(self):
        self.showStatus("Declare XY pins mode")
        self.definePinsWindow.showPinsWindow()

    def openTeachWindow(self):
        teachWindow.showTeachWindow()
       
    def enterManual(self):
        self.showStatus("Toggle mode coil Y")

    def runAutoCycle(self):
        if comWindow.connectSignal == True:
            self.disableMenuButton(True)
            self.autoRunFlag = True
        else:
            self.showStatus("===> Open COM port first!!! ")

    def runJog(self):
        self.showStatus("JOG mode - run line by line")

    def pauseMotor(self):
        self.showStatus("- pause/resume program")
        run.pause_motor()

    def eStopMotor(self):
        self.showStatus("- emergency stop")
        run.disable_run_mode()

    def getSpecsOfSensor(self):
        self.coilXY.xhomeBit = self.definePinsWindow.xSensorDefined[0]; self.coilXY.yhomeBit = self.definePinsWindow.xSensorDefined[1] 
        self.coilXY.zhomeBit = self.definePinsWindow.xSensorDefined[2];  self.coilXY.ahomeBit = self.definePinsWindow.xSensorDefined[3]
        self.coilXY.xlimitBit = self.definePinsWindow.xSensorDefined[4];  self.coilXY.ylimitBit = self.definePinsWindow.xSensorDefined[5]
        self.coilXY.zlimitBit = self.definePinsWindow.xSensorDefined[6]; self.coilXY.alimitBit = self.definePinsWindow.xSensorDefined[7]

        self.coilXY.sensorBitPos = [self.coilXY.xhomeBit, self.coilXY.yhomeBit, self.coilXY.zhomeBit, self.coilXY.ahomeBit, 
                                    self.coilXY.xlimitBit, self.coilXY.ylimitBit, self.coilXY.zlimitBit, self.coilXY.alimitBit]

        self.showStatus("===> Vị trí khai báo bit sensor: "+ str(self.coilXY.sensorBitPos))

    def getSpecsOfCoilY(self):
        self.coilXY.y1Bit = self.definePinsWindow.yCoilDefine[0]; self.coilXY.y2Bit = self.definePinsWindow.yCoilDefine[1]
        self.coilXY.y3Bit = self.definePinsWindow.yCoilDefine[2]; self.coilXY.y4Bit = self.definePinsWindow.yCoilDefine[3]
        self.coilXY.y5Bit = self.definePinsWindow.yCoilDefine[4]; self.coilXY.y6Bit = self.definePinsWindow.yCoilDefine[5]
        self.coilXY.y7Bit = self.definePinsWindow.yCoilDefine[6]; self.coilXY.y8Bit = self.definePinsWindow.yCoilDefine[7]

        self.coilXY.coilYBitPos = [self.coilXY.y1Bit, self.coilXY.y2Bit, self.coilXY.y3Bit, self.coilXY.y4Bit,
                                   self.coilXY.y5Bit, self.coilXY.y6Bit,self.coilXY.y7Bit,self.coilXY.y8Bit ]
        
        self.showStatus("===> Vị trí khai báo bit coilY: "+ str(self.coilXY.coilYBitPos))

    def getXYdefinePins(self):
        self.definePinsWindow.getXpinsFromJson()
        self.definePinsWindow.getYpinsFromJson()
        self.definePinsWindow.getSensorPinFromJson()
        self.definePinsWindow.getOutputPinFromJson()
        self.definePinsWindow.getxSensorBitPositon()
        self.definePinsWindow.getyCoilBitPosition()

    def sendMotorSensorBitPostoArduino(self):
        value = [self.coilXY.xlimitBit,self.coilXY.xhomeBit,self.coilXY.ylimitBit,self.coilXY.yhomeBit,
                 self.coilXY.zlimitBit, self.coilXY.zhomeBit,  self.coilXY.alimitBit, self.coilXY.ahomeBit]
        comWindow.workSerial.settingMotorSensorBit(value)

    def sendOutputBitPostoArduino(self):
        value = [self.coilXY.y1Bit,self.coilXY.y2Bit,self.coilXY.y3Bit,self.coilXY.y4Bit,
                 self.coilXY.y5Bit, self.coilXY.y6Bit,  self.coilXY.y7Bit, self.coilXY.y8Bit]
        comWindow.workSerial.settingOuputBit(value)
    
    def getGearRatioFromJson(self):
        result = self.jsonFile.getGearRatio()
        if result != []:
            self.saveGearRatio(result)

    def saveGearRatio(self, result):
        self.getGearRatioCalculated(result)

    def getGearRatioCalculated(self, value):
        self.gearRatio.clear()
        for i in range(len(value)):
            self.gearRatio.append(value[i])
        self.showStatus("===> Hệ số xung/mm và xung/deg lưu trong chương trình: ")
        self.showStatus(str(self.gearRatio))

    def showCurrentPositions(self):
        position = self.read_pulse_from_slaves(self.gearRatio)    # trả về 8 phần tử X,Y,Z,A,B,C, pos_Yspray, pos_Zspray
        if position != None:
            for i in range(self.MAX_AXIS + 2):
                self.currentPos[i] = position[i]
        else:
            position = []
            for i in range(self.MAX_AXIS + 2):
                position.append(self.currentPos[i])
            
            main_window.window.showText_signal.emit("===> read current position failed")
 
        return position
    def updateLabelPosition(self):

        for i in range(len(self.lableG54Position)):
                self.lableG54Position[i].setText(str(round(self.currentPos[i],3)))
                self.lableMachinePosition[i].setText(str(round(self.currentPos[i],3)))

        self.labelGunPosition[0].setText(str(round(self.currentPos[0],3)))
        self.labelGunPosition[1].setText(str(round(self.currentPos[6],3)))
        self.labelGunPosition[2].setText(str(round(self.currentPos[7],3)))

    def callMotorSpeed(self):
        setSpeed = self.speedMotor()
        return setSpeed

    def read_pulse_from_slaves(self, gearRatio):
        current_position_motor = []
        current_pulse = []
        index = 0
        # Đọc giá trị xung của tất cả động cơ 
        try:
            # Đọc giá trị current position ở địa chỉ bắt đầu từ 0, đọc 12 giá trị 16 bit
            current_position = comWindow.workSerial.readCurrentPosition()
            for i in range(self.MAX_AXIS):
                current_position_motor.append((current_position[index] << 16) | (current_position[index+1] & 65535))
                index = index + 2
                current_pulse.append(self.check_negative_num(current_position_motor[i]))
            
            resultCurrentPos = self.calculateCurrentPos(current_pulse, gearRatio)

            return resultCurrentPos


        except Exception as error:
            main_window.window.showText_signal.emit("===> read pulse from slaves function failed"+ str(error))
            return None

    def check_negative_num(self, x):
        if ((x & (1<<31)) != 0):
            # This is negative num
            a = -(0xFFFFFFFF - x +1)
        else:
            a = x
        return a

    def calculateCurrentPos(self, currentPulse, gearRatio):
        currentPosition = []
        for i in range(len(currentPulse)):
            currentPosition.append(float(currentPulse[i]*gearRatio[i]))

        # vị trí Y,Z của trục súng sơn theo phương trình động học
        pos_Yspray = currentPosition[1] + self.spray_axis*math.cos((currentPosition[3]*math.pi)/180)
        pos_Zspray = currentPosition[2] + self.spray_axis*math.sin((currentPosition[3]*math.pi)/180)

        currentPosition.append(pos_Yspray)
        currentPosition.append(pos_Zspray)

        # trả về 8 phần tử X,Y,Z,A,B,C, pos_Yspray, pos_Zspray
        return currentPosition

    def startgotoZeroPosition(self):
        if comWindow.connectSignal == True:
            self.disable_control_option(True)
            self.gotoZeroFlag = True
        else:
            self.showStatus("===> Open COM port first!!! ")
      
    def gotoZeroPosition(self):
        main_window.window.showText_signal.emit("Sent command: Go to Zero Position")
        try:
            comWindow.workSerial.commandGotoZero()
            waiting = True
            while waiting:
                positionCompleted = comWindow.workSerial.commandPositionCompleted()
                if positionCompleted[0] == 1:
                    waiting = False
                time.sleep(0.1)

            main_window.window.showText_signal.emit("- goto Zero done")
        except Exception as e:
            main_window.window.showText_signal.emit("- goto Zero error status: "+str(e))
            
        self.disable_control_option(False)
        self.threadTeachMode.finishedGotoZeroMode.emit()

    def startgotoMachinePosition(self):
        if comWindow.connectSignal == True:
            self.disable_control_option(True)
            self.gotoHomeFlag = True
        else:
            self.showStatus("===> Open COM port first!!! ")

    def gotoMachinePosition(self):
        main_window.window.showText_signal.emit("Sent command: Go to Home Position")
       
        try:
            if self.go_machine_home == False:
              
                comWindow.workSerial.commandCheckXYZAsensor()
                
                pulse_to_machine_axis_X = [-36000, 0, 0, 0, 0, 0]
                pulse_to_machine_axis_Y = [0, -70000, 0, 0, 0, 0]
                pulse_to_machine_axis_Z = [0, 0, -36000, 0, 0, 0]
                pulse_to_machine_axis_A = [0, 0, 0, -32000, 0, 0]
                pulse_to_machine_axis_B = [0, 0, 0, 0, 0, 0]
                pulse_to_machine_axis_C = [0, 0, 0, 0, 0, 0]

                pulse_to_machine_axis = [pulse_to_machine_axis_X, pulse_to_machine_axis_Y, pulse_to_machine_axis_Z, 
                                            pulse_to_machine_axis_A, pulse_to_machine_axis_B, pulse_to_machine_axis_C ]
                pulse_to_begin_position = [1600, 1600, 1600, 1000, 0, 0]
                speed_axis = [30,30,30,10,10,10]

                
                # set lại các thông số motor, đưa giá trị current_position về 0
                comWindow.workSerial.setZeroPositions()
                time.sleep(0.1)
                for i in range(self.MAX_AXIS):
                    run.send_to_execute_board(pulse_to_machine_axis[i],speed_axis[i])
                    self.go_machine_axis_state = False
                    while True: 
                        # Đọc giá trị thanh ghi lưu giá trị xung đang phát ra
                        positionCompleted = comWindow.workSerial.commandPositionCompleted()
                        if (positionCompleted[0]==1 or main_window.coilXY.sensor_machine_axis[i] == 0):
                            # dừng động cơ
                            run.stop_motor()
                            self.go_machine_axis_state = True
                            break  # thoat khỏi vong lặp while
                        time.sleep(0.1)

                # sau khi chạy hết các động cơ về vị trí cảm biến
                # tịnh tiến các trục X,Y,Z ra khỏi vị trí cảm biến và set lại 0
                time.sleep(0.5)
                run.send_to_execute_board(pulse_to_begin_position,100)
                while True:
                    
                    # Đọc trạng thái phát xung đã hoàn tất chưa
                    positionCompleted = comWindow.workSerial.commandPositionCompleted()
                    # Đọc giá trị thanh ghi lưu giá trị xung đang phát ra
                    if positionCompleted[0] == 1: 
                        # set lại các thông số motor, đưa giá trị current_position về 0
                        comWindow.workSerial.setZeroPositions()
                        comWindow.workSerial.commandCheckXYZAsensor()
                        break

                    time.sleep(0.1)
                self.go_machine_home = True # đã về home

            main_window.window.showText_signal.emit("- goto Home done")

        except Exception as error:
            main_window.window.showText_signal.emit("- goto Home position error: "+ str(error))

        self.disable_control_option(False)
        self.threadTeachMode.finishedGotoHomeMode.emit()

    def showStatus(self, value):
        horScrollBar = self.uiWorking.textBrowser_terminal.horizontalScrollBar()
        verScrollBar = self.uiWorking.textBrowser_terminal.verticalScrollBar()
        self.uiWorking.textBrowser_terminal.append(str(value))
        self.uiWorking.textBrowser_terminal.moveCursor(QTextCursor.End)
        verScrollBar.setValue(verScrollBar.maximum()) # Scrolls to the bottom
        horScrollBar.setValue(0) # scroll to the left
        self.uiWorking.textBrowser_terminal.update()   # cập nhật thay đổi trong textBrower
#================================================================================================
class runMotor:
    def __init__(self):
        self.sum_xung_le = [0,0,0,0,0,0]
        self.pause_on = 0
        self.pre_result_value = [0,0,0,0,0,0,0,0] # X,Y,Z,A,B,C,S,F
        self.pre_points = [0,0,0,0,0,0]
        self.new_Fspeed = 0
        self.run_auto_mode = False          # trạng thái vào chế độ auto run
        self.counter = 0                    # lưu tổng số điểm đã truyền tới data_packet slave để chạy block mode
        self.delayTimer = 0
        self.executeDelay = False

        self.MAX_POINT_IN_BLOCK = 110     # số điểm tối đa có thể truyền tới data_packet slave trong block mode
        self.end_symbol = 'M30'           #command kết thúc chương trình
        self.start_run_block = 'G05.0'    #command bắt đầu chạy theo block N điểm
        self.end_run_block = 'G05.1'      #command kết thúc chạy theo block N điểm
        self.go_to_2nd_point = 'G30'      #command quay về điểm gốc thứ 2
        self.go_to_1st_point = 'G28'      #command quay về vị trí gốc 0 (điểm bắt đầu chạy)
        self.turn_on_spray = 'M08'        #command lệnh bật súng sơn
        self.turn_off_spray = 'M09'       #command lệnh tắt súng sơn
        self.table_rotary = 'M10'         #command xoay bàn sơn

        self.toggleCoilM1 = 'M01'
        self.toggleCoilM2 = 'M02'
        self.toggleCoilM3 = 'M03'
        self.toggleCoilM4 = 'M04'

        self.run_block_done = False

        self.e_stop = False                 # trạng thái tín hiệu nút nhấn ESTOP
#=============================================================
    def activate_run_mode(self):
        # điều kiện để chạy chương trình là vị trí ban đầu của các trục là 0 và đã set home xong.
        for i in range(main_window.MAX_AXIS):
            #if round(main_window.currentPos[i],3) == 0 and main_window.go_machine_home == True:
            if round(main_window.currentPos[i],3) == 0:
                pass
            else:
                main_window.disableMenuButton(False)
                main_window.window.showText_signal.emit("Run Auto: Go to zero/machine axis first!!!")
                main_window.threadAutoRun.finished.emit()
                return
        main_window.window.showText_signal.emit("Run Auto: Running...")
        try:
            position = wFile.file.seek(0,0) # Di chuyen con tro vi tri read file ve vi tri đầu file
            self.run_auto_mode = True
            for str_content in wFile.file:
                
                if self.e_stop == True:  # nếu có tín hiệu nhấn E-STOP
                    wFile.file.close()
                    break
                if main_window.coilXY.errorSensorSignal == True:
                    main_window.go_machine_home = False
                    wFile.file.close()
                    break

                content_line = str_content.replace(" ", "") # Bo ky tu khoang trang trong chuoi 
                content_line = content_line.upper()         # chuyen doi chuoi thanh chu IN HOA
                self.monitor_str_content(str_content.replace("\n",""))       # hiện thị từng dòng trong file
                recognizeStringArr = self.recognize_command_syntax(content_line)   # Kiểm tra các ký tự đúng cú pháp hay không

                if recognizeStringArr == True:
                    # tách số của các trục
                    result_string = self.separate_string(content_line)
                    # tính toán khoảng cách cần tịnh tiến
                    result_delta = self.calculate_delta(result_string)
                    # tính toán số xung tịnh tiến
                    result_xung_nguyen = self.calculate_pulse(result_delta)
                    # gửi khoảng cách theo đơn vị xung và tốc độ tới board execute
                    self.send_to_execute_board(result_xung_nguyen, self.new_Fspeed)
                    comWindow.workSerial.commandPointToPoint()  # phát lệnh chạy mode point to point bình thường
                    self.monitor_run_auto_next()                # giám sát chạy lệnh point to point 
                
                    if self.executeDelay == True: # có lệnh delay
                        main_window.window.showText_signal.emit("- Giá tri timer delay S: "+ str(self.delayTimer/10)+" s")
                        comWindow.workSerial.command_delayTimer(self.delayTimer)
                        while True:
                            excecuteTimerDone = comWindow.workSerial.commandDelayCompleted()
                            time.sleep(0.1)
                            if excecuteTimerDone[0] == 1:
                                self.executeDelay = False
                                break
                else:

                    if content_line == self.end_symbol + '\n' or content_line == self.end_symbol: # gặp ký hiệu báo kết thúc file
                        main_window.window.showText_signal.emit("Run Auto: End program")
                        break

                    if content_line == self.turn_on_spray + '\n': # bật súng sơn
                        self.command_run_spray(1)
                        
                    if content_line == self.turn_off_spray + '\n' : # tắt súng sơn
                        self.command_run_spray(0)
                        
                    if content_line == self.table_rotary + '\n' : # xoay bàn sơn
                        self.command_table_rotate()

                    if content_line ==  self.toggleCoilM1 +'\n' or content_line ==  self.toggleCoilM1:
                        self.command_toggle_coilM1()

                    if content_line ==  self.toggleCoilM2 +'\n' or content_line ==  self.toggleCoilM2:
                        self.command_toggle_coilM2()

                    if content_line ==  self.toggleCoilM3 +'\n' or content_line ==  self.toggleCoilM3:
                        self.command_toggle_coilM3()

                    if content_line ==  self.toggleCoilM4 +'\n' or content_line ==  self.toggleCoilM4:
                        self.command_toggle_coilM4()
                    
                    if content_line == self.go_to_1st_point + '\n' : # đi tới điểm gốc đầu tiên, điểm 0
                        main_window.gotoZeroPosition()

                    if content_line == self.go_to_2nd_point + '\n': # đi tới điểm gốc thứ 2
                        pass
                    
                    if content_line == self.start_run_block + '\n':
                        main_window.window.showText_signal.emit("- G05.0 Start block run mode")
                        result_run_block = self.send_packet_to_slave()  # giá trị trả về luôn trong khoảng [0:140]
                        if result_run_block == False: 
                            main_window.window.showText_signal.emit("- G05.1 Error !!!")
                            break
                        else: 
                            # gửi lần 2 lệnh change_state_run_block để tắt chế độ run block mode
                            main_window.window.showText_signal.emit("- Block run mode done")
                            self.counter = 0

        except Exception as e:
                main_window.window.showText_signal.emit("- Run Auto Error: " + str(e))
                main_window.disableMenuButton(False)

        finally:
            self.re_init()
            main_window.disableMenuButton(False)
            main_window.threadAutoRun.finished.emit()

# gui N packet tới board slave, hàm trả về số điểm đã gửi tới board slave            
    def send_packet_to_slave(self):
        sent_packet_done = False
        sent_point = 0
        target_line = ' '
        run_block = False

        for str_content in wFile.file:
            content_line = str_content.replace(" ", "") # Bo ky tu khoang trang trong chuoi
            content_line = content_line.upper()     # chuyen doi chuoi thanh chu IN HOA
            recognizeStringArr = self.recognize_command_syntax(content_line)   # Kiểm tra các ký tự đúng cú pháp hay không

            if recognizeStringArr == True:
                target_line = content_line
                # tách số của các trục
                result_string = self.separate_string(content_line)
                # tính toán khoảng cách cần tịnh tiến
                result_delta = self.calculate_delta(result_string)
                # tính toán số xung tịnh tiến
                result_xung_nguyen = self.calculate_pulse(result_delta)
                # gửi khoảng cách theo đơn vị xung và tốc độ tới board execute
                self.send_to_execute_board(result_xung_nguyen, self.new_Fspeed)
                # lệnh lưu result_xung_nguyen vào bộ nhớ tạm của board slave
                sent_point = self.save_to_packet_data()

                if sent_point == self.MAX_POINT_IN_BLOCK:  # nếu đã lưu đủ 140 điểm (bên slave có bộ nhớ 150 điểm)
                    sent_packet_done = True

            if content_line == self.end_run_block + '\n' or sent_packet_done == True:    
                main_window.window.showText_signal.emit("- G05.1 End block run mode")
                self.monitor_str_content(target_line.replace("\n",""))  # hiện thị điểm đến cuối cùng trong block data đã chuyển đi   

                if 0 < sent_point <= self.MAX_POINT_IN_BLOCK:  # kiểm tra trường hợp 2
                    # cho chạy auto 
                    main_window.window.showText_signal.emit("- Start block run mode - Point number: " + str(sent_point))
                    self.send_end_run_block_mode()
                    self.monitor_run_block_begin()
                    run_block = self.run_block_done
                break
                # thoát khỏi vòng lặp for 
        return run_block

# chay block point đã gửi tới board slave
    def monitor_run_block_begin(self):
        self.run_block_done = False
        self.pause_on = 0
        comWindow.workSerial.commandChangeStateBlockRun()
        while True:
            point_done = comWindow.workSerial.commandPositionCompleted()

            if point_done[0] == 1: # slave đã chạy xong hết block
                self.run_block_done = True
                break

            if self.pause_on == 1: # dừng motor
                comWindow.workSerial.commandPauseMotor()
                        
            if self.pause_on == 2: # tiếp tục chạy
                comWindow.workSerial.commandResumeMotor()
                self.pause_on = 0
            
            time.sleep(0.1)
# 
    def monitor_run_auto_next(self):
        self.pause_on = 0

        while True:
            point_done = comWindow.workSerial.commandPositionCompleted()

            if point_done[0] == 1: 
                break

            if self.pause_on == 1: # dừng motor
                comWindow.workSerial.commandPauseMotor()

            if self.pause_on == 2: # tiếp tục chạy
                comWindow.workSerial.commandResumeMotor()
                self.pause_on = 0

            time.sleep(0.1)

# gửi mã thoát khỏi chế độ run block point tới board slave
    def send_end_run_block_mode(self):
        send_to_slave_id2 = []
        pulse_end = [0,0,0,0,0,0]
        speed_end = -1
        # lưu giá trị xung để truyền đi
        for i in range(main_window.MAX_AXIS):
            send_to_slave_id2.append(pulse_end[i] >> 16)
            send_to_slave_id2.append(pulse_end[i] & 65535)
        # lưu giá trị tốc độ truyền đi
        send_to_slave_id2.append(speed_end >> 16)
        send_to_slave_id2.append(speed_end & 65535)
        comWindow.workSerial.sendMultipledata(send_to_slave_id2, 0)
        self.save_to_packet_data()

# Dừng chương trình chạy auto
    def disable_run_mode(self):
        if self.run_auto_mode == True:
            self.stop_motor() # dừng motor khẩn cấp
            self.e_stop = True

# tách giá trị tương ứng với từng phần tử trong file 
    def separate_string(self, string):
        Range_char = ['X','Y','Z','A','B','C','S','F','\n']
        # Giá trị tương ứng với các phần tử trong chuỗi string
        value_char = {'X': '0', 'Y': '0', 'Z': '0','A': '0', 'B': '0', 'C': '0', 'S': '0', 'F': '0' }
        try:
            for i in range(len(Range_char)-1):
                index = string.find(Range_char[i])
                next_char = 0
                next_index_array = []
                if index != -1:
                    while next_char < len(Range_char):
                        next_index = string.find(Range_char[next_char])
                        next_index_array.append(next_index)
                        next_char += 1
                    next_index_array.sort()     
                    for j in range(len(next_index_array)):
                        if next_index_array[j] > index:
                           larger_index = next_index_array[j]
                           break
                    value_char[Range_char[i]] = string[index+1: larger_index]
                else: 
                    value_char[Range_char[i]] = self.pre_result_value[i]
            
            result_value = [value_char['X'],value_char['Y'],value_char['Z'],value_char['A'],
                            value_char['B'],value_char['C'],value_char['S'],value_char['F']]

            for i in range(len(self.pre_result_value)):
                self.pre_result_value[i] = result_value[i]  

            self.delayTimer = int(float(result_value[6])*10)     # thời gian delay
            self.new_Fspeed = int(result_value[7])          # tốc độ sơn

        except Exception as e:
            main_window.window.showText_signal.emit('- Separate string error: ' + str(e))
            return
        return result_value

# tính khoảng cách giữa các điểm theo đơn vị xung
    def calculate_delta(self,result_array):
    # result_array là mảng chứa kết quả của hàm separate_string    
    # tính giá trị xung tịnh tiến
        result_value    = []
        delta           = []
        print_delta     = []
        for i in range(len(self.pre_points)):
            delta.append(float(result_array[i])- self.pre_points[i])
            self.pre_points[i] = float(result_array[i])
            result_value.append(float(delta[i])/main_window.gearRatio[i])
            print_delta.append(round(delta[i],3))
        return result_value

# tách xung nguyên và xung lẻ
    def calculate_pulse(self,delta_array):
        print_delta_array   = []       
        xung_le             = []
        xung_nguyen         = []
        so_xung             = []
        for x in range(len(delta_array)):
            print_delta_array.append(round(delta_array[x],3))
            so_xung.append(delta_array[x]+self.sum_xung_le[x])
            xung_nguyen.append(math.trunc(so_xung[x]))
            self.sum_xung_le[x] = so_xung[x] - xung_nguyen[x]
            xung_le.append(round(self.sum_xung_le[x],3))  
        return xung_nguyen

# truyền giá trị xung và tốc độ x,y,z,a,b,c tới board execute; giá trị 32 bit
    def send_to_execute_board(self, pulse, _speed):
        send_to_slave_id2 = [] # gói giá trị 16 bit

        # tính tốc độ của trục x,y,z,a,b,c
        if _speed <= 0:
            # trường hợp không chạy auto mode
            if self.run_auto_mode == False:
                speed_slaves = main_window.callMotorSpeed()
            else: 
                speed_slaves = 10
        else: speed_slaves = _speed
        
        #main_window.window.showText_signal.emit('speed: ' + str(speed_slaves))
        # tách giá trị 32 bit thành packets 16 bit để gửi đến slaves
       
        # lưu giá trị xung để truyền đi
        for i in range(main_window.MAX_AXIS):
            send_to_slave_id2.append(pulse[i] >> 16)
            send_to_slave_id2.append(pulse[i] & 65535)
        # lưu giá trị tốc độ truyền đi
        send_to_slave_id2.append(speed_slaves >> 16)
        send_to_slave_id2.append(speed_slaves & 65535)

        # gửi số xung x,y,z,a,b,c,speed cần chạy tới board slave id 2, gửi 14 word, bắt đầu từ địa chỉ 0
        comWindow.workSerial.sendMultipledata(send_to_slave_id2, 0)
        if self.run_auto_mode == False:
        # phát command tới board slave chạy đến điểm đã gửi
            comWindow.workSerial.commandPointToPoint()

# phát lệnh dừng tay máy
    def pause_motor(self):
        self.pause_on += 1

# gửi index packet data N điểm tới slaves khi khi gặp G05.0
    def save_to_packet_data(self):
        comWindow.workSerial.commandSavePacketsData()
        self.counter += 1
        result_value = self.counter
        return result_value 

# define lại giá trị sau khi đã chạy auto hoàn tất
    def re_init(self):
        self.pre_points = [0,0,0,0,0,0]
        self.pause_on = 0
        self.pre_result_value = [0,0,0,0,0,0,0,0]
        self.run_auto_mode = False
        self.run_block_done = False
        self.counter = 0
        self.e_stop = False
        self.executeDelay = False

# Hiện thị từng dòng đang chạy trong file lên label
    def monitor_str_content(seft, string):
        main_window.uiWorking.label_showline.setText(string)

# Nhận diện dòng thỏa cú pháp trong file
    def recognize_command_syntax(self, StringArr):
        if StringArr == '\0' or StringArr == '\n':
            Recognize_command = False
            return Recognize_command
        Recognize_command = True
        RecognizeChar = ['0','1','2','3','4','5','6','7','8','9', 
                         'X', 'Y', 'Z', 'A', 'B', 'C', 'S', 'F', '.', '-', '\n', '\0']
        for char in StringArr:
            if char in RecognizeChar[0:]: 
                if char == 'S': self.executeDelay = True    #kiểm tra dòng lệnh có S hay không
                pass
            else:
              Recognize_command = False
              self.executeDelay = False
              #main_window.window.showText_signal.emit("Ký tự: " + str(StringArr).replace("\n", ""))
              break
        return Recognize_command

# command bật tắt súng sơn 
    def command_run_spray(self, state):
        try: 
            if state:
                main_window.window.showText_signal.emit("- Spray ON")
                comWindow.workSerial.commandTurnOnSpray()
            else:
                main_window.window.showText_signal.emit("- Spray OFF")
                comWindow.workSerial.commandTurnOffSpray()    
        except Exception as e:
            main_window.window.showText_signal.emit("- Spray Error: " + str(e))
            pass

# Dừng động cơ
    def stop_motor(self):
        comWindow.workSerial.commandStopMotor()

# command xoay bàn sơn
    def command_table_rotate(self):
        try:
            main_window.window.showText_signal.emit("- Rotating table")
            comWindow.workSerial.commandRotateTable()
        except Exception as e:
            main_window.window.showText_signal.emit("- Rotating table error: "+ str(e))
# command kich coil M
    def command_toggle_coilM1(self):
        try:
            main_window.window.showText_signal.emit("- Toggle coil M1")
            comWindow.workSerial.commandToggleCoilM1()
        except Exception as e:
            main_window.window.showText_signal.emit("- Toggle coil M1 error: "+ str(e))
# command kich coil M
    def command_toggle_coilM2(self):
        try:
            main_window.window.showText_signal.emit("- Toggle coil M2")
            comWindow.workSerial.commandToggleCoilM2()
        except Exception as e:
            main_window.window.showText_signal.emit("- Toggle coil M2 error: "+ str(e))
# command kich coil M
    def command_toggle_coilM3(self):
        try:
            main_window.window.showText_signal.emit("- Toggle coil M3")
            comWindow.workSerial.commandToggleCoilM3()
        except Exception as e:
            main_window.window.showText_signal.emit("- Toggle coil M3 error: "+ str(e))
# command kich coil M
    def command_toggle_coilM4(self):
        try:
            main_window.window.showText_signal.emit("- Toggle coil M4")
            comWindow.workSerial.commandToggleCoilM4()
        except Exception as e:
            main_window.window.showText_signal.emit("- Toggle coil M4 error: "+ str(e))
#================================================================================================
class monitorInputOutput:
    def __init__(self):
        self.numCoilXY = 16
        self.valueCoilY = 0
        # khai báo vị trí home sensor và limit sensor trong value
        self.xhomeBit = 0; self.yhomeBit = 0;  self.zhomeBit = 0;  self.ahomeBit = 0; 
        self.xlimitBit = 0;  self.ylimitBit = 0;  self.zlimitBit = 0; self.alimitBit = 0
        # khai báo vị trí bit coilY 
        self.y1Bit = 0; self.y2Bit = 0; self.y3Bit = 0; self.y4Bit = 0
        self.y5Bit = 0; self.y6Bit = 0; self.y7Bit = 0; self.y8Bit = 0 

        self.sensorBitPos = []; self.coilYBitPos = []
        self.sensor_value = []; self.coil_value = []
    
    def returnCoilY1(self):
        checkValue = 0; self.writeCoilY(checkValue)
    def returnCoilY2(self):
        checkValue = 1; self.writeCoilY(checkValue)
    def returnCoilY3(self):
        checkValue = 2; self.writeCoilY(checkValue)
    def returnCoilY4(self):
        checkValue = 3; self.writeCoilY(checkValue)
    def returnCoilY5(self):
        checkValue = 4; self.writeCoilY(checkValue)
    def returnCoilY6(self):
        checkValue = 5; self.writeCoilY(checkValue)
    def returnCoilY7(self):
        checkValue = 6; self.writeCoilY(checkValue)
    def returnCoilY8(self):
        checkValue = 7; self.writeCoilY(checkValue)
    def returnCoilY9(self):
        checkValue = 8; self.writeCoilY(checkValue)
    def returnCoilY10(self):
        checkValue = 9; self.writeCoilY(checkValue)
    def returnCoilY11(self):
        checkValue = 10; self.writeCoilY(checkValue)
    def returnCoilY12(self):
        checkValue = 11; self.writeCoilY(checkValue)
    def returnCoilY13(self):
        checkValue = 12; self.writeCoilY(checkValue)
    def returnCoilY14(self):
        checkValue = 13; self.writeCoilY(checkValue)
    def returnCoilY15(self):
        checkValue = 14; self.writeCoilY(checkValue)
    def returnCoilY16(self):
        checkValue = 15; self.writeCoilY(checkValue)

    def enableCheckButton(self):
        for i in range(self.numCoilXY):
            main_window.checkButtonCoilY[i].setChecked(False)
            
    def disableCheckButton(self):
        for i in range(self.numCoilXY):
            main_window.checkButtonCoilY[i].setChecked(False)

# Lệnh bật output Y và giám sát trạng thái đóng mở của Y      
    def writeCoilY(self, checkValue):
        if main_window.checkButtonCoilY[checkValue].isChecked():
            self.valueCoilY |= (1 << checkValue)
            #main_window.showStatus("Y"+str(checkValue+1) + "ON " + str(self.valueCoilY))
        else:
            self.valueCoilY &= ~(1 << checkValue)
            #main_window.showStatus("Y"+str(checkValue+1) + "OFF " + str(self.valueCoilY))
        try: 
            comWindow.workSerial.sendCoilValue(self.valueCoilY)
         

        except Exception as error:
            main_window.window.showText_signal.emit("===> Toggle coil Y error: " + str(error))
            return

# Cho phép đọc trạng thái coil X từ board slave
    def read_coilXY(self):
        # input bình thường ở mức cao. khi có tín hiệu thì sẽ kéo xuống mức thấp
        try: 
            input_output_packet = comWindow.workSerial.readInputOutputCoil()
        except Exception as error:
            main_window.window.showText_signal.emit("===> Monitor In/Out error: "+ str(error))
            input_output_packet = None

        return input_output_packet
    
    def returnXvalue(self, xyValue):
        input_packet = []
        for i in range(self.numCoilXY):
            input_packet.append((xyValue[0] >> i) & 0x0001)
        return input_packet

    def returnYvalue(self, xyValue):
        output_packet = []
        for i in range(self.numCoilXY):
            output_packet.append((xyValue[1] >> i) & 0x0001) 
        return output_packet

    def monitor_coil_XY(self):
        
        self.updateLabelXYvalue(self.sensor_value, self.coil_value)
        self.showWarning(self.sensor_value)
        self.sensor_machine_axis = [self.sensor_value[self.xhomeBit], self.sensor_value[self.yhomeBit], 
                                    self.sensor_value[self.zhomeBit], self.sensor_value[self.ahomeBit], 0, 0]

        self.sensor_limmit = [self.sensor_value[self.xlimitBit],self.sensor_value[self.xhomeBit],
                                self.sensor_value[self.ylimitBit],self.sensor_value[self.yhomeBit],
                                self.sensor_value[self.zlimitBit],self.sensor_value[self.zhomeBit],
                                self.sensor_value[self.alimitBit],self.sensor_value[self.ahomeBit]]
        self.errorSensorSignal = self.checkErrorSensorSignal()

    def updateLabelXYvalue(self, xValue, yValue):
        for i in range(self.numCoilXY):
            if xValue[i] == 1: main_window.labelCoilX[i].setStyleSheet("background-color: " + main_window.orgColorLabelX[i] + ";")
            else: main_window.labelCoilX[i].setStyleSheet("background-color: #00aa00")    # có tín hiệu input
            
            if yValue[i] == 1: main_window.labelCoilY[i].setStyleSheet("background-color: #00aa00")  # có tín hiệu
            else: main_window.labelCoilY[i].setStyleSheet("background-color: " + main_window.orgColorLabelY[i] + ";")   # không có tín hiệu

    def showWarning(self, value):
        for i in range(len(self.sensorBitPos)):
            if value[self.sensorBitPos[i]]: # Không có tín hiệu
                main_window.warningLabel[i].setStyleSheet("background-color: " + main_window.orgColorWarningLabel[i] + ";")
            else:
                main_window.warningLabel[i].setStyleSheet("background-color: #00aa00;")

    def checkErrorSensorSignal(self): 
        error = False
        if self.sensorBitPos == [] or self.sensor_limmit == [0,0,0,0,0,0,0,0]: error = True
        else:
            for i in range(len(self.sensorBitPos)-1):
                if self.sensorBitPos[i] == self.sensorBitPos[i+1]: error = True; break  # lỗi trùng giá trị bit
        return error
#================================================================================================
if __name__ == "__main__": # define điểm bắt đầu chạy chương trình
    
    #QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)


    app = QApplication(sys.argv)

    main_window = workingWindow()
    comWindow = checkComWindow()
    teachWindow = teachingWindow()
    setMotor = paramWindow()

    teach = workingTeachMode()
    wFile = workingFile()
    run = runMotor()

    main_window.getGearRatioFromJson() #lấy thông số gear từ Json
    main_window.getXYdefinePins()      #lấy thông số pins XY defined từ Json
    main_window.getSpecsOfSensor()     #lưu thông số pins XY vào giá trị cảm biến
    main_window.getSpecsOfCoilY()
    main_window.showWorkingWindow()

    sys.exit(app.exec_()) # creating an event loop for app
