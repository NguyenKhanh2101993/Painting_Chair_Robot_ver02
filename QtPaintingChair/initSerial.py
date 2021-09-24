import modbus_tk.defines as cst
import modbus_tk.modbus_rtu as rtu
import serial
import serial.tools.list_ports_windows

class Read_Write_to_Serial:
    def __init__(self):
        self.SLAVE_02 = 2
        self.CHOOSE = 1
        self.defineModbusAddr()

    def defineModbusAddr(self):
        self.CURRENT_POSITION_MODBUS_ADDR = 0
        self.ENABLE_HOME_MODBUS_ADDR = 15
        self.EXECUTE_PULSE_DONE = 0
        self.CHECK_SENSOR_XYZA_ADDR = 3
        self.SET_ZERO_POSITION_ADDR = 16
        self.POINT2POINT_MODBUS_ADDR = 7
        self.STOP_MOTOR_MODBUS_ADDR = 1
        self.SAVE_PACKET_DATA_MODBUS_ADDR = 10
        self.TABLE_CHANGE_STATE_MODBUS_ADDR = 4
        self.SPRAY_ON_MODBUS_ADDR = 6
        self.SPRAY_OFF_MODBUS_ADDR = 5
        self.PAUSE_MOTOR_MODBUS_ADDR = 8
        self.RESUME_MOTOR_MODBUS_ADDR = 9
        self.CHANGE_STATE_RUN_BLOCK_MODBUS_ADDR = 11

    def Init_Serial(self,baud,com): # Connect to Arduino
        connect = 0
        try:
            self.master = rtu.RtuMaster(serial.Serial(port = com, baudrate = baud, bytesize=8, parity='N', stopbits=1, xonxoff=0))
            self.master.set_timeout(5.0)
            self.master.set_verbose(True)
            connect = 1
        except Exception as e:
            print(str(e))
            connect = 0
            pass
        #logger.info(master.execute(1, cst.READ_COILS, 0, 10))
        #logger.info(master.execute(1, cst.READ_DISCRETE_INPUTS, 0, 8))
        #logger.info(master.execute(1, cst.READ_INPUT_REGISTERS, 100, 3))
        #logger.info(master.execute(1, cst.READ_HOLDING_REGISTERS, 100, 12))
        #logger.info(master.execute(1, cst.WRITE_SINGLE_COIL, 7, output_value=1))
        #logger.info(master.execute(1, cst.WRITE_SINGLE_REGISTER, 100, output_value=54))
        #logger.info(master.execute(1, cst.WRITE_MULTIPLE_COILS, 0, output_value=[1, 1, 0, 1, 1, 0, 1, 1]))
        #logger.info(master.execute(1, cst.WRITE_MULTIPLE_REGISTERS, 100, output_value=xrange(12)))Set_zero_position
        if connect == 1:
            #messagebox.showinfo("Serial Comunication", "SUCCESS CONNECTION")
            return connect
        else:
            #messagebox.showinfo("Serial Comunication", "FAILURE CONNECTION")
            return connect

    def detect_comports(self):
        comports = []
        portdata = serial.tools.list_ports_windows.comports()
        for i in range(len(portdata)):
            port = portdata[i]
            str_port = str(port) 
            split_port = str_port.split(" ")
            comports.append(split_port[0])
        return comports   

    def choose_comports(self,baud,com):
        result = 0
        result = self.Init_Serial(baud,com)
        return result

    def readCurrentPosition(self):
        value = self.master.execute (self.SLAVE_02, cst.READ_HOLDING_REGISTERS, self.CURRENT_POSITION_MODBUS_ADDR, 12)
        return value

    def commandGotoZero(self):
        self.master.execute(self.SLAVE_02, cst.WRITE_SINGLE_COIL, self.ENABLE_HOME_MODBUS_ADDR, output_value = self.CHOOSE)

    def commandPositionCompleted(self):
        status = self.master.execute(self.SLAVE_02, cst.READ_COILS, self.EXECUTE_PULSE_DONE, 1)
        return status

    def commandCheckXYZAsensor(self):
        self.master.execute(self.SLAVE_02, cst.WRITE_SINGLE_COIL, self.CHECK_SENSOR_XYZA_ADDR, output_value = self.CHOOSE)

    def setZeroPositions(self):
        self.master.execute(self.SLAVE_02, cst.WRITE_SINGLE_COIL, self.SET_ZERO_POSITION_ADDR, output_value = self.CHOOSE)

    def sendMultipledata(self, data, startAddress):
        self.master.execute(self.SLAVE_02, cst.WRITE_MULTIPLE_REGISTERS, startAddress , output_value = data)

    def commandPointToPoint(self):
        self.master.execute(self.SLAVE_02, cst.WRITE_SINGLE_COIL, self.POINT2POINT_MODBUS_ADDR, output_value = self.CHOOSE)

    def commandStopMotor(self):
        self.master.execute(self.SLAVE_02, cst.WRITE_SINGLE_COIL, self.STOP_MOTOR_MODBUS_ADDR, output_value = self.CHOOSE)

    def commandSavePacketsData(self):
        self.master.execute(self.SLAVE_02, cst.WRITE_SINGLE_COIL, self.SAVE_PACKET_DATA_MODBUS_ADDR, output_value = self.CHOOSE)

    def commandRotateTable(self):
        self.master.execute(self.SLAVE_02, cst.WRITE_SINGLE_COIL, self.TABLE_CHANGE_STATE_MODBUS_ADDR, output_value = self.CHOOSE)

    def commandTurnOnSpray(self):
        self.master.execute(self.SLAVE_02, cst.WRITE_SINGLE_COIL, self.SPRAY_ON_MODBUS_ADDR, output_value = self.CHOOSE) 

    def commandTurnOffSpray(self):
        self.master.execute(self.SLAVE_02, cst.WRITE_SINGLE_COIL, self.SPRAY_OFF_MODBUS_ADDR, output_value = self.CHOOSE)   
       
    def commandPauseMotor(self):
        self.master.execute(self.SLAVE_02, cst.WRITE_SINGLE_COIL, self.PAUSE_MOTOR_MODBUS_ADDR, output_value = self.CHOOSE)
    
    def commandResumeMotor(self):
        self.master.execute(self.SLAVE_02, cst.WRITE_SINGLE_COIL, self.RESUME_MOTOR_MODBUS_ADDR, output_value = self.CHOOSE)

    def commandChangeStateBlockRun(self):
        self.master.execute(self.SLAVE_02, cst.WRITE_SINGLE_COIL, self.CHANGE_STATE_RUN_BLOCK_MODBUS_ADDR, output_value = self.CHOOSE)