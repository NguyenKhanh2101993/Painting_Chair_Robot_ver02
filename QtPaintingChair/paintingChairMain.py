# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QWidget
from comWindow import Ui_ComportWindow
from workWindow import Ui_MainWindow
from initSerial import Read_Write_to_Serial 
from workFile import workingFile 
from monitorPosition import monitor 


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

class checkComWindow():
    def __init__(self):
        
        self.startWindow = QWidget()
        self.uic = Ui_ComportWindow()
        self.uic.setupUi(self.startWindow)
        
        self.reset_comports()
        self.uic.pushButton.clicked.connect(self.choose_comports)
        self.uic.pushButton_2.clicked.connect(self.reset_comports)

        self.mainWindow = 0

        self.showStartWindow() 

    def showStartWindow(self):
        self.startWindow.showNormal()

    def detroyStartWindow(self):
        self.startWindow.destroy()
    
    def reset_comports(self):
        comports = workSerial.detect_comports()
        print(comports)
        self.uic.comboBox.clear()
        self.uic.comboBox.addItems(comports)  

    def choose_comports(self):
        com = self.uic.comboBox.currentText()
        print(com)
        self.mainWindow = workSerial.choose_comports(115200,com)
        if self.mainWindow: 
            #main_window.showWorkingWindow()
            self.detroyStartWindow()
            pass
#================================================================================================
class workingWindow():
    def __init__(self):
        uiWorking.setupUi(window)
        self.lableG54Position = [uiWorking.label_Xposition, uiWorking.label_Yposition, uiWorking.label_Zposition, 
                                    uiWorking.label_Aposition, uiWorking.label_Bposition, uiWorking.label_Cposition]

        self.lableMachinePosition = [uiWorking.label_Xhome, uiWorking.label_Yhome, uiWorking.label_Zhome, uiWorking.label_Ahome,
                                        uiWorking.label_Bhome,uiWorking.label_Chome,]


    def showWorkingWindow(self):
        window.show()

    def test(self):
        self.showStatus("===> OKOK")

    def showCurrentPositions(self):
        position = []
        position = monitorPos.read_pulse_from_slaves()    # trả về 8 phần tử X,Y,Z,A,B,C, pos_Yspray, pos_Zspray
        for i in range(len(self.lableG54Position)):
            self.lableG54Position[i].setText(str(round(position[i],3)))
            self.lableMachinePosition[i].setText(str(round(position[i],3)))
        self.pos_Yspray =  position[6]
        self.pos_Zspray =  position[7]  

    def showStatus(self, value):
        uiWorking.textBrowser_terminal.append(str(value))
