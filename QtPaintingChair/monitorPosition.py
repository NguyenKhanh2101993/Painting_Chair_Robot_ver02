from initSerial import Read_Write_to_Serial as workSerial
import math

class monitor:
    def __init__(self):
        self.MAX_AXIS = 6
        self.spray_axis = 550
        self.modbus = workSerial()

    # giám sát vị trí các trục tay máy
    def read_pulse_from_slaves(self):
        gearRatio = [1,1,1,1,1,1]
        current_position_motor = []
        current_pulse = []
        resultCurrentPos = []
        index = 0
        # Đọc giá trị xung của tất cả động cơ 
        try:
            # Đọc giá trị current position ở địa chỉ bắt đầu từ 0, đọc 12 giá trị 16 bit
            current_position = self.modbus.readCurrentPosition()
            for i in range(self.MAX_AXIS):
                current_position_motor.append((current_position[index] << 16) | (current_position[index+1] & 65535))
                index = index + 2
                current_pulse.append(self.check_negative_num(current_position_motor[i]))
           
            resultCurrentPos = self.calculateCurrentPos(current_pulse, gearRatio)

            return resultCurrentPos

        except Exception as error:
            print(str(error))
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


    """""
        self.var1.set(str(round(self.pos_X,3))+ " mm")
        self.var2.set(str(round(self.pos_Y,3))+ " mm")
        self.var3.set(str(round(self.pos_Z,3))+ " mm")
        self.var4.set(str(round(self.pos_A,3))+ " deg")
        self.var5.set(str(round(self.pos_B,3))+ " deg")
        self.var6.set(str(round(self.pos_C,3))+ " deg")

       
        self.var20.set(str(round((self.pos_Yspray - self.spray_axis),3)) + " mm")
        self.var21.set(str(round(self.pos_Zspray,3)) + " mm")
        # lưu giá trị tọa độ theo G54 là tọa độ chạy chương trình
        self.G54_pulse = [self.pos_X - self.offset_x_axis, self.pos_Y - self.offset_y_axis,
                          self.pos_Z - self.offset_z_axis, self.pos_A - self.offset_a_axis,
                          self.pos_B - self.offset_b_axis, self.pos_C - self.offset_c_axis]

        self.var11.set(str(round(self.G54_pulse[0],3))+ " mm")
        self.var12.set(str(round(self.G54_pulse[1],3))+ " mm")
        self.var13.set(str(round(self.G54_pulse[2],3))+ " mm")
        self.var14.set(str(round(self.G54_pulse[3],3))+ " deg")
        self.var15.set(str(round(self.G54_pulse[4],3))+ " deg")
        self.var16.set(str(round(self.G54_pulse[5],3))+ " deg")

        Show_Screen.update_axis_label()


        def kinematics_Zaxis(self):
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

    """""   