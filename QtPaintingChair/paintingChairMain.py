# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys
import time
import math

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QThread, QRunnable, QThreadPool, pyqtSignal

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
        self.connectSignal = False
     
    def showComWindow(self):
        self.comWindow.show()

    def detroyComWindow(self):
        self.comWindow.close()
    
    def reset_comports(self):
        comports = self.workSerial.detect_comports()
        main_window.showStatus(comports)
        self.uic.comboBox_comPort.clear()
        self.uic.comboBox_baudRate.clear()
        self.uic.comboBox_comPort.addItems(comports)  
        self.uic.comboBox_baudRate.addItems(["115200", "9600"])

    def choose_comports(self):
        com = self.uic.comboBox_comPort.currentText()
        baud = self.uic.comboBox_baudRate.currentText()
        result = self.workSerial.choose_comports(baud,com)
        if result: 
              main_window.showStatus("Kết nối với cổng COM: " + com + "-Baudrate: "+ baud)
              main_window.showCurrentPositions()
              main_window.threadInputOutput.start()
              self.connectSignal = True
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
# Confirm to exit teachingWindow
class MyTeachWindow(QtWidgets.QWidget):
    def closeEvent(self,event):
        result = QtWidgets.QMessageBox.question(self,
                      "Confirm Exit...",
                      "Are you sure you want to exit ?",
                      QtWidgets.QMessageBox.Yes| QtWidgets.QMessageBox.No)
        event.ignore()

        if result == QtWidgets.QMessageBox.Yes:
            teachWindow.exitTeachMode()
            event.accept()