#================================================================================================
class teach_mode(workingWindow):
    def __init__(self):
        
        self.defineTeachModeButton()
        self.activateTeachMode(False)

    def defineTeachModeButton(self):
        self.teachModeButton_Fw = [ uiWorking.pushButton_xFw, uiWorking.pushButton_yFw, uiWorking.pushButton_zFw,
                                    uiWorking.pushButton_aFw, uiWorking.pushButton_bFw, uiWorking.pushButton_cFw,
                                    uiWorking.pushButton_z1Up] 

        self.teachModeButtonFwCommand = [self.test, self.test, self.test, self.test, self.test, self.test, self.test]

        for i in range(len(self.teachModeButton_Fw)): 
            self.teachModeButton_Fw[i].pressed.connect(self.teachModeButtonFwCommand[i])

        self.teachModeButton_Rw = [ uiWorking.pushButton_xRw, uiWorking.pushButton_yRw, uiWorking.pushButton_zRw,
                                    uiWorking.pushButton_aRw, uiWorking.pushButton_bRw, uiWorking.pushButton_cRw,
                                    uiWorking.pushButton_z1down]
        
        for i in range(len(self.teachModeButton_Rw)): 
            self.teachModeButton_Rw[i].pressed.connect(self.teachModeButtonFwCommand[i])

        self.teachModeButton_coil = [uiWorking.pushButton_tableFw, uiWorking.pushButton_tableRw,
                                     uiWorking.pushButton_sprayOn, uiWorking.pushButton_sprayOff]

        self.teachModeButton_coilCommand = []
        for i in range(len(self.teachModeButton_coil)): 
            self.teachModeButton_coil[i].clicked.connect(self.teachModeButtonFwCommand[i])

        self.teachModeButton_control = [uiWorking.pushButton_exitTeach, uiWorking.pushButton_savePoint, uiWorking.pushButton_setZero]
        self.teachModeButton_controlCommand = [self.exitTeachMode, self.setPoint, self.setZero]
        for i in range(len(self.teachModeButton_control)): 
            self.teachModeButton_control[i].clicked.connect(self.teachModeButton_controlCommand[i])

    def initTeachMode(self):
        self.showStatus("===> Enter teach mode")
        uiWorking.label_directory.clear()
        uiWorking.textBrowser_showfile.clear()
        self.activateTeachMode(True)

    def activateTeachMode(self,state):
        if state == True:
            self.showStatus("===> Enable teachMode button")
        else: 
            self.showStatus("===> Disable teachMode button")

        for i in range(len(self.teachModeButton_Fw)):
            self.teachModeButton_Fw[i].setEnabled(state)
        for i in range(len(self.teachModeButton_Rw)):
            self.teachModeButton_Rw[i].setEnabled(state)
        for i in range(len(self.teachModeButton_coil)):
            self.teachModeButton_coil[i].setEnabled(state)
        for i in range(len(self.teachModeButton_control)):
            self.teachModeButton_control[i].setEnabled(state)

    def exitTeachMode(self):
        self.activateTeachMode(False)
        control.disable_control_option(False)

    def saveFile(self):
        pass

    def setPoint(self):
        pass

    def setZero(self):
        pass
    
    def monitorTeachMode(self):
        try:
            Teach_mode.teach_axis = Teach_mode.no_choise_axis
            new_pos_X = self.pos_X; new_pos_Y = self.pos_Y; new_pos_A = self.pos_A
            new_pos_B = self.pos_B; new_pos_C = self.pos_C; new_pos_Z = self.pos_Z
            while True:
                
                self.pulse_teach_packet = [0,0,0,0,0,0]
                state_runing = False
                self.button_state = self.read_state_button()
                self.Read_pulse_PWM_from_slaves()
                self.Kinematics_Zaxis_mode_02()
                
                # gửi command quay chiều thuận trục được chọn
                if Teach_mode.teach_axis == Teach_mode.TEACH_X_AXIS:
                    if (self.button_state > self.pre_button_state):  new_pos_X = -1000
                    if (self.button_state < self.pre_button_state):  new_pos_X = 1000
                    pulse_teach = int((new_pos_X - self.pos_X)/self.gear_ratio_X)
                    if self.pos_X < -1000 or self.pos_X > 1000: self.button_state = self.pre_button_state
        
                if Teach_mode.teach_axis == Teach_mode.TEACH_Y_AXIS:
                    if (self.button_state > self.pre_button_state):  new_pos_Y = -1600
                    if (self.button_state < self.pre_button_state):  new_pos_Y = 1600
                    pulse_teach = int((new_pos_Y - self.pos_Y)/self.gear_ratio_Y)
                    if self.pos_Y < -1600 or self.pos_Y > 1600: self.button_state = self.pre_button_state

                if Teach_mode.teach_axis == Teach_mode.TEACH_Z_AXIS:
                    if (self.button_state > self.pre_button_state):  new_pos_Z = -1000
                    if (self.button_state < self.pre_button_state):  new_pos_Z = 1000
                    pulse_teach = int((new_pos_Z - self.pos_Z)/self.gear_ratio_Z)
                    if self.pos_Z < -1000 or self.pos_Z > 1000: self.button_state = self.pre_button_state

                if Teach_mode.teach_axis == Teach_mode.TEACH_A_AXIS:
                    if (self.button_state > self.pre_button_state):  new_pos_A = -180
                    if (self.button_state < self.pre_button_state):  new_pos_A = 180
                    pulse_teach = int((new_pos_A - self.pos_A)/self.gear_ratio_A)
                    if self.pos_A < -180 or self.pos_A > 180: self.button_state = self.pre_button_state

                if (Teach_mode.teach_axis == Teach_mode.TEACH_B_AXIS): 
                    if (self.button_state > self.pre_button_state):  new_pos_B = -180
                    if (self.button_state < self.pre_button_state):  new_pos_B = 180
                    pulse_teach = int((new_pos_B - self.pos_B)/self.gear_ratio_B)
                    if self.pos_B < -180 or self.pos_B > 180: self.button_state = self.pre_button_state

                if (Teach_mode.teach_axis == Teach_mode.TEACH_C_AXIS):
                    if (self.button_state > self.pre_button_state):  new_pos_C = -1000
                    if (self.button_state < self.pre_button_state):  new_pos_C = 1000
                    pulse_teach = int((new_pos_C - self.pos_C)/self.gear_ratio_C)
                    if self.pos_C < -1000 or self.pos_C > 1000: self.button_state = self.pre_button_state

                if self.button_state != self.pre_button_state:
                    self.pulse_teach_packet[Teach_mode.teach_axis] = pulse_teach   
                    Run.send_to_execute_board(self.pulse_teach_packet,0)
                    state_runing = True
        
                while state_runing:
                    # Đọc giá trị thanh ghi lưu giá trị xung đang phát ra
                    self.Read_pulse_PWM_from_slaves()
                    self.button_state = self.read_state_button()
                    if self.button_state == self.pre_button_state:
                        Monitor_in_out.stop_motor()
                        state_runing = False
                        break  # thoat khỏi vong lặp while
                
                if (self.monitor_off == True):
                    self.monitor_off = False
                    Teach_mode.teach_axis = Teach_mode.no_choise_axis
                    break
        except Exception as e:
            print(str(e))
            return

    def Kinematics_Zaxis_mode_02(self):
            if Teach_mode.teach_axis == Teach_mode.TEACH_Z1_AXIS:
                Yspray_expect = self.pos_Yspray
                while True:
                    running = False
                    self.button_state = self.read_state_button()
                    self.Read_pulse_PWM_from_slaves()
                    if (self.button_state > self.pre_button_state): # nhấn Z1-
                        # tính động học
                        new_pos_A = self.pos_A - 2
                        new_pos_Y = Yspray_expect - self.spray_axis*math.cos((new_pos_A*math.pi)/180)
                        new_pos_Z = 0
                        pulse_Y_teach = int((new_pos_Y - self.pos_Y)/self.gear_ratio_Y)
                        pulse_A_teach = int((new_pos_A - self.pos_A)/ self.gear_ratio_A)
                        pulse_Z_teach = int((new_pos_Z - self.pos_Z)/self.gear_ratio_Z)
                        if(self.pos_Z > 0): self.pulse_teach_packet = [0,0,pulse_Z_teach,0,0,0]
                        else:               self.pulse_teach_packet = [0,pulse_Y_teach,0,pulse_A_teach,0,0]
                        
                    if (self.button_state < self.pre_button_state): # nhấn Z1+
                        
                        new_pos_A = self.pos_A + 2 #(góc A của mỗi lần chạy: càng nhỏ chạy càng chính xác)
                        new_pos_Y = Yspray_expect - self.spray_axis*math.cos((new_pos_A*math.pi)/180)
                        new_pos_Z = 600
                        pulse_A_teach = int((new_pos_A - self.pos_A)/self.gear_ratio_A)
                        pulse_Y_teach = int((new_pos_Y - self.pos_Y)/self.gear_ratio_Y)
                        pulse_Z_teach = int((new_pos_Z - self.pos_Z)/self.gear_ratio_Z)
                        if new_pos_A >= 90: self.pulse_teach_packet = [0,0,pulse_Z_teach,0,0,0]
                        else:               self.pulse_teach_packet = [0,pulse_Y_teach,0,pulse_A_teach,0,0]
                    
                    if self.button_state != self.pre_button_state:
                        Run.send_to_execute_board(self.pulse_teach_packet,0)
                        running = True

                    while running:
                        self.button_state = self.read_state_button()
                        self.Read_pulse_PWM_from_slaves()
                        if self.button_state == self.pre_button_state:
                            Monitor_in_out.stop_motor()
                            running = False
                            break  # thoat khỏi vong lặp while
                    
                    # nếu disable teach mode thì thoát khỏi 
                    if (self.monitor_off == True) or (Teach_mode.teach_axis != Teach_mode.TEACH_Z_AXIS):
                        break
            else: pass

