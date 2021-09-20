import modbus_tk.defines as cst
import modbus_tk.modbus_rtu as rtu
#import pickle
import serial
import serial.tools.list_ports_windows

class Read_Write_to_Serial():

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
        if result == 1:
                print("Khởi tạo cổng COM đã xong")
        else: 
                print("Không nhận được cổng COM")
        return result