#================================================================================================
class teachingWindow:
    def __init__(self):
        super().__init__() 
        self.teachWin = MyTeachWindow()
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

        self.pre_string_value = [(' X'+'0.0'),(' Y'+'0.0'),(' Z'+'0.0'),(' A'+'0.0'),(' B'+'0.0'),(' C'+'0.0'),
                                 (' S'+'0'),(' F'+'0')]
        self.counter_line = 0

        self.defineTeachModeButton()
   
    def showTeachWindow(self):
        try:
            main_window.showStatus  ("HIEN THI TEACH BOX")
            self.teachWin.show()
        except Exception as e:
            print(str(e))

    def detroyTeachWindow(self):
        self.teachWin.close()

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

        steachModeButton_coilCommand = [self.tableRorateFW, self.tableRorateRW, self.sprayON, self.sprayOFF]
        for i in range(len(self.teachModeButton_coil)): 
            self.teachModeButton_coil[i].clicked.connect(steachModeButton_coilCommand[i])

        self.teachModeButton_control = [self.uiteach.pushButton_exitTeach, self.uiteach.pushButton_savePoint, 
                                        self.uiteach.pushButton_setZero, self.uiteach.pushButton_saveFile]
        teachModeButton_controlCommand = [self.exitTeachMode, self.setPoint, self.setZero, self.saveTofile]
        for i in range(len(self.teachModeButton_control)): 
            self.teachModeButton_control[i].clicked.connect(teachModeButton_controlCommand[i])

        self.teachModeButton_control[0].setDisabled(True)   # disable nut exit tren teaching Window

    def enterTeachMode(self):
        main_window.uiWorking.label_directory.clear()
        main_window.uiWorking.textBrowser_showfile.clear()
        self.reInitTeachMode()
        self.showTeachWindow()
        # đưa vào Qthread để chạy hàm monitorTeachMode
        main_window.threadTeachMode.start()
       
    def reInitTeachMode(self):
        self.button_active = 0
        self.teach_axis = -1   # biến lựa chọn trục cần chạy trong teach mode
        self.monitor_off = False

        self.pre_string_value = [(' X'+'0.0'),(' Y'+'0.0'),(' Z'+'0.0'),(' A'+'0.0'),(' B'+'0.0'),(' C'+'0.0'),
                                 (' S'+'0'),(' F'+'0')]
        self.counter_line = 0

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
        #main_window.threadTeachMode.deleteLater()
        main_window.disable_control_option(False)
        self.monitor_off = True
        main_window.showStatus ("===> Thoát khỏi chế độ Teach Mode")

    def setPoint(self):
        show_line = (' '+ str(self.counter_line))
        different_value = False
        exceed_limit = False

        # lay gia tri
        F_speed =  main_window.speedMotor()
    
        X_value = str(round(main_window.currentPos[0],3)); Y_value = str(round(main_window.currentPos[1],3)); Z_value = str(round(main_window.currentPos[2],3))
        A_value = str(round(main_window.currentPos[3],3)); B_value = str(round(main_window.currentPos[4],3)); C_value = str(round(main_window.currentPos[5],3))
            
        Spray_state = 0 

        if  F_speed < 0: F_speed = 0
        if  F_speed > 200: F_speed = 200

        current_string_value = [(' X'+X_value), (' Y'+Y_value), (' Z'+Z_value), (' A'+ A_value), 
                                (' B'+B_value),(' C'+C_value), (' S'+ str(Spray_state)), (' F'+ str(F_speed))]
        
        # khi nhấn setpoint, phải đảm bảo trục X,Y,Z không đụng vào cảm biến hành trình đầu cuối
        for ii in range(main_window.MAX_AXIS):
            if main_window.coilXY.sensor_limmit[ii] == 0:
                exceed_limit = True
                break
        if exceed_limit == True:
            main_window.showStatus ("Limited: EXCEED SENSOR LIMIT")

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
            #show_line = show_line + '\n'
            self.counter_line += 1
            main_window.uiWorking.textBrowser_showfile.append(show_line) 
            main_window.showStatus("===> Giá trị đã cài đặt: " + show_line)

    def setZero(self):
        main_window.showStatus("===> SET ZERO POSITION")
        comWindow.workSerial.setZeroPositions()

    def saveTofile(self):
        main_window.showStatus ('===> Lưu file.pnt')
        main_window.uiWorking.textBrowser_showfile.append(run.turn_off_spray)
        main_window.uiWorking.textBrowser_showfile.append(run.go_to_1st_point)  # command về vị trí zero
        main_window.uiWorking.textBrowser_showfile.append(run.table_rotary)     # ghi ký tự command xoay bàn sơn
        main_window.uiWorking.textBrowser_showfile.append(run.end_symbol)       # ghi ký tự nhận diện end file
        retrieve_text = main_window.uiWorking.textBrowser_showfile.toPlainText()
        wFile.save_file(retrieve_text)
        main_window.showStatus (wFile.saveFileStatus)

    def tableRorateFW(self):
        main_window.showStatus  ("===> BÀN XOAY 1")
        run.command_table_rotate()

    def tableRorateRW(self):
        main_window.showStatus  ("===> BÀN XOAY 2")
        run.command_table_rotate()

    def sprayON(self):
        main_window.showStatus  ("===> SÚNG SƠN BẬT")
        run.command_run_spray(1)

    def sprayOFF(self):
        main_window.showStatus  ("===> SÚNG SƠN TẮT")
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
                main_window.showCurrentPositions()
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
            print(str(e))
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
# Thread trong monitor teach mode
class monitorTeachModeThread(QThread):
    def __init__(self, parent=None):
        super(monitorTeachModeThread, self).__init__(parent)
    def run(self):
        main_window.showStatus("Start monitor in teachMode")
        teach.monitorTeachMode()
    
#================================================================================================
# Thread monitor input_output signals
class monitorInputOutputThread(QThread):
    change_value = pyqtSignal(int)
    def __init__(self, parent=None):
        super(monitorInputOutputThread, self).__init__(parent)
    def run(self):
        main_window.showStatus("Start monitor input/output")
        main_window.coilXY.monitor_coil_XY()
    #def stop(self):
#================================================================================================
# Confirm exit workingWindow
class MyWindow(QtWidgets.QMainWindow):

    def closeEvent(self,event):
        result = QtWidgets.QMessageBox.question(self,
                      "Confirm Exit...",
                      "Are you sure you want to exit ?",
                      QtWidgets.QMessageBox.Yes| QtWidgets.QMessageBox.No)
        event.ignore()

        if result == QtWidgets.QMessageBox.Yes:
            event.accept()