class controlButton():
    def __init__(self):
        self.go_machine_home = False
        self.defineControlButton()

    def defineControlButton(self):
        self.controlButtonName = [uiWorking.pushButton_choosefile, uiWorking.pushButton_teach, uiWorking.pushButton_settings,
                                   uiWorking.pushButton_manual, uiWorking.pushButton_gotozero, uiWorking.pushButton_machinehome]
        self.controlButtonCommand = [self.chooseFile, self.enterTeachMode, self.enterSettings, self.enterManual, 
                                        self.gotoZeroPosition, self.gotoMachinePosition]
        for i in range(len(self.controlButtonName)):
            self.controlButtonName[i].clicked.connect(self.controlButtonCommand[i])

    def disable_control_option(self, state):
        for i in range(len(self.controlButtonName)):
            self.controlButtonName[i].setDisabled(state)

    def chooseFile(self):
        main_window.showStatus("Chế độ chọn file.pnt")
        try:
            pathFile = wFile.show_initial_directory()
            main_window.showStatus("pathFile: "+ pathFile)
            uiWorking.label_directory.setText(pathFile)
            content = wFile.get_file(pathFile)
            uiWorking.textBrowser_showfile.setText(content)

        except Exception as error: 
            uiWorking.label_directory.setText("NO FILE LOADED")
            main_window.showStatus(error)
            return

    def enterTeachMode(self):
        main_window.showStatus("Chế độ teach mode")
        self.disable_control_option(True)
        teach.initTeachMode()
        teach.monitorTeachMode()
        

    def enterSettings(self):
        main_window.showStatus("Chế độ cài đặt thông số motor")

    def enterManual(self):
        main_window.showStatus("Chế độ manual bật tắt coilY")

    def gotoZeroPosition(self):
        main_window.showStatus("Đưa tay máy về vị trí 0")
        workSerial.commandGotoZero()
        while True:
            positionCompleted = workSerial.commandPositionCompleted()
            main_window.showCurrentPositions()
            if positionCompleted[0] == 1: 
                break
        main_window.showStatus("Tay máy đã về vị trí 0")

    def gotoMachinePosition(self):
        if self.go_machine_home == False:
            main_window.showStatus("Đưa tay máy về vị trí cảm biến gốc máy")
            workSerial.commandCheckXYZAsensor()
            
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
            workSerial.setZeroPositions()
            time.sleep(0.5)
            for i in range(monitorPos.MAX_AXIS):
                #Run.send_to_execute_board(pulse_to_machine_axis[i],speed_axis[i])
                self.go_machine_axis_state = False
                while True: 
                    # Đọc giá trị thanh ghi lưu giá trị xung đang phát ra
                    positionCompleted = workSerial.commandPositionCompleted()
                    main_window.showCurrentPositions()

                    if (positionCompleted[0]==1 or self.sensor_machine_axis[i] == 0):
                        # dừng động cơ
                        #Monitor_in_out.stop_motor()
                        self.go_machine_axis_state = True
                        print("Động cơ dừng")
                        break  # thoat khỏi vong lặp while

            # sau khi chạy hết các động cơ về vị trí cảm biến
            # tịnh tiến các trục X,Y,Z ra khỏi vị trí cảm biến và set lại 0
            time.sleep(0.5)
            #Run.send_to_execute_board(pulse_to_begin_position,120)
            while True:
                
                # Đọc trạng thái phát xung đã hoàn tất chưa
                positionCompleted = workSerial.commandPositionCompleted()
                # Đọc giá trị thanh ghi lưu giá trị xung đang phát ra
                main_window.showCurrentPositions()
                if positionCompleted[0] == 1: 
                    # set lại các thông số motor, đưa giá trị current_position về 0
                    workSerial.setZeroPositions()
                    workSerial.commandCheckXYZAsensor()
                    break
       
            self.disable_control_option(False)
            self.go_machine_home = True # đã về home
        
        main_window.showStatus("Tay máy đã về vị trí cảm biến gốc máy")


#================================================================================================
if __name__ == "__main__": # define điểm bắt đầu chạy chương trình
    app = QApplication([])
    window = QMainWindow()
    uiWorking = Ui_MainWindow()

    main_window = workingWindow()
    teach = teach_mode()
    control = controlButton()
    wFile = workingFile()
    workSerial = Read_Write_to_Serial()
    monitorPos = monitor()

    main_window.showWorkingWindow()
    sys.exit(app.exec_())
