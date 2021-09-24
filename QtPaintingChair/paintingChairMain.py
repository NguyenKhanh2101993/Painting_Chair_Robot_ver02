# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys
import time
import math
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QWidget
from comWindow import Ui_communication
from workWindow import Ui_MainWindow
from teachWindow import Ui_teachMode
from settingWindow import Ui_motorSettings

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
     
    def showComWindow(self):
        self.comWindow.show()

    def detroyComWindow(self):
        self.comWindow.close()
    
    def reset_comports(self):
        comports = self.workSerial.detect_comports()
        main_window.showStatus(comports)
        self.uic.comboBox_comPort.clear()
        self.uic.comboBox_comPort.addItems(comports)  

    def choose_comports(self):
        com = self.uic.comboBox_comPort.currentText()
        result = self.workSerial.choose_comports(115200,com)
        if result: 
              main_window.showStatus("Kết nối với cổng COM: " + com)
        else: 
              main_window.showStatus("Không nhận được cổng COM (Mất kết nối hoặc bị chặn)")
#================================================================================================
# ====> test ok
class paramWindow:
    def __init__(self):
       
        self.settingWin = QWidget()
        self.uiSetting = Ui_motorSettings()
        self.uiSetting.setupUi(self.settingWin)

        self.uiSetting.buttonBox.rejected.connect(self.closeParamWindow)
        self.uiSetting.buttonBox.accepted.connect(self.save_settings)

        self.jsonFile = makeJsonSetting()
        self.getGearRatioFromJson()

    def closeParamWindow(self):
        self.settingWin.close()

    def showParamWindow(self):
        self.settingWin.show()
        self.getParameter()

    # truy xuat giá trị cài đặt motor từ file json
    def getParameter(self):
        gearbox_value = []; microStep_value = []; diameter_value = []
        try:
            motorSetting = self.jsonFile.getMotorInfo() 

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
            main_window.showStatus(error)
            main_window.showStatus("===> ConfigFile Motor Error")
            return

    # lưu giá trị cài đặt từ bảng vào file json        
    def save_settings(self):
        gear = []; microstep = []; diameter = []
        for i in range(main_window.MAX_AXIS):
            gear.append(self.uiSetting.tableWidget.item(0, i).text())
            microstep.append(self.uiSetting.tableWidget.item(1, i).text())
            diameter.append(self.uiSetting.tableWidget.item(2, i).text())

        main_window.showStatus("=======================================================")
        main_window.showStatus("Tỉ số truyền hộp số, vi bước và đường kính bánh răng: ") 
        main_window.showStatus(gear)
        main_window.showStatus(microstep)
        main_window.showStatus(diameter)
        main_window.showStatus("=======================================================")

        self.jsonFile.setMotorInfor(gear, microstep, diameter)   # lưu các thông số cài đặt motor
        result = self.calculate_gearRatio(gear, microstep, diameter)
        if result != []:
            self.jsonFile.setGearInfor(result)                       #lưu giá trị gearratio đã tính toán được
            self.saveGearRatio(result)

    def calculate_gearRatio(self, gear, microstep, diameter):
        result = []
        try:
            #((80*math.pi)/(1600*5))
            gear_ratio_X = (float(diameter[0])*math.pi)/(int(microstep[0])*float(gear[0]))
            #((80*math.pi)/(25600))
            gear_ratio_Y = (float(diameter[1])*math.pi)/(int(microstep[1])*float(gear[1]))
            #((80*math.pi)/(3200*5))
            gear_ratio_Z = (float(diameter[2])*math.pi)/(int(microstep[2])*float(gear[2]))
            #(360/(12800*5))
            gear_ratio_A = float(diameter[3])/(int(microstep[3])*float(gear[3]))
            #(360/12800)
            gear_ratio_B = float(diameter[4])/(int(microstep[4])*float(gear[4]))
            #(360/12800)
            gear_ratio_C = float(diameter[5])/(int(microstep[5])*float(gear[5]))

            result = [gear_ratio_X, gear_ratio_Y, gear_ratio_Z,gear_ratio_A, gear_ratio_B, gear_ratio_C]

        except Exception as e:
            main_window.showStatus("Nhập giá trị bị sai, giá trị không phải là số ")

        return result

    def saveGearRatio(self, result):
        main_window.getGearRatioCalculated(result)

    def getGearRatioFromJson(self):
        result = self.jsonFile.getGearRatio()
        if result != []:
            self.saveGearRatio(result)

#================================================================================================
class teachingWindow:
    def __init__(self):
        self.teachWin = QWidget()
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
        self.monitor_off = False

        self.defineTeachModeButton()

    def showTeachWindow(self):
        self.teachWin.show()

    def detroyTeachWindow(self):
        self.teachWin.close()

    def defineTeachModeButton(self):

        teach_command_deactive = [self.deactive, self.deactive, self.deactive, self.deactive, 
                                   self.deactive, self.deactive, self.deactive]

        self.teachModeButton_Fw = [ self.uiteach.pushButton_xFw, self.uiteach.pushButton_yFw, self.uiteach.pushButton_zFw,
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

        steachModeButton_coilCommand = [None, None, None, None]
        for i in range(len(self.teachModeButton_coil)): 
            self.teachModeButton_coil[i].clicked.connect(teach_command_deactive[i])

        self.teachModeButton_control = [self.uiteach.pushButton_exitTeach, self.uiteach.pushButton_savePoint, 
                                        self.uiteach.pushButton_setZero, self.uiteach.pushButton_saveFile]
        teachModeButton_controlCommand = [self.exitTeachMode, self.setPoint, self.setZero, self.saveTofile]
        for i in range(len(self.teachModeButton_control)): 
            self.teachModeButton_control[i].clicked.connect(teachModeButton_controlCommand[i])

    def enterTeachMode(self):
        self.initTeachMode()
        teach.monitorTeachMode()
    
    def initTeachMode(self):
        main_window.uiWorking.label_directory.clear()
        main_window.uiWorking.textBrowser_showfile.clear()
        self.showTeachWindow()

    def activateTeachMode(self,state):
        if state == True:
            main_window.showStatus("===> Enable teachMode button")
        else: 
            main_window.showStatus("===> Disable teachMode button")

        for i in range(len(self.teachModeButton_Fw)):
            self.teachModeButton_Fw[i].setEnabled(state)
        for i in range(len(self.teachModeButton_Rw)):
            self.teachModeButton_Rw[i].setEnabled(state)
        for i in range(len(self.teachModeButton_coil)):
            self.teachModeButton_coil[i].setEnabled(state)
        for i in range(len(self.teachModeButton_control)):
            self.teachModeButton_control[i].setEnabled(state)

    def buttonX_forward(self):
        main_window.showStatus ("Dang nhan button X-")
        self.teach_axis = self.TEACH_X_AXIS
        self.button_active = self.forward

    def buttonX_reverse(self):
        main_window.showStatus  ("Dang nhan button X+")
        self.teach_axis = self.TEACH_X_AXIS
        self.button_active = self.reverse

    def buttonY_forward(self):
        main_window.showStatus  ("Dang nhan button Y-")
        self.teach_axis = self.TEACH_Y_AXIS
        self.button_active = self.forward

    def buttonY_reverse(self):
        main_window.showStatus  ("Dang nhan button Y+")
        self.teach_axis = self.TEACH_Y_AXIS
        self.button_active = self.reverse

    def buttonZ_forward(self):
        main_window.showStatus  ("Dang nhan button Z-")
        self.teach_axis = self.TEACH_Z_AXIS
        self.button_active = self.forward

    def buttonZ_reverse(self):
        main_window.showStatus  ("Dang nhan button Z+")
        self.teach_axis = self.TEACH_Z_AXIS
        self.button_active = self.reverse

    def buttonB_forward(self):
        main_window.showStatus  ("Dang nhan button B-")
        self.teach_axis = self.TEACH_B_AXIS
        self.button_active = self.forward

    def buttonB_reverse(self):
        main_window.showStatus  ("Dang nhan button B+")
        self.teach_axis = self.TEACH_B_AXIS
        self.button_active = self.reverse

    def buttonC_forward(self):
        main_window.showStatus  ("Dang nhan button C-")
        self.teach_axis = self.TEACH_C_AXIS
        self.button_active = self.forward

    def buttonC_reverse(self):
        main_window.showStatus  ("Dang nhan button C+")
        self.teach_axis = self.TEACH_C_AXIS
        self.button_active = self.reverse

    def buttonA_forward(self):
        main_window.showStatus  ("Dang nhan button A-")
        self.teach_axis = self.TEACH_A_AXIS
        self.button_active = self.forward

    def buttonA_reverse(self):
        main_window.showStatus  ("Dang nhan button A+")
        self.teach_axis = self.TEACH_A_AXIS
        self.button_active = self.reverse    

    def buttonZ1_forward(self):
        main_window.showStatus  ("Dang nhan button Z1-")
        self.teach_axis = self.TEACH_Z1_AXIS
        self.button_active = self.forward

    def buttonZ1_reverse(self):
        main_window.showStatus  ("Dang nhan button Z1+")
        self.teach_axis = self.TEACH_Z1_AXIS
        self.button_active = self.reverse

    def deactive(self):
        main_window.showStatus  ("Thả nút nhấn")
        self.button_active = 0

    def exitTeachMode(self):
        self.detroyTeachWindow()
        main_window.disable_control_option(False)
        self.monitor_off = True

    def setPoint(self):
        pass

    def setZero(self):
        pass

    def saveTofile(self):
        pass
#================================================================================================
class workingTeachMode():
    def __init__(self):

        self.pos_Yspray = 6
        self.pos_Zspray = 7
        self.pre_button_state = 0 
        self.no_choise_axis = -1
        self.xAXIS = 0; self.yAXIS = 1; self.zAXIS = 2; self.aAXIS = 3; self.bAXIS = 4; self.cAXIS = 5; self.z1AXIS = 6
   
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
            while True:
                self.pulse_teach_packet = [0,0,0,0,0,0]
                state_runing = False
                self.chooseAxis = self.read_teach_axis()
                self.button_state = self.read_state_button()
                main_window.showCurrentPositions()
                self.Kinematics_Zaxis_mode_02()
                
                # gửi command quay chiều thuận trục được chọn
                if self.chooseAxis == self.xAXIS:
                    if (self.button_state > self.pre_button_state):  new_pos_X = -1000
                    if (self.button_state < self.pre_button_state):  new_pos_X = 1000
                    pulse_teach = int((new_pos_X - main_window.currentPos[self.xAXIS])/main_window.gearRatio[self.xAXIS])
                    if  main_window.currentPos[self.xAXIS] < -1000 or  main_window.currentPos[self.xAXIS] > 1000: 
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
                    if (self.button_state > self.pre_button_state):  new_pos_A = -180
                    if (self.button_state < self.pre_button_state):  new_pos_A = 180
                    pulse_teach = int((new_pos_A -  main_window.currentPos[self.aAXIS])/main_window.gearRatio[self.aAXIS])
                    if main_window.currentPos[self.aAXIS] < -180 or main_window.currentPos[self.aAXIS] > 180: 
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
                    main_window.showCurrentPositions()
                    self.button_state = self.read_state_button()
                    if self.button_state == self.pre_button_state:
                        run.stop_motor()
                        state_runing = False
                        break  # thoat khỏi vong lặp while
                
                if (teachWindow.monitor_off == True):
                    teachWindow.monitor_off = False
                    self.chooseAxis = self.no_choise_axis
                    main_window.showStatus  ("===> Thoát khỏi chế độ teach mode")
                    break

        except Exception as e:
            main_window.showStatus("===> Exit chế độ monitor teach mode")
            main_window.showStatus (str(e))
            return

    def Kinematics_Zaxis_mode_02(self):
            if self.chooseAxis == self.z1AXIS:
                Yspray_expect = main_window.currentPos[self.pos_Yspray]
                while True:
                    running = False
                    self.button_state = self.read_state_button()
                    main_window.showCurrentPositions()
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
                        main_window.showCurrentPositions()
                        if self.button_state == self.pre_button_state:
                            run.stop_motor()
                            running = False
                            break  # thoat khỏi vong lặp while
                    
                    # nếu disable teach mode thì thoát khỏi 
                    if (teachWindow.monitor_off == True) or (self.chooseAxis != self.zAXIS):
                        break
            else: pass
#================================================================================================
class workingWindow():
    def __init__(self):

        self.window = QMainWindow()
        self.uiWorking = Ui_MainWindow()
        self.uiWorking.setupUi(self.window)

        self.defineControlButton()
        
        self.currentPos = []
        self.gearRatio = []
        self.MAX_AXIS = 6
        self.spray_axis = 550
        self.go_machine_home = False

    def showWorkingWindow(self):
        self.window.show()

    def defineControlButton(self):

        self.lableG54Position = [self.uiWorking.label_Xposition, self.uiWorking.label_Yposition, self.uiWorking.label_Zposition, 
                                    self.uiWorking.label_Aposition, self.uiWorking.label_Bposition, self.uiWorking.label_Cposition]

        self.lableMachinePosition = [self.uiWorking.label_Xhome, self.uiWorking.label_Yhome, self.uiWorking.label_Zhome, self.uiWorking.label_Ahome,
                                        self.uiWorking.label_Bhome,self.uiWorking.label_Chome]

        self.controlButtonName = [ self.uiWorking.pushButton_gotozero, self.uiWorking.pushButton_machinehome]
        self.controlButtonCommand = [ self.gotoZeroPosition, self.gotoMachinePosition]
        for i in range(len(self.controlButtonName)):
            self.controlButtonName[i].clicked.connect(self.controlButtonCommand[i])

        self.uiWorking.actionChoose_File_pnt.triggered.connect(self.chooseFile)
        self.uiWorking.actionConnect_to_Slave.triggered.connect(self.chooseComPort)
        self.uiWorking.actionMotor.triggered.connect(self.openSettingMotor)
        self.uiWorking.actionTeach_mode_3.triggered.connect(self.openTeachWindow)


    def disable_control_option(self, state):
        for i in range(len(self.controlButtonName)):
            self.controlButtonName[i].setDisabled(state)

    def chooseFile(self):
        self.showStatus("Chế độ chọn file.pnt")
        try:
            pathFile = wFile.show_initial_directory()
            self.showStatus("pathFile: "+ pathFile)
            self.uiWorking.label_directory.setText(pathFile)
            content = wFile.get_file(pathFile)
            self.uiWorking.textBrowser_showfile.setText(content)

        except Exception as error: 
            self.uiWorking.label_directory.setText("NO FILE LOADED")
            self.showStatus(error)
            return

    def chooseComPort(self):
        self.showStatus("Chế độ chọn cổng COM giao tiếp")
        comWindow.showComWindow()

    def openSettingMotor(self):
        self.showStatus("Chế độ cài đặt thông số motor")
        setMotor.showParamWindow()

    def openTeachWindow(self):
        self.showStatus("Chế độ dạy chương trình")
        self.disable_control_option(True)
        teachWindow.enterTeachMode()

    def enterManual(self):
        self.showStatus("Chế độ manual bật tắt coilY")

    def getGearRatioCalculated(self, value):
        self.gearRatio.clear()
        for i in range(len(value)):
            self.gearRatio.append(value[i])
        self.showStatus("===> Hệ số xung/mm và xung/deg lưu trong chương trình: ")
        self.showStatus(self.gearRatio)

    def showCurrentPositions(self):
        position = []; self.currentPos.clear()
        position = self.read_pulse_from_slaves(self.gearRatio)    # trả về 8 phần tử X,Y,Z,A,B,C, pos_Yspray, pos_Zspray
        for i in range(len(self.lableG54Position)):
            self.lableG54Position[i].setText(str(round(position[i],3)))
            self.lableMachinePosition[i].setText(str(round(position[i],3)))

        for i in range(len(position)):
            self.currentPos.append(position[i])

    def callMotorSpeed(self):
        return 0

    def read_pulse_from_slaves(self, gearRatio):
        current_position_motor = []
        current_pulse = []
        resultCurrentPos = []
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
            self.showStatus("===> read_pulse_from_slaves function failed")
            self.showStatus(error)
            return

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

    def gotoZeroPosition(self):
        self.showStatus("Đưa tay máy về vị trí 0")
        comWindow.workSerial.commandGotoZero()
        while True:
            positionCompleted = comWindow.workSerial.commandPositionCompleted()
            self.showCurrentPositions()
            if positionCompleted[0] == 1: 
                break
        self.showStatus("Tay máy đã về vị trí 0")

    def gotoMachinePosition(self):
        if self.go_machine_home == False:
            self.showStatus("Đưa tay máy về vị trí cảm biến gốc máy")
            comWindow.workSerial.commandCheckXYZAsensor()
            
            pulse_to_machine_axis_X = [-25600, 0, 0, 0, 0, 0]
            pulse_to_machine_axis_Y = [0, -25600, 0, 0, 0, 0]
            pulse_to_machine_axis_Z = [0, 0, -25600, 0, 0, 0]
            pulse_to_machine_axis_A = [0, 0, 0, -16000, 0, 0]
            pulse_to_machine_axis_B = [0, 0, 0, 0, -6400, 0]
            pulse_to_machine_axis_C = [0, 0, 0, 0, 0, -12800]

            pulse_to_machine_axis = [pulse_to_machine_axis_X, pulse_to_machine_axis_Y, pulse_to_machine_axis_Z, 
                                        pulse_to_machine_axis_A, pulse_to_machine_axis_B, pulse_to_machine_axis_C ]
            pulse_to_begin_position = [1600, 6400, 3200, 0, 0, 0]
            speed_axis = [100,100,100,100,100,200]

            self.disable_control_option(True)
            # khai báo mảng chứa giá trị cảm biến gốc máy
            self.sensor_machine_axis = [] #[Monitor_in_out.sensor_value[0], Monitor_in_out.sensor_value[2], Monitor_in_out.sensor_value[4],
                                        #Monitor_in_out.sensor_value[6], Monitor_in_out.sensor_value[8], Monitor_in_out.sensor_value[10]]
            # set lại các thông số motor, đưa giá trị current_position về 0
            comWindow.workSerial.setZeroPositions()
            time.sleep(0.5)
            for i in range(self.MAX_AXIS):
                run.send_to_execute_board(pulse_to_machine_axis[i],speed_axis[i])
                self.go_machine_axis_state = False
                while True: 
                    # Đọc giá trị thanh ghi lưu giá trị xung đang phát ra
                    positionCompleted = comWindow.workSerial.commandPositionCompleted()
                    self.showCurrentPositions()
                    if (positionCompleted[0]==1 or self.sensor_machine_axis[i] == 0):
                        # dừng động cơ
                        run.stop_motor()
                        self.go_machine_axis_state = True
                        break  # thoat khỏi vong lặp while

            # sau khi chạy hết các động cơ về vị trí cảm biến
            # tịnh tiến các trục X,Y,Z ra khỏi vị trí cảm biến và set lại 0
            time.sleep(0.5)
            run.send_to_execute_board(pulse_to_begin_position,120)
            while True:
                
                # Đọc trạng thái phát xung đã hoàn tất chưa
                positionCompleted = comWindow.workSerial.commandPositionCompleted()
                # Đọc giá trị thanh ghi lưu giá trị xung đang phát ra
                self.showCurrentPositions()
                if positionCompleted[0] == 1: 
                    # set lại các thông số motor, đưa giá trị current_position về 0
                    comWindow.workSerial.setZeroPositions()
                    comWindow.workSerial.commandCheckXYZAsensor()
                    break
       
            self.disable_control_option(False)
            self.go_machine_home = True # đã về home
        
        self.showStatus("===> Tay máy đã về vị trí cảm biến gốc máy")

    def showStatus(self, value):
        self.uiWorking.textBrowser_terminal.append(str(value))
#================================================================================================
class runMotor:
    def __init__(self):
        self.run_auto_mode = False

# truyền giá trị xung và tốc độ x,y,z,a,b,c tới board execute; giá trị 32 bit
    def send_to_execute_board(self, pulse, _speed):
        send_to_slave_id2 = [] # gói giá trị 16 bit

        # tính tốc độ của trục x,y,z,a,b,c
        if _speed <= 30:
            speed_slaves = main_window.callMotorSpeed()
        else: speed_slaves = _speed

        main_window.showStatus ("Tốc độ tay máy: ",int(speed_slaves),"%")
        main_window.showStatus ("Giá trị xung cấp vào driver: ",pulse) 
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

    def stop_motor(self):
        main_window.showStatus("STOP MOTOR")
        comWindow.workSerial.commandStopMotor()
#================================================================================================
if __name__ == "__main__": # define điểm bắt đầu chạy chương trình
    app = QApplication([])

    main_window = workingWindow()
    comWindow = checkComWindow()
    teachWindow = teachingWindow()
    setMotor = paramWindow()

    
    teach = workingTeachMode()
    wFile = workingFile()
    run = runMotor()

    main_window.showWorkingWindow()
    sys.exit(app.exec_())