#================================================================================================
class workingWindow:
    def __init__(self):
        self.window = MyWindow() 
        self.uiWorking = Ui_MainWindow()
        self.uiWorking.setupUi(self.window)
        self.coilXY = monitorInputOutput()
        self.threadTeachMode = monitorTeachModeThread()
        self.threadInputOutput = monitorInputOutputThread()

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

        # Khai báo sử dụng đa luồng được quản lý bới threadpool
        # Tính số luồng tối đa có thể sử dụng maxThreadCount bởi threadpool
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
        

    #def closeEvent(self, event):
    #    print ("close event: ")

    def showWorkingWindow(self):
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

        self.controlButtonName = [ self.uiWorking.pushButton_gotozero, self.uiWorking.pushButton_machinehome, 
                                self.uiWorking.pushButton_auto,  self.uiWorking.pushButton_jog, self.uiWorking.pushButton_pause,
                                self.uiWorking.pushButton_estop]

        self.controlButtonCommand = [ self.gotoZeroPosition, self.gotoMachinePosition, self.runAutoCycle,
                                         self.runJog, self.pauseMotor, self.eStopMotor]
        for i in range(len(self.controlButtonName)):
            self.controlButtonName[i].clicked.connect(self.controlButtonCommand[i])

        self.uiWorking.actionChoose_File_pnt.triggered.connect(self.chooseFile)
        self.uiWorking.actionConnect_to_Slave.triggered.connect(self.chooseComPort)
        self.uiWorking.actionMotor.triggered.connect(self.openSettingMotor)
        self.uiWorking.actionTeach_mode_3.triggered.connect(self.openTeachWindow)

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
                            self.uiWorking.label_zlimit]
        self.orgColorWarningLabel = []
        for i in range(len(self.warningLabel)):
            self.orgColorWarningLabel.append(self.warningLabel[i].palette().window().color().name())

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

    def runAutoCycle(self):
        self.showStatus("Chế độ chạy auto")
        run.activate_run_mode()

    def runJog(self):
        self.showStatus("Chế độ JOG - chạy từng dòng")

    def pauseMotor(self):
        self.showStatus("Tạm dừng motor")
        run.pause_motor()

    def eStopMotor(self):
        self.showStatus("Dừng motor khẩn cấp")
        run.disable_run_mode()

    def getGearRatioCalculated(self, value):
        self.gearRatio.clear()
        for i in range(len(value)):
            self.gearRatio.append(value[i])
        self.showStatus("===> Hệ số xung/mm và xung/deg lưu trong chương trình: ")
        self.showStatus(self.gearRatio)

    def showCurrentPositions(self):
        position = []
        position = self.read_pulse_from_slaves(self.gearRatio)    # trả về 8 phần tử X,Y,Z,A,B,C, pos_Yspray, pos_Zspray
        for i in range(len(position)):
            self.currentPos[i] = position[i]

        for i in range(len(self.lableG54Position)):
            self.lableG54Position[i].setText(str(round(position[i],3)))
            self.lableMachinePosition[i].setText(str(round(position[i],3)))

        return position

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
            
            pulse_to_machine_axis_X = [-36000, 0, 0, 0, 0, 0]
            pulse_to_machine_axis_Y = [0, -70000, 0, 0, 0, 0]
            pulse_to_machine_axis_Z = [0, 0, -36000, 0, 0, 0]
            pulse_to_machine_axis_A = [0, 0, 0, -32000, 0, 0]
            pulse_to_machine_axis_B = [0, 0, 0, 0, 0, 0]
            pulse_to_machine_axis_C = [0, 0, 0, 0, 0, 0]

            pulse_to_machine_axis = [pulse_to_machine_axis_X, pulse_to_machine_axis_Y, pulse_to_machine_axis_Z, 
                                        pulse_to_machine_axis_A, pulse_to_machine_axis_B, pulse_to_machine_axis_C ]
            pulse_to_begin_position = [1600, 3200, 1600, -3200, 0, 0]
            speed_axis = [100,100,100,100,100,100]

            self.disable_control_option(True)
            # set lại các thông số motor, đưa giá trị current_position về 0
            comWindow.workSerial.setZeroPositions()
            time.sleep(0.1)
            for i in range(self.MAX_AXIS):
                run.send_to_execute_board(pulse_to_machine_axis[i],speed_axis[i])
                self.go_machine_axis_state = False
                while True: 
                    # Đọc giá trị thanh ghi lưu giá trị xung đang phát ra
                    positionCompleted = comWindow.workSerial.commandPositionCompleted()
                    self.showCurrentPositions()
                    if (positionCompleted[0]==1 or main_window.coilXY.sensor_machine_axis[i] == 0):
                        # dừng động cơ
                        run.stop_motor()
                        self.go_machine_axis_state = True
                        break  # thoat khỏi vong lặp while

            # sau khi chạy hết các động cơ về vị trí cảm biến
            # tịnh tiến các trục X,Y,Z ra khỏi vị trí cảm biến và set lại 0
            time.sleep(0.5)
            run.send_to_execute_board(pulse_to_begin_position,100)
            while True:
                
                # Đọc trạng thái phát xung đã hoàn tất chưa
                positionCompleted = comWindow.workSerial.commandPositionCompleted()
                # Đọc giá trị thanh ghi lưu giá trị xung đang phát ra
                self.showCurrentPositions()
                if positionCompleted[0] == 1: 
                    # set lại các thông số motor, đưa giá trị current_position về 0
                    comWindow.workSerial.setZeroPositions()
                    comWindow.workSerial.commandCheckXYZAsensor()
                    self.showCurrentPositions()
                    break
       
            self.disable_control_option(False)
            self.go_machine_home = True # đã về home
        
        self.showStatus("===> Tay máy đã về vị trí cảm biến gốc máy")

    def showStatus(self, value):
        self.uiWorking.textBrowser_terminal.append(str(value))
        horScrollBar = self.uiWorking.textBrowser_terminal.horizontalScrollBar()
        verScrollBar = self.uiWorking.textBrowser_terminal.verticalScrollBar()
        scrollIsAtEnd = verScrollBar.maximum() - verScrollBar.value() <= 10
        if scrollIsAtEnd:
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
    
        self.MAX_POINT_IN_BLOCK = 140       # số điểm tối đa có thể truyền tới data_packet slave trong block mode
        self.end_symbol = 'M30\n'           #command kết thúc chương trình
        self.start_run_block = 'G05.0'    #command bắt đầu chạy theo block N điểm
        self.end_run_block = 'G05.1'      #command kết thúc chạy theo block N điểm
        self.go_to_2nd_point = 'G30'      #command quay về điểm gốc thứ 2
        self.go_to_1st_point = 'G28'      #command quay về vị trí gốc 0 (điểm bắt đầu chạy)
        self.turn_on_spray = 'M08'        #command lệnh bật súng sơn
        self.turn_off_spray = 'M09'       #command lệnh tắt súng sơn
        self.table_rotary = 'M10'         #command xoay bàn sơn
        self.run_block_done = False

        self.e_stop = False                 # trạng thái tín hiệu nút nhấn ESTOP

#=============================================================
    def activate_run_mode(self):
        
        for i in main_window.MAX_AXIS:
            if round(main_window.currentPos[i],3) == 0 and main_window.go_machine_home == True:
                pass
            else:
                main_window.showStatus("Run Auto: Go to zero/machine axis first!!!")
                return
        
        try:
            position = wFile.file.seek(0,0) # Di chuyen con tro vi tri read file ve vi tri đầu file
            #main_window.disable_screen_option()
            #main_window.disable_button_control(0)
            self.run_auto_mode = True
            
            for str_content in wFile.file:
                if self.e_stop == True: # nếu có tín hiệu nhấn E-STOP
                    wFile.file.close()
                    break

                main_window.showStatus ('========================================================================')
                content_line = str_content.replace(" ", "") # Bo ky tu khoang trang trong chuoi
                main_window.showStatus (content_line)
                content_line = content_line.upper()         # chuyen doi chuoi thanh chu IN HOA
                self.monitor_str_content(str_content)       # hiện thị từng dòng trong file
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
                        main_window.showStatus("Giá tri timer delay S: "+ str(self.delayTimer))
                        comWindow.workSerial.command_delayTimer(self.delayTimer)
                        while True:
                            excecuteTimerDone = comWindow.workSerial.commandDelayCompleted()
                            time.sleep(0.1)
                            #print("gia tri excecuteTimerDone: ", excecuteTimerDone)
                            if excecuteTimerDone[0] == 1:
                                self.executeDelay = False
                                break
                else:

                    if content_line == self.end_symbol: # gặp ký hiệu báo kết thúc file
                        break

                    if content_line == self.turn_on_spray: # bật súng sơn
                        self.command_run_spray(1)
                        
                    if content_line == self.turn_off_spray: # tắt súng sơn
                        self.command_run_spray(0)
                        
                    if content_line == self.table_rotary: # xoay bàn sơn
                        self.command_table_rotate()

                    if content_line == self.go_to_1st_point: # đi tới điểm gốc đầu tiên, điểm 0
                        main_window.gotoZeroPosition()

                    if content_line == self.go_to_2nd_point: # đi tới điểm gốc thứ 2
                        pass
                    
                    if content_line == self.start_run_block:
                        main_window.showStatus ("=====> G05.0 START BLOCK RUN MODE")
                        result_run_block = self.send_packet_to_slave()  # giá trị trả về luôn trong khoảng [0:140]
                        if result_run_block == False: 
                            main_window.showStatus ("=====> G05.1 Error !!!")
                            break
                        else: 
                            # gửi lần 2 lệnh change_state_run_block để tắt chế độ run block mode
                            main_window.showStatus ("===> BLOCK RUN MODE DONE")
                            self.counter = 0

        except Exception as e:
                main_window.showStatus('activate_run_mode error: '+str(e))
                main_window.showStatus("===> Run Auto", "Error: ")

        finally:
            main_window.showStatus ('========================================================================')
            self.re_init()
            main_window.showStatus("--------------------------------------------------------------------------")
            main_window.showStatus("END")

# gui N packet tới board slave, hàm trả về số điểm đã gửi tới board slave            
    def send_packet_to_slave(self):
        sent_packet_done = False
        sent_point = 0
        target_line = ' '
        run_block = False

        for str_content in wFile.file:
            main_window.showStatus('========================================================================')
            content_line = str_content.replace(" ", "") # Bo ky tu khoang trang trong chuoi
            main_window.showStatus(content_line)
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

            if content_line == self.end_run_block or sent_packet_done == True:    
                main_window.showStatus("=====> G05.1 END BLOCK RUN MODE")
                self.monitor_str_content(target_line)  # hiện thị điểm đến cuối cùng trong block data đã chuyển đi   

                if 0 < sent_point <= self.MAX_POINT_IN_BLOCK:  # kiểm tra trường hợp 2
                    # cho chạy auto 
                    main_window.showStatus("===> START BLOCK RUN MODE - POINT NUMBER: " + str(sent_point))
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
            main_window.showCurrentPositions()

            if point_done[0] == 1: # slave đã chạy xong hết block
                self.run_block_done = True
                break

            if self.pause_on == 1: # dừng motor
                comWindow.workSerial.commandPauseMotor()
                        
            if self.pause_on == 2: # tiếp tục chạy
                comWindow.workSerial.commandResumeMotor()
                self.pause_on = 0
# 
    def monitor_run_auto_next(self):
        self.pause_on = 0

        while True:
            point_done = comWindow.workSerial.commandPositionCompleted()
            main_window.showCurrentPositions()

            if point_done[0] == 1: 
                break

            if self.pause_on == 1: # dừng motor
                comWindow.workSerial.commandPauseMotor()

            if self.pause_on == 2: # tiếp tục chạy
                comWindow.workSerial.commandResumeMotor()
                self.pause_on = 0

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
            main_window.showStatus('separate_string error: ' + str(e))
            return
        return result_value

# tính khoảng cách giữa các điểm theo đơn vị xung
    def calculate_delta(self,result_array):
    # result_array là mảng chứa kết quả của hàm separate_string    
    # tính giá trị xung tịnh tiến
        main_window.showStatus('Giá trị X,Y,Z,A,B,C,S,F là:' + str(result_array))
        main_window.showStatus('Giá trị pre_points: ' + str(self.pre_points))
        result_value    = []
        delta           = []
        print_delta     = []
        for i in range(len(self.pre_points)):
            delta.append(float(result_array[i])- self.pre_points[i])
            self.pre_points[i] = float(result_array[i])
            result_value.append(float(delta[i])/main_window.gearRatio[i])
            print_delta.append(round(delta[i],3))

        main_window.showStatus('Gia tri delta cua X,Y,Z,A,B,C là:'+ str(print_delta))
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
        main_window.showStatus ("------------------------------------")
        main_window.showStatus ('>>> Gia tri xung x,y,z,a,b,c chua calib lan luot la: ' + str(print_delta_array))
        main_window.showStatus ('>>> So xung nguyen truc x,y,z,a,b,c: ' + str(xung_nguyen))
        main_window.showStatus ('>>> So xung le truc x,y,z,a,b,c:     '+ str(xung_le))
        main_window.showStatus ("------------------------------------")
        return xung_nguyen

# truyền giá trị xung và tốc độ x,y,z,a,b,c tới board execute; giá trị 32 bit
    def send_to_execute_board(self, pulse, _speed):
        send_to_slave_id2 = [] # gói giá trị 16 bit

        # tính tốc độ của trục x,y,z,a,b,c
        if _speed <= 30:
            speed_slaves = main_window.callMotorSpeed()
        else: speed_slaves = _speed

        main_window.showStatus ("===> Tốc độ tay máy: " + str(speed_slaves) +"%")
        main_window.showStatus ("===> Giá trị xung cấp vào driver: " + str(pulse)) 
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
        main_window.showStatus("===> Tạm dừng động cơ")

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
        #main_window.enable_button_control(0)
        #main_window.enable_screen_option()

# Hiện thị từng dòng đang chạy trong file lên label
    def monitor_str_content(seft, string):
        main_window.uiWorking.label_showline.setText(string)

# Nhận diện dòng thỏa cú pháp trong file
    def recognize_command_syntax(self, StringArr):
        if StringArr == '\0' or StringArr == '\n':
            main_window.showStatus("Ky tu khong dung systax: " + str(StringArr))
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
              main_window.showStatus ("Ky tu khong dung systax: " + str(StringArr))
              break
        return Recognize_command

# command bật tắt súng sơn 
    def command_run_spray(self, state):
        if state:
            main_window.showStatus("===> SÚNG SƠN BẬT")
            comWindow.workSerial.commandTurnOnSpray()
        else:
            main_window.showStatus("===> SÚNG SƠN TẮT")
            comWindow.workSerial.commandTurnOffSpray()    

# Dừng động cơ
    def stop_motor(self):
        main_window.showStatus("===> STOP MOTOR")
        comWindow.workSerial.commandStopMotor()

# command xoay bàn sơn
    def command_table_rotate(self):
        main_window.showStatus("===> Xoay bàn sơn")
        comWindow.workSerial.commandRotateTable()
#================================================================================================
class monitorInputOutput:
    def __init__(self):
        self.numCoilXY = 16
        self.valueCoilY = 0
        # khai báo vị trí home sensor và limit sensor trong value
        self.xhomeBit = 1; self.yhomeBit = 3;  self.zhomeBit = 5;  self.ahomeBit = 6; 
        self.xlimitBit = 0;  self.ylimitBit = 2;  self.zlimitBit = 4; 

        self.bitPos = [self.xhomeBit, self.yhomeBit, self.zhomeBit, self.ahomeBit, 
                                    self.xlimitBit, self.ylimitBit, self.zlimitBit]
    
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
            main_window.showStatus("Y"+str(checkValue+1) + "ON " + str(self.valueCoilY))
            #main_window.labelCoilY[checkValue].setStyleSheet("background-color: #00aa00;")
        else:
            self.valueCoilY &= ~(1 << checkValue)
            main_window.showStatus("Y"+str(checkValue+1) + "OFF " + str(self.valueCoilY))
            #main_window.labelCoilY[checkValue].setStyleSheet("background-color: " + main_window.orgColorLabelY[checkValue] + ";")
        try: 
            comWindow.workSerial.sendCoilValue(self.valueCoilY)
        except Exception as error:
            main_window.showStatus("===> Kích coil Y bị lỗi đường truyền tín hiệu")
            return

# Cho phép đọc trạng thái coil X từ board slave
    def read_coilXY(self):
        # input bình thường ở mức cao. khi có tín hiệu thì sẽ kéo xuống mức thấp
        input_output_packet = comWindow.workSerial.readInputOutputCoil()
        """""
        input_packet = []
        output_packet = []
        for i in range(self.numCoilXY):
            input_packet.append((input_output_packet[0] >> i) & 0x0001)
            if input_packet[i] == 1: main_window.labelCoilX[i].setStyleSheet("background-color: " + main_window.orgColorLabelX[i] + ";")
            else: main_window.labelCoilX[i].setStyleSheet("background-color: #00aa00")    # có tín hiệu input
        
        for i in range(self.numCoilXY):
            output_packet.append((input_output_packet[1] >> i) & 0x0001)   
            if output_packet[i] == 1: main_window.labelCoilY[i].setStyleSheet("background-color: #00aa00")  # có tín hiệu
            else: main_window.labelCoilY[i].setStyleSheet("background-color: " + main_window.orgColorLabelY[i] + ";")   # không có tín hiệu
        
        return input_packet  # tra ve gia tri input
        """
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

    def updateLabelXYvalue(self, xValue, yValue):
        for i in range(self.numCoilXY):
            if xValue[i] == 1: main_window.labelCoilX[i].setStyleSheet("background-color: " + main_window.orgColorLabelX[i] + ";")
            else: main_window.labelCoilX[i].setStyleSheet("background-color: #00aa00")    # có tín hiệu input
            if yValue[i] == 1: main_window.labelCoilY[i].setStyleSheet("background-color: #00aa00")  # có tín hiệu
            else: main_window.labelCoilY[i].setStyleSheet("background-color: " + main_window.orgColorLabelY[i] + ";")   # không có tín hiệu
        
    def monitor_coil_XY(self):
        try:
            while True:
                val = self.read_coilXY()
                self.sensor_value = self.returnXvalue(val)
                self.coil_value = self.returnYvalue(val)
                #self.updateLabelXYvalue(self.sensor_value, self.coil_value)
                #self.showWarning(self.sensor_value)
                #main_window.showStatus(str(self.sensor_value))
                self.sensor_machine_axis = [self.sensor_value[self.xhomeBit], self.sensor_value[self.yhomeBit], 
                                            self.sensor_value[self.zhomeBit], self.sensor_value[self.ahomeBit], 0, 0]

                self.sensor_limmit = [self.sensor_value[self.xlimitBit],self.sensor_value[self.xhomeBit],
                                        self.sensor_value[self.ylimitBit],self.sensor_value[self.yhomeBit],
                                        self.sensor_value[self.zlimitBit],self.sensor_value[self.zhomeBit]]

                time.sleep(0.1) # 100 ms đọc data coilXY 1 lần

        except Exception as error:
            main_window.showStatus("===> Lỗi trong quá trình giám sát cổng input/output")
            main_window.showStatus("===> Nhấn nút ResetCOIL để khởi động lại quá trình giám sát")
            return

    def showWarning(self, value):
        for i in range(len(self.bitPos)):
            if value[self.bitPos[i]]: # Không có tín hiệu
                main_window.warningLabel[i].setStyleSheet("background-color: " + main_window.orgColorWarningLabel[i] + ";")
            else:
                main_window.warningLabel[i].setStyleSheet("background-color: #00aa00;")

#================================================================================================
if __name__ == "__main__": # define điểm bắt đầu chạy chương trình
    app = QApplication(sys.argv)

    main_window = workingWindow()
    comWindow = checkComWindow()
    teachWindow = teachingWindow()
    setMotor = paramWindow()

    teach = workingTeachMode()
    wFile = workingFile()
    run = runMotor()

    main_window.showWorkingWindow()

    sys.exit(app.exec_()) # creating an event loop for app
