from tkinter import *
from tkinter.ttk import Combobox
from tkinter import filedialog, messagebox, ttk
import tkinter.font as font
#from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import modbus_tk
import modbus_tk.defines as cst
import modbus_tk.modbus_rtu as rtu

import pickle
import serial
import time
import threading
import queue
import math
import webbrowser
import numpy as np
#========================================================================
root = Tk()
root.title('CHAIR PAINTING MACHINE')
root_icon = PhotoImage(file = 'Robot.png')
button_01 = PhotoImage(file = 'button1.png')
root.iconphoto(False, root_icon)
root.resizable(width = True, height = True)
root.minsize(width = 1500, height = 750)
estyle = ttk.Style()
estyle.theme_use('alt')
#========================================================================
#========================================================================
global CHOOSE, NOCHOOSE
global SLAVE_02, SLAVE_03
#global outfile, file, content
CHOOSE = 1
NOCHOOSE = 0
SLAVE_02 = 2
SLAVE_03 = 3
#============================================================================================
# Ghi data vào register output của board slave
# Set bit thứ register_name của COIL[] board slaver để chọn đối tượng cần ghi giá trị
# index: số word cần write
# addr: địa chỉ bắt đầu write: 0
# def Write_packet_data_to_output_slave_board():
  
#============================================================================================
# Đọc data từ feedback register của board slave để monitor
# index: số word cần read
# addr: địa chỉ bắt đầu read: SINGLE_REGISTER_ADDR
# def Read_packet_data_from_feedback_register_slave_board():

#============================================================================================
# đưa các trục tay máy sơn về vị trí gốc máy khi mới mở phần mềm.
# phát command để các động cơ chạy tới khi nào gặp cảm biến thì dừng lại
#============================================================================================
class Home_position:
    def __init__(self):
        self.ENABLE_HOME_MODBUS_ADDR = 15
    def Go_Home(self):
        try:
            state = Send_to_Serial.Init_Serial()
            if state == 1:
                master.execute(SLAVE_02, cst.WRITE_SINGLE_COIL, self.ENABLE_HOME_MODBUS_ADDR, output_value = CHOOSE)
                master.execute(SLAVE_03, cst.WRITE_SINGLE_COIL, self.ENABLE_HOME_MODBUS_ADDR, output_value = CHOOSE)
                print("Go to Home")
            else:
                return
            time.sleep(4)
            Home_mode.destroy()
            Show_Screen.Show_screen_options()
            Show_Screen.Show_screen_teach_mode()
            Show_Screen.Show_screen_monitor()
            Show_Screen.Show_screen_res()
            Show_Screen.Show_draw_file()
            Show_Screen.Show_XYZ()
            Show_Screen.Speed_toolbar()
            Show_Screen.Text_box()
            Monitor_mode.Read_pulse_PWM_from_slaves()

        except:
            messagebox.showinfo("Serial Comunication","OPEN SOFWARE FAILED")
            return

#============================================================================================
class Save_file:
        
    def open_file(self):
        Show_Screen.Show_content.delete('1.0','end')
        Show_Screen.Show_content.config(state = NORMAL)
        self.file = filedialog.askopenfile(mode ='r', filetypes =[('File pulse', '*.paint')])
        try:
            show_file = self.file.read()
            Show_Screen.Show_content.insert(END,show_file) # insert all the characters of file into T
        except Exception as err:
            print(str(err))
            return

    def save_file(self):
        retrieve_text = Show_Screen.Show_content.get('1.0','end-1c')
        savefile = filedialog.asksaveasfile(mode='w+', defaultextension='*.paint', filetypes =[('File pulse', '*.paint')])
        try:
            savefile.write(retrieve_text)  # retrieve_text phải là các ký tự không có dấu.
            savefile.close()
            Show_Screen.Inform_App_Status("ĐÃ LƯU")
            
        except Exception as err:
            print(str(err))
            return
#============================================================================================
class Read_Write_to_Serial:
    def Init_Serial(self): # Connect to Arduino
        global master
        #try: 
            #baud = int(ComunicationRobot.choose_BAUD.get())
            #com  = str(ComunicationRobot.choose_COM.get())
        baud = 115200
        com  = 'COM4'
         #except Exception as e:
         #   messagebox.showinfo("Serial Comunication", "Error: Please choose baudrate and com port")
         #   print(str(e))
         #   return
        try:         
                #Connect to the slave
                master = rtu.RtuMaster(serial.Serial(port= com, baudrate = baud, bytesize=8, parity='N', stopbits=1, xonxoff=0))
                master.set_timeout(5.0)
                master.set_verbose(True)
                #logger.info(master.execute(1, cst.READ_COILS, 0, 10))
                #logger.info(master.execute(1, cst.READ_DISCRETE_INPUTS, 0, 8))
                #logger.info(master.execute(1, cst.READ_INPUT_REGISTERS, 100, 3))
                #logger.info(master.execute(1, cst.READ_HOLDING_REGISTERS, 100, 12))
                #logger.info(master.execute(1, cst.WRITE_SINGLE_COIL, 7, output_value=1))
                #logger.info(master.execute(1, cst.WRITE_SINGLE_REGISTER, 100, output_value=54))
                #logger.info(master.execute(1, cst.WRITE_MULTIPLE_COILS, 0, output_value=[1, 1, 0, 1, 1, 0, 1, 1]))
                #logger.info(master.execute(1, cst.WRITE_MULTIPLE_REGISTERS, 100, output_value=xrange(12)))Set_zero_position
                ComunicationRobot.Connect.config(state=DISABLED)
                ComunicationRobot.Disconnect.config(state = NORMAL)
                #messagebox.showinfo("Serial Comunication", "SUCCESS CONNECTION")
                return 1
        except Exception as e:
                messagebox.showinfo("Serial Comunication", "FAILURE CONNECTION")
                print(str(e))
                return 0

    def Disconnect_Serial(self):
        try:
            master_closed = master._do_close()
            if master_closed:
                messagebox.showinfo("Serial Comunication", "DISCONNECTED")
                ComunicationRobot.Connect.config(state=NORMAL)
                ComunicationRobot.Disconnect.config(state = DISABLED)
        except:
                return
#========================================================================
class Validate_modbus_rtu:
    def write_mutiple_register(self):
        send_data = [0,0,0,0,0,0,0,0]
        data = [-10000,-20000,-30000,-40000]

        send_data[0] = int(data[0]) >> 16
        send_data[1] = int(data[0]) & 65535
    
        send_data[2] = int(data[1]) >> 16
        send_data[3] = int(data[1]) & 65535
   
        send_data[4] = int(data[2]) >> 16
        send_data[5] = int(data[2]) & 65535

        send_data[6] = int(data[3]) >> 16
        send_data[7] = int(data[3]) & 65535

        #master.execute(2, cst.WRITE_MULTIPLE_REGISTERS, 10, output_value = send_data)
#========================================================================
# END CLASS
#========================================================================
validate_rtu = Validate_modbus_rtu()
#========================================================================
class Screen:
    def __init__(self):
        self.Teach_option = Button()
        self.Home_option = Button()
        self.Manual_option = Button()
        self.Load_file = Button()

        self.Disable_teach_mode = Button()
        self.Set_teach_point = Button()
        self.X_button = Button()
        self.Y_button = Button()
        self.Z_button = Button()
        self.A_button = Button()
        self.B_button = Button()
        self.C_button = Button()
        self.spray_on = Button()
        self.spray_off = Button()
        self.save_file_button = Button()

        self.Auto_run_button = Button()

        self.label_X = Label()
        self.label_Y = Label()
        self.label_Z = Label()
        self.label_A = Label()
        self.label_B = Label()
        self.label_C = Label()

        self.X1_button = Button()
        self.X10_button = Button()
        self.X100_button = Button()
        self.X1000_button = Button()

        self.label_X_spray = Label()
        self.label_Y_spray = Label()
        self.label_Z_spray = Label()
        self.label_B_spray = Label()
        self.spray_on_state = Label()
        self.label_axis_monitor = Label()

        self.speed_value = DoubleVar()
        self.speed_scale = Scale()
        self.Show_content = Text()

        self.bg_frame11 = Canvas()
        self.Frame11 = LabelFrame()
        # góc của trục Y so với trục X hiện thị trên canvas
        self.degXY = 0
        self.string_content = StringVar()
    
#========================================================================
    def Show_screen_options(self):
        Frame0 = LabelFrame(root)#,text="TÙY CHỌN")
        Frame0.place(x = 900, y = 150)
        bg_frame0 = Canvas(Frame0, bg="gray", height=30, width=610, bd = 1)
        bg_frame0.pack(side = LEFT)
       
        #========================================================================
        self.Teach_option = Button(Frame0, text ='TEACH MODE', justify = LEFT, width = 15, command = Teach_mode.Enable_teach_options, 
                              font = ("Arial",10,"bold"), bg = '#006699', activebackground = 'green')
        self.Teach_option.place(x = 5, y = 5)
        self.Home_option = Button(Frame0, text ='HOME', justify = LEFT, width = 15, command = Monitor_mode.Go_to_home,
                              font = ("Arial",10,"bold"), bg = '#006699', activebackground = 'green')
        self.Home_option.place(x = 150, y = 5)
        self.Manual_option = Button(Frame0, text ='MANUAL', justify = LEFT, width = 15, command = validate_rtu.write_mutiple_register,
                              font = ("Arial",10,"bold"), bg = '#006699', activebackground = 'green')
        self.Manual_option.place(x = 300, y = 5)
        self.Load_file = Button(Frame0, text ='CHOOSE FILE', justify = LEFT, width = 15, command = Work_file.open_file,
                              font = ("Arial",10,"bold"), bg = '#006699', activebackground = 'green')
        self.Load_file.place(x = 450, y = 5)  
#========================================================================
    def Show_screen_teach_mode(self):
        Frame1 = LabelFrame(root,text="CHẾ ĐỘ DẠY ROBOT SƠN")
        Frame1.place(x = 10, y = 150)
        bg_frame1 = Canvas(Frame1, bg="wheat", height=370, width=300, bd = 1)
        bg_frame1.pack(side = LEFT)
        
        #========================================================================
        self.Disable_teach_mode = Button(Frame1, text ='DISABLE TEACH MODE', justify = LEFT, width = 20, activebackground = 'green', 
                                    bg = "red",  command = Teach_mode.Disable_teach_options)
        self.Disable_teach_mode.config(state = DISABLED)
        self.Disable_teach_mode.place(x = 20, y = 10)
        self.Set_teach_point = Button(Frame1, text ='SET POINT', justify = LEFT, width = 10, activebackground = 'red',
                                 command = Teach_mode.Show_point_to_textbox, bg = "green", state=DISABLED)
        self.Set_teach_point.place(x = 200, y = 10)

        self.X_button = Button(Frame1, text ='Súng sơn sang trái/phải - TRỤC X', justify = LEFT, width = 30, activebackground = 'green', 
                                bg = "gray", command = Teach_mode.Teach_X_Axis, state=DISABLED)
        self.X_button.place(x = 10, y = 55)
        self.Y_button = Button(Frame1, text = 'Súng sơn đi tới/lui - TRỤC Y', justify = LEFT, width = 30, activebackground = 'green', 
                                 bg = "gray",  command = Teach_mode.Teach_Y_Axis, state=DISABLED)
        self.Y_button.place(x = 10, y = 95)
        self.Z_button = Button(Frame1, text = 'Súng sơn đi lên/xuống - TRỤC Z', justify = LEFT, width = 30, activebackground = 'green', 
                              bg = "gray", command = Teach_mode.Teach_Z_Axis, state=DISABLED)
        self.Z_button.place(x = 10, y = 135)
        self.A_button = Button(Frame1, text = 'Súng sơn quay - TRỤC A', justify = LEFT, width = 30, activebackground = 'green', 
                               bg = "gray", command = Teach_mode.Teach_A_Axis, state=DISABLED)
        self.A_button.place(x = 10, y = 175)
        self.B_button = Button(Frame1, text = 'Súng sơn quay - SÚNG SƠN', justify = LEFT, width = 30, activebackground = 'green', 
                               bg = "gray", command = Teach_mode.Teach_B_Axis, state=DISABLED)
        self.B_button.place(x = 10, y = 215)
        self.C_button = Button(Frame1, text = 'Xoay ghế - TRỤC GHẾ', justify = LEFT, width = 30, activebackground = 'green',
                               bg = "gray", command = Teach_mode.Teach_C_Axis, state=DISABLED)
        self.C_button.place(x = 10, y = 255)
        self.spray_on = Button(Frame1, text = 'Bật phun sơn', justify = LEFT, width = 12, activebackground = 'green',
                               command = Teach_mode.Spray_on, bg = "gray", state=DISABLED)
        self.spray_on.place(x = 10, y = 295)
        self.spray_off = Button(Frame1, text = 'Tắt phun sơn', justify = LEFT, width = 12, activebackground = 'green',
                               command = Teach_mode.Spray_off, bg = "gray", state=DISABLED)
        self.spray_off.place(x = 135, y = 295)
        save_file_font = font.Font(size=14)
        self.save_file_button = Button(Frame1, text = 'SAVE FILE', justify = LEFT, width = 10, activebackground = 'green',
                               command = Teach_mode.Save_file, bg = "#339966", state=DISABLED)
        self.save_file_button.place(x = 180, y = 330)
        self.save_file_button['font'] = save_file_font
        self.set_zero_point = Button(Frame1, text = 'SET 0', justify = LEFT, width = 10, activebackground = 'green',
                               command = Teach_mode.Set_zero_position, bg = "blue", state=DISABLED)
        self.set_zero_point.place(x = 10, y = 330)
        self.set_zero_point['font'] = save_file_font
#========================================================================
    def Show_screen_monitor(self):
        Frame3 = LabelFrame(root, text="HIỂN THỊ VỊ TRÍ CÁC TRỤC CỦA MÁY SƠN")
        Frame3.place(x = 350, y = 150)
        bg_frame3 = Canvas(Frame3, bg="wheat", height=210, width=280, bd = 1)
        bg_frame3.pack(side = LEFT)
        #========================================================================
        self.label_X = Label(Frame3, text= 0,fg ='red', textvariable = Monitor_mode.var1,bd = 1,width=15,relief = 'solid',
                        font = ("Arial",11,"bold") )
        self.label_X.place(x = 140, y = 30 )
        self.label_Y = Label(Frame3, text= 0,fg ='red', textvariable = Monitor_mode.var2, bd = 1,width=15,relief = 'solid',
                        font = ("Arial",11,"bold"))
        self.label_Y.place(x = 140, y = 60 )
        self.label_Z = Label(Frame3, text= 0,fg ='red', textvariable = Monitor_mode.var3, bd = 1,width=15,relief = 'solid',
                        font = ("Arial",11,"bold"))
        self.label_Z.place(x = 140, y = 90 )
        self.label_A = Label(Frame3, text= 0,fg ='red', textvariable = Monitor_mode.var4, bd = 1,width=15,relief = 'solid',
                        font = ("Arial",11,"bold"))
        self.label_A.place(x = 140, y = 120 )
        self.label_B = Label(Frame3, text= 0,fg ='red', textvariable = Monitor_mode.var5, bd = 1,width=15,relief = 'solid',
                        font = ("Arial",11,"bold"))
        self.label_B.place(x = 140, y = 150 )
        self.label_C = Label(Frame3, text= 0,fg ='red', textvariable = Monitor_mode.var6, bd = 1,width=15,relief = 'solid',
                        font = ("Arial",11,"bold"))
        self.label_C.place(x = 140, y = 180 )

        Label(Frame3,text = 'TRỤC X (X)',fg ='black', bg = '#99CC00', justify = LEFT, relief = 'solid',width=17).place(x=10, y=30)
        Label(Frame3,text = 'TRỤC Y (Y)',fg ='black', bg = '#99CC00',justify = LEFT, relief = 'solid',width=17).place(x=10, y=60)
        Label(Frame3,text = 'TRỤC Z (Z)',fg ='black', bg = '#99CC00', justify = LEFT, relief = 'solid',width=17).place(x=10, y=90)
        Label(Frame3,text = 'TRỤC A (A)',fg ='black', bg = '#99CC00', justify = LEFT, relief = 'solid',width=17).place(x=10, y=120)
        Label(Frame3,text = 'TRỤC SÚNG SƠN (B)',fg ='black', bg = '#99CC00', justify = LEFT, relief = 'solid',width=17).place(x=10, y=150)
        Label(Frame3,text = 'TRỤC GHẾ (C)',fg ='black', bg = '#99CC00', justify = LEFT, relief = 'solid',width=17).place(x=10, y=180)
#========================================================================
    def Show_screen_res(self):
        Frame4 = LabelFrame(root, text="ĐỘ PHÂN GIẢI")
        Frame4.place(x = 10, y = 560)
        bg_frame4 = Canvas(Frame4, bg="#FFCC66", height=50, width=300, bd = 1)
        bg_frame4.pack(side = LEFT)
        #========================================================================
        #========================================================================
        self.X1_button = Button(Frame4, text ='x1', justify = LEFT, width = 5, activebackground = 'green',
                               command = Teach_mode.X1_resolution, state=DISABLED, bg = "gray")
        self.X1_button.place(x = 20, y = 15)
        self.X10_button = Button(Frame4, text = 'x10', justify = LEFT, width = 5, activebackground = 'green',
                               command = Teach_mode.X10_resolution, state=DISABLED, bg = "gray")
        self.X10_button.place(x = 90, y = 15)
        self.X100_button = Button(Frame4, text = 'x100', justify = LEFT, width = 5, activebackground = 'green',
                               command = Teach_mode.X100_resolution, state=DISABLED, bg = "gray")
        self.X100_button.place(x = 160, y = 15)
        self.X1000_button = Button(Frame4, text = 'x1000', justify = LEFT, width = 5, activebackground = 'green',
                               command = Teach_mode.X1000_resolution, state=DISABLED, bg = "gray")
        self.X1000_button.place(x = 230, y = 15)
#========================================================================
    def Show_draw_file(self):
        self.Frame11 = LabelFrame(root)
        self.Frame11.place(x = 900, y = 220)
        self.bg_frame11 = Canvas(self.Frame11, bg="black", height=565, width=610, bd = 1)
        self.bg_frame11.pack(side = LEFT)

        # vẽ trục Z
        self.bg_frame11.create_line(10,70,10,160,fill = 'white',width = 2)
        self.bg_frame11.create_line(10,160,6,150,fill = 'white',width = 2)
        self.bg_frame11.create_line(10,160,14,150,fill = 'white',width = 2)
        # vẽ trục X
        self.bg_frame11.create_line(10,70,100,70,fill = 'white',width = 2)
        self.bg_frame11.create_line(100,70,90,64,fill = 'white',width = 2)
        self.bg_frame11.create_line(100,70,90,74,fill = 'white',width = 2)
        # vẽ trục Y
        self.bg_frame11.create_line(10,70,100,30,fill = 'white',width = 2)
        self.bg_frame11.create_line(100,30,90,27,fill = 'white',width = 2)
        self.bg_frame11.create_line(100,30,95,40,fill = 'white',width = 2)

        self.bg_frame11.create_text(10,180,anchor = W, text = 'Z+', fill = 'white',font= 'Arial')
        self.bg_frame11.create_text(110,60,anchor = W, text = 'X+', fill = 'white',font= 'Arial')
        self.bg_frame11.create_text(110,15,anchor = W, text = 'Y+', fill = 'white',font= 'Arial')
        # tính góc lệch của trục Y so với trục X
        self.radXY = math.acos(90/math.sqrt(90*90 + 40*40))
        self.degXY = ((self.radXY/math.pi)*180)
        if self.degXY <0:
            self.degXY = 360 - abs(self.degXY)
        #print(self.degXY)
        #========================================================================
    def Show_XYZ(self):
        Frame12 = LabelFrame(root)#, text="HIỂN THỊ TỌA ĐỘ SÚNG SƠN")
        Frame12.place(x = 650, y = 150)
        bg_frame12 = Canvas(Frame12, bg="#333333", height=210, width=210, bd = 1)
        bg_frame12.pack(side = LEFT)

        self.label_X_spray = Label(Frame12, text= 0,fg ='black', textvariable = Monitor_mode.var1, bd = 1,width=15,activeforeground ='red',
                                    relief = 'solid', font = ("Arial",11,"bold"))
        self.label_X_spray.place(x = 70, y = 30 )
        self.label_Y_spray = Label(Frame12, text= 0,fg ='black', textvariable = Monitor_mode.var20, bd = 1,width=15,relief = 'solid',
                                    font = ("Arial",11,"bold"))
        self.label_Y_spray.place(x = 70, y = 60 )
        self.label_Z_spray = Label(Frame12, text= 0,fg ='black', textvariable = Monitor_mode.var21, bd = 1,width=15,relief = 'solid',
                                    font = ("Arial",11,"bold"))
        self.label_Z_spray.place(x = 70, y = 90 )
        self.label_B_spray = Label(Frame12, text= 0,fg ='black', textvariable = Monitor_mode.var5, bd = 1,width=15,relief = 'solid',
                                    font = ("Arial",11,"bold"))
        self.label_B_spray.place(x = 70, y = 120 )

        Label(Frame12,text = 'X',fg ='white', bg = '#777777',justify = LEFT, relief = 'solid', highlightcolor= 'red', width=5, font = ("Arial",11,"bold")).place(x=10, y=30)
        Label(Frame12,text = 'Y',fg ='white', bg = '#777777',justify = LEFT, relief = 'solid', width=5, font = ("Arial",11,"bold")).place(x=10, y=60)
        Label(Frame12,text = 'Z',fg ='white', bg = '#777777',justify = LEFT, relief = 'solid', width=5, font = ("Arial",11,"bold")).place(x=10, y=90)
        Label(Frame12,text = 'B',fg ='white', bg = '#777777',justify = LEFT, relief = 'solid', width=5, font = ("Arial",11,"bold")).place(x=10, y=120)

        spray_state_font = font.Font(size=14)
        self.spray_on_state = Label(Frame12,text = 'TẮT PHUN SƠN',fg ='black', justify = LEFT, relief = 'solid',width=15, bg = 'red')
        self.spray_on_state.place(x=20, y=170)
        self.spray_on_state['font'] = spray_state_font
#======================================================================== 
    def Speed_toolbar(self):
     
        Frame13 = LabelFrame(root, text="TỐC ĐỘ SƠN (%)")
        Frame13.place(x = 10, y = 650)

        self.speed_scale = Scale( Frame13, variable = self.speed_value, from_ = 10, to = 100, orient = HORIZONTAL,  bg = '#669966',
                                length = 300, width=25, bd = 1)   
        self.speed_scale.pack(anchor = CENTER) 
        self.speed_scale.set(30) # khởi tạo giá trị mặc định
#========================================================================
    def Text_box(self):
        Frame14 = LabelFrame(root, text="BẢNG GIÁM SÁT")
        Frame14.place(x = 350, y = 400)

        scroll1 = Scrollbar(Frame14,  orient = VERTICAL)
        scroll2 = Scrollbar(Frame14,  orient = HORIZONTAL)
        self.Show_content = Text(Frame14, height=13, width=62, bd = 1, bg = "#669966",fg ='black', font = ("Arial",11,"bold"),
                                 xscrollcommand = scroll2.set, yscrollcommand = scroll1.set, wrap = 'none')
        scroll1.config (command = self.Show_content.yview)
        scroll2.config (command = self.Show_content.xview)
        scroll1.pack(side=RIGHT, fill= Y)
        scroll2.pack(side=BOTTOM, fill= X)
        self.Show_content.pack(side = LEFT)
        self.Show_content.config(state = DISABLED)

        Frame15 = LabelFrame(root)
        Frame15.place(x = 350, y = 655)
        bg_frame15 = Canvas(Frame15, bg="#003300", height=125, width=510, bd = 1)
        bg_frame15.pack(side = LEFT)
        axis_monitor = font.Font(size=14)
        self.label_axis_monitor = Label(Frame15, text= 0,fg ='red', bg = '#999966', textvariable = self.string_content, bd = 1,height= 2, width=45,relief = 'solid')
        self.label_axis_monitor.place(x = 10, y = 10 )
        self.label_axis_monitor['font'] = axis_monitor

        Jog_button = Button(Frame15, text ='PAUSE', justify = LEFT, height = 1, width = 10, activebackground = 'green',  bd = 2,
                                 command = Run.pause_motor, bg = "#FF9966")
        Jog_button.place(x = 250, y = 70)
        Jog_button['font'] = axis_monitor
        self.Auto_run_button = Button(Frame15, text ='AUTO', justify = LEFT, height = 1, width = 10, activebackground = 'green',  bd = 2,
                                 command = Run.activate_run_mode, bg = "#00CC33")
        self.Auto_run_button.place(x = 120, y = 70)
        self.Auto_run_button['font'] = axis_monitor
        self.Stop_button = Button(Frame15, text ='STOP', justify = LEFT, height = 1, width = 10, activebackground = 'red',  bd = 2,
                                 command = Run.disable_run_mode, bg = "red", state = DISABLED)
        #self.Stop_button.place(x = 380, y = 70)
        self.Stop_button['font'] = axis_monitor
        
    def pause(self, event):
        Run.pause_motor()
        print("pause button")

    def Inform_App_Status(self,a):
        messagebox.showinfo("Inform", a)
#========================================================================
class Monitor_Position_Class():
    def __init__(self):
        #Hiện thị vị trí các trục của robot
        self.var1 = StringVar()
        self.var2 = StringVar()
        self.var3 = StringVar()
        self.var4 = StringVar()
        self.var5 = StringVar()
        self.var6 = StringVar()

        self.var20 = StringVar()
        self.var21 = StringVar()

        self.PWM_VALUE_X_AXIS_MODBUS_ADDR = 0           # Địa chỉ lưu giá trị xung trục X
        self.PWM_VALUE_Y_AXIS_MODBUS_ADDR = 2           # Địa chỉ lưu giá trị xung trục Y
        self.PWM_VALUE_Z_AXIS_MODBUS_ADDR = 4           # Địa chỉ lưu giá trị xung trục Z
        self.PWM_VALUE_A_AXIS_MODBUS_ADDR = 6           # Địa chỉ lưu giá trị xung trục A
        self.PWM_VALUE_SPRAY_AXIS_MODBUS_ADDR = 8       # Địa chỉ lưu giá trị xung trục B
        self.PWM_VALUE_CHAIR_AXIS_MODBUS_ADDR = 10      # Địa chỉ lưu giá trị xung trục C
        self.ROTARY_ENCODER_MODBUS_ADDR       = 20      # Địa chỉ lưu giá trị xung ROTARY ENCODER

        self.rotary_encoder = 0
        self.pre_rotary_encoder = 0

        self.pwm_value_x_axis = 0
        self.pwm_value_y_axis = 0
        self.pwm_value_z_axis = 0
        self.pwm_value_a_axis = 0
        self.pwm_value_b_axis = 0
        self.pwm_value_c_axis = 0

        self.pulse_to_home = [0,0,0,0,0,0]
        self.current_pulse = [0,0,0,0,0,0]
        self.pulse_teach_packet = [0,0,0,0,0,0]

        self.EXECUTE_PULSE_DONE = 0        # Địa chỉ coil đọc trạng thái về Home
        self.home = 0

        self.go_home_state = False
        self.monitor_off = False  # tắt mở chế độ monitor xung
        self.pos_X = 0
        self.pos_Y = 0
        self.pos_Z = 0
        self.pos_A = 0
        self.pos_B = 0
        self.pos_C = 0
        self.pos_Yspray = 0
        self.pos_Zspray = 0

        self.gear_ratio_X = ((80*math.pi)/(128000))
        self.gear_ratio_Y = ((80*math.pi)/(128000))
        self.gear_ratio_Z = ((80*math.pi)/(128000))
        self.gear_ratio_A = (360/128000)
        self.gear_ratio_B = (360/25600)
        self.gear_ratio_C = (360/25600)

        self.spray_axis = 550    # chiều dài trục súng sơn
        
    def Kinematics_Zaxis(self):
        if Teach_mode.teach_axis == Teach_mode.TEACH_Z_AXIS:
            Yspray_expect = self.pos_Yspray
            while Teach_mode.teach_axis == Teach_mode.TEACH_Z_AXIS:
                self.rotary_encoder = self.Read_rotary_encoder()
                self.Read_pulse_PWM_from_slaves()
                if (self.rotary_encoder > self.pre_rotary_encoder):
                    #print("quay thuan")
                    # tính động học
                    # cho trục A quay thêm 1 góc tương đương gain_rotary_encoder xung để có vị trí new_pos_A
                    pulse_A_teach = -1*Teach_mode.gain_rotary_encoder
                    new_pos_A = self.pos_A + (pulse_A_teach*self.gear_ratio_A)
                    if(self.pos_Z > 0): # nếu pos_Z lớn hơn 0 thì quay trục Z, không quay trục A và Y
                        pulse_Z_teach = pulse_A_teach
                        self.pulse_teach_packet = [0,0,pulse_Z_teach,0,0,0]
                    else: # nếu pos_Z <= 0 thì quay trục A và Y
                        new_pos_Y = Yspray_expect - self.spray_axis*math.cos((new_pos_A*math.pi)/180)
                        pulse_Y_teach = int((new_pos_Y - self.pos_Y)/self.gear_ratio_Y) # số xung trục quay Y cần quay
                        self.pulse_teach_packet = [0,pulse_Y_teach,0,pulse_A_teach,0,0]

                if (self.rotary_encoder < self.pre_rotary_encoder):
                    #print("quay nghich")
                    # tính động học
                    # cho trục A quay thêm 1 góc tương đương gain_rotary_encoder xung để có vị trí new_pos_A
                    pulse_A_teach = Teach_mode.gain_rotary_encoder
                    new_pos_A = self.pos_A + float(pulse_A_teach*self.gear_ratio_A)
                    if(new_pos_A > 90): # nếu new_pos_A >= 90 deg thì không quay trục A mà chạy trục Z gain_rotary_encoder xung
                        pulse_Z_teach = pulse_A_teach
                        self.pulse_teach_packet = [0,0,pulse_Z_teach,0,0,0]
                    else: # nếu new_pos_A < 90 deg thì quay trục A và Y sao cho Yspray không đổi
                        new_pos_Y = Yspray_expect - self.spray_axis*math.cos((new_pos_A*math.pi)/180)
                        pulse_Y_teach = int((new_pos_Y - self.pos_Y)/self.gear_ratio_Y) # số xung trục quay Y cần quay
                        self.pulse_teach_packet = [0,pulse_Y_teach,0,pulse_A_teach,0,0]

                if self.rotary_encoder != self.pre_rotary_encoder:
                    self.pre_rotary_encoder = self.rotary_encoder
                    Run.send_to_execute_board(self.pulse_teach_packet)
                    while True:
                        new_position_done_slave_02 = master.execute(SLAVE_02, cst.READ_COILS, self.EXECUTE_PULSE_DONE, 1)
                        new_position_done_slave_03 = master.execute(SLAVE_03, cst.READ_COILS, self.EXECUTE_PULSE_DONE, 1)
                        self.Read_pulse_PWM_from_slaves()
                        if new_position_done_slave_02[0] == 1 and new_position_done_slave_03[0] == 1: 
                           break  # thoat khỏi vong lặp while
                # nếu disable teach mode thì thoát khỏi 
                if (self.monitor_off == True):
                    self.rotary_encoder = 0
                    self.pre_rotary_encoder = 0
                    break
        else: pass
# thực hiện chạy động cơ và giám sát số xung phát ra trong chế độ teach mode
    def Monitor_pulse_in_teach_mode(self):
        Teach_mode.teach_axis = -1
        while True:
            self.pulse_teach_packet = [0,0,0,0,0,0]
            state_runing = False
            self.rotary_encoder = self.Read_rotary_encoder()
            self.Read_pulse_PWM_from_slaves()
            self.Kinematics_Zaxis()
            if (self.rotary_encoder > self.pre_rotary_encoder):
                # gửi command quay chiều thuận trục được chọn
                pulse_teach = -1*Teach_mode.gain_rotary_encoder
                if Teach_mode.teach_axis == Teach_mode.TEACH_X_AXIS:
                    new_pos_X = self.pos_X + (pulse_teach*self.gear_ratio_X)
                    if new_pos_X < 0:
                        self.pre_rotary_encoder = self.rotary_encoder
                        pass
                    else:
                        self.pulse_teach_packet[Teach_mode.teach_axis] = pulse_teach
                if Teach_mode.teach_axis == Teach_mode.TEACH_Y_AXIS:
                    new_pos_Y = self.pos_Y + (pulse_teach*self.gear_ratio_Y)
                    if new_pos_Y < 0:
                        self.pre_rotary_encoder = self.rotary_encoder
                        pass
                    else:
                        self.pulse_teach_packet[Teach_mode.teach_axis] = pulse_teach
                if Teach_mode.teach_axis == Teach_mode.TEACH_B_AXIS:
                    new_pos_B = self.pos_B + (pulse_teach*self.gear_ratio_B)
                    self.pulse_teach_packet[Teach_mode.teach_axis] = pulse_teach

                if Teach_mode.teach_axis == Teach_mode.TEACH_C_AXIS:
                    new_pos_C = self.pos_C + (pulse_teach*self.gear_ratio_C)
                    self.pulse_teach_packet[Teach_mode.teach_axis] = pulse_teach
                
            if (self.rotary_encoder < self.pre_rotary_encoder):
                # gửi command quay chiều nghịch trục được chọn                
                self.pulse_teach_packet[Teach_mode.teach_axis] = Teach_mode.gain_rotary_encoder

            if (self.rotary_encoder != self.pre_rotary_encoder):
                self.pre_rotary_encoder = self.rotary_encoder
                Run.send_to_execute_board(self.pulse_teach_packet)
                state_runing = True
                                    
            while state_runing:
                # Đọc trạng thái phát xung đã hoàn tất chưa
                new_position_done_slave_02 = master.execute(SLAVE_02, cst.READ_COILS, self.EXECUTE_PULSE_DONE, 1)
                new_position_done_slave_03 = master.execute(SLAVE_03, cst.READ_COILS, self.EXECUTE_PULSE_DONE, 1)
                # Đọc giá trị thanh ghi lưu giá trị xung đang phát ra
                self.Read_pulse_PWM_from_slaves()
                if new_position_done_slave_02[0] == 1 and new_position_done_slave_03[0] == 1: 
                    break  # thoat khỏi vong lặp while

            if (self.monitor_off == True):
                self.monitor_off = False
                self.rotary_encoder = 0
                self.pre_rotary_encoder = 0
                Teach_mode.teach_axis = -1
                break

# phát lệnh cho các động cơ chạy về điểm zero: điểm gốc máy so với vị trí hiện tại của tay máy
    def Go_to_home(self):
        print("Go to Home")
        Show_Screen.Teach_option.config(state = DISABLED)
        Show_Screen.Home_option.config(state = DISABLED)
        Show_Screen.Manual_option.config(state = DISABLED)
        Show_Screen.Load_file.config(state = DISABLED)
        self.go_home_state = True
        Run.send_to_execute_board(self.pulse_to_home)
        while True:
            # Đọc trạng thái phát xung đã hoàn tất chưa
            Go_to_Home_done_slave_02 = master.execute(SLAVE_02, cst.READ_COILS, self.EXECUTE_PULSE_DONE, 1)
            Go_to_Home_done_slave_03 = master.execute(SLAVE_03, cst.READ_COILS, self.EXECUTE_PULSE_DONE, 1)
            # Đọc giá trị thanh ghi lưu giá trị xung đang phát ra
            self.Read_pulse_PWM_from_slaves()
            if (Go_to_Home_done_slave_02[0] == 1) and (Go_to_Home_done_slave_03[0] == 1): 
                Show_Screen.Teach_option.config(state = NORMAL)
                Show_Screen.Home_option.config(state = NORMAL)
                Show_Screen.Manual_option.config(state = NORMAL)
                Show_Screen.Load_file.config(state = NORMAL)
                self.go_home_state = False
                break  # thoat khỏi vong lặp while

    def Cancel(self):
        self.home = 1

    def Read_rotary_encoder(self):
        # Đọc giá trị thanh ghi rotary encoder ở địa chỉ bắt đầu từ 20, đọc 2 giá trị 16 bit
        rotaty_encoder_packet = master.execute(SLAVE_02, cst.READ_HOLDING_REGISTERS, self.ROTARY_ENCODER_MODBUS_ADDR , 2)
        counter = ((rotaty_encoder_packet[1] & 65535) | (rotaty_encoder_packet[0] << 16))
        counter = self.check_negative_num(counter)
        return counter

    def Read_pulse_PWM_from_slaves(self):
        # Đọc giá trị xung của tất cả động cơ 
        try:
           
            # Đọc giá trị thanh ghi PWM trục X ở địa chỉ bắt đầu từ 0, đọc 2 giá trị 16 bit
            pulse_Xaxis_packet = master.execute(SLAVE_02, cst.READ_HOLDING_REGISTERS, self.PWM_VALUE_X_AXIS_MODBUS_ADDR, 2)
            pulse_Xaxis = ((pulse_Xaxis_packet[1] & 65535) | (pulse_Xaxis_packet[0] << 16))
            # Đọc giá trị thanh ghi PWM trục X ở địa chỉ bắt đầu từ 2, đọc 2 giá trị 16 bit
            pulse_Yaxis_packet = master.execute(SLAVE_02, cst.READ_HOLDING_REGISTERS, self.PWM_VALUE_Y_AXIS_MODBUS_ADDR, 2)
            pulse_Yaxis = ((pulse_Yaxis_packet[1] & 65535) | (pulse_Yaxis_packet[0] << 16))
            # Đọc giá trị thanh ghi PWM trục X ở địa chỉ bắt đầu từ 4, đọc 2 giá trị 16 bit
            pulse_Zaxis_packet = master.execute(SLAVE_02, cst.READ_HOLDING_REGISTERS, self.PWM_VALUE_Z_AXIS_MODBUS_ADDR, 2)
            pulse_Zaxis = ((pulse_Zaxis_packet[1] & 65535) | (pulse_Zaxis_packet[0] << 16))
            # Đọc giá trị thanh ghi PWM trục X ở địa chỉ bắt đầu từ 6, đọc 2 giá trị 16 bit
            pulse_Aaxis_packet = master.execute(SLAVE_02, cst.READ_HOLDING_REGISTERS, self.PWM_VALUE_A_AXIS_MODBUS_ADDR, 2)
            pulse_Aaxis = ((pulse_Aaxis_packet[1] & 65535) | (pulse_Aaxis_packet[0] << 16))
            # Đọc giá trị thanh ghi PWM trục X ở địa chỉ bắt đầu từ 8, đọc 2 giá trị 16 bit
            pulse_Baxis_packet = master.execute(SLAVE_03, cst.READ_HOLDING_REGISTERS, self.PWM_VALUE_SPRAY_AXIS_MODBUS_ADDR, 2)
            pulse_Baxis = ((pulse_Baxis_packet[1] & 65535) | (pulse_Baxis_packet[0] << 16))
            # Đọc giá trị thanh ghi PWM trục X ở địa chỉ bắt đầu từ 10, đọc 2 giá trị 16 bit
            pulse_Caxis_packet = master.execute(SLAVE_03, cst.READ_HOLDING_REGISTERS, self.PWM_VALUE_CHAIR_AXIS_MODBUS_ADDR, 2)
            pulse_Caxis = ((pulse_Caxis_packet[1] & 65535) | (pulse_Caxis_packet[0] << 16))            
            # kiểm tra giá trị âm
            self.pwm_value_x_axis = self.check_negative_num(pulse_Xaxis)
            self.pwm_value_y_axis = self.check_negative_num(pulse_Yaxis)
            self.pwm_value_z_axis = self.check_negative_num(pulse_Zaxis)
            self.pwm_value_a_axis = self.check_negative_num(pulse_Aaxis)
            self.pwm_value_b_axis = self.check_negative_num(pulse_Baxis)
            self.pwm_value_c_axis = self.check_negative_num(pulse_Caxis)
            
            # lưu giá trị xung cần chạy để về vị trí zero point ở thời điểm hiện tại
            self.pulse_to_home = [-(self.pwm_value_x_axis),-(self.pwm_value_y_axis),-(self.pwm_value_z_axis),-(self.pwm_value_a_axis),-(self.pwm_value_b_axis),-(self.pwm_value_c_axis)]
            # lưu giá trị xung đã chạy được ở thời điểm hiện tại
            self.current_pulse = [self.pwm_value_x_axis,self.pwm_value_y_axis,self.pwm_value_z_axis,self.pwm_value_a_axis,self.pwm_value_b_axis,self.pwm_value_c_axis]
            self.Show_Position()
        except Exception as e:
            messagebox.showinfo("Please check COM communication again")
            print(str(e))

    def check_negative_num(self, x):
        if ((x & (1<<31)) != 0):
            # This is negative num
            a = -(0xFFFFFFFF - x +1)
        else:
            a = x
        return a

    def Show_Position(self):
        # cài đặt microstep trục X = 25600 pulse/rev; gear ratio = 1:5 -> cần 128000 xung - quay bánh răng 360 độ ( bánh răng D80 mm = 80*Pi mm)
        self.pos_X = float(self.pwm_value_x_axis*self.gear_ratio_X)
        # cài đặt microstep trục Y = 25600 pulse/rev; gear ratio = 1:5 -> cần 128000 xung - quay bánh răng 360 độ ( bánh răng D80 mm = 80*Pi mm)
        self.pos_Y = float(self.pwm_value_y_axis*self.gear_ratio_Y)
        # cài đặt microstep trục Z = 25600 pulse/rev; gear ratio = 1:5 -> cần 128000 xung - quay bánh răng 360 độ ( bánh răng D80 mm = 80*Pi mm)
        self.pos_Z = float(self.pwm_value_z_axis*self.gear_ratio_Z)
        # cài đặt microstep trục A = 25600 pulse/rev; gear ratio = 1:5 -> cần 128000 xung - quay bánh răng 360 độ 
        self.pos_A = float(self.pwm_value_a_axis*self.gear_ratio_A)
        # cài đặt microstep trục B = 25600 pulse/rev; gear ratio = 1:1 -> cần 25600 xung - quay bánh răng 360 độ
        self.pos_B = float(self.pwm_value_b_axis*self.gear_ratio_B)
        # cài đặt microstep trục C = 25600 pulse/rev; gear ratio = 1:1 -> cần 25600 xung - quay bánh răng 360 độ
        self.pos_C = float(self.pwm_value_c_axis*self.gear_ratio_C)
        # vị trí Y,Z của trục súng sơn theo phương trình động học
        self.pos_Yspray = self.pos_Y + self.spray_axis*math.cos((self.pos_A*math.pi)/180)
        self.pos_Zspray = self.pos_Z + self.spray_axis*math.sin((self.pos_A*math.pi)/180)

        self.var1.set(str(round(self.pos_X,3))+ " mm")
        self.var2.set(str(round(self.pos_Y,3))+ " mm")
        self.var3.set(str(round(self.pos_Z,3))+ " mm")
        self.var4.set(str(round(self.pos_A,3))+ " deg")
        self.var5.set(str(round(self.pos_B,3))+ " deg")
        self.var6.set(str(round(self.pos_C,3))+ " deg")

        self.var20.set(str(round((self.pos_Yspray - self.spray_axis),3)) + " mm")
        self.var21.set(str(round(self.pos_Zspray,3)) + " mm")

        Show_Screen.label_X.update()
        Show_Screen.label_Y.update()
        Show_Screen.label_Z.update()
        Show_Screen.label_A.update()
        Show_Screen.label_B.update()
        Show_Screen.label_C.update()
# tính tốc độ của 6 trục ứng với giá trị xung tương ứng
    def Calculate_speed(self,pwm_x,pwm_y,pwm_z,pwm_a,pwm_b,pwm_c):
        speed_axis = [0,0,0,0,0,0] # tốc độ 6 trục
        velocity = [0,0,0,0,0,0]   # vận tốc 6 trục
        ratio = [0,0,0,0,0,0]    # tỉ lệ 6 trục so với trục lớn nhất
        if ((Teach_mode.teach_state == True) or (self.go_home_state == True)):
            Fspray = 80
        else:
            Fspray = Show_Screen.speed_scale.get() # tốc độ sơn, đơn vị mm/s
            #if Fspray > 300: Fspray = 300 # giới hạn tốc độ 

        self.index = self.spray_axis*math.sin((self.gear_ratio_A*math.pi)/180)
        # tính giá trị xung lớn nhất trong các trục
        pwm_value_max = max(abs(pwm_x),abs(pwm_y),abs(pwm_z),abs(pwm_a),abs(pwm_b),abs(pwm_c))
        # tính tỉ lệ giá trị xung từng trục so với giá trị xung lớn nhất
       # print("giá trị pwm_value_max: ",pwm_value_max)
        #print("giá trị pwm các trục: ",pwm_x,pwm_y,pwm_z,pwm_a)
        if pwm_value_max != 0:
            ratio[0] = abs(pwm_x)/pwm_value_max
            ratio[1] = abs(pwm_y)/pwm_value_max
            ratio[2] = abs(pwm_z)/pwm_value_max
            ratio[3] = abs(pwm_a)/pwm_value_max
            ratio[4] = abs(pwm_b)/pwm_value_max
            ratio[5] = abs(pwm_c)/pwm_value_max
            # nếu trường hợp chỉ có trục B hoặc C quay, các trục còn lại đứng yên
            if (ratio[0] == 0 and ratio[1] == 0 and ratio[2] == 0 and ratio[3] == 0):
                max_speed = 8000
            # tính bình phương của giá trị Fspray
            else:
                Fspray_pow2 = math.pow(Fspray,2) 
                index_Xpow2 = math.pow((ratio[0]*self.gear_ratio_X),2)
                index_Ypow2 = math.pow((ratio[1]*self.gear_ratio_Y),2)
                index_Zpow2 = math.pow((ratio[2]*self.gear_ratio_Z),2) + 2*ratio[2]*ratio[3]*self.gear_ratio_Z*self.index + math.pow((ratio[3]*self.index),2)
                if (index_Xpow2 != 0 or index_Ypow2 != 0 or index_Zpow2 != 0):
                    max_speed = int(math.sqrt(Fspray_pow2/(index_Xpow2 + index_Ypow2 + index_Zpow2)))
                else:
                    max_speed = 15000
                print("max_speed: ",max_speed)
                if max_speed > 60000: 
                    max_speed = 50000
                    print("quá tốc độ")
        # trường hợp tất cả các trục đều không quay
        else:
            ratio = [0,0,0,0,0,0]
            max_speed = 0
        # tính tần số phát xung cho các trục (xung/s)
        speed_axis[0] = ratio[0]*max_speed
        speed_axis[1] = ratio[1]*max_speed
        speed_axis[2] = ratio[2]*max_speed
        speed_axis[3] = ratio[3]*max_speed
        speed_axis[4] = ratio[4]*max_speed
        speed_axis[5] = ratio[5]*max_speed
       
        # tính tốc độ trục X,Y,Z của đầu súng sơn theo đơn vị mm/s
        velocity[0] = int(speed_axis[0])*self.gear_ratio_X
        velocity[1] = int(speed_axis[1])*self.gear_ratio_Y
        velocity[2] = int(speed_axis[2])*self.gear_ratio_Z + int(speed_axis[3])*self.index
        self.speed_XYZ_spray = math.sqrt(math.pow(velocity[0],2) + math.pow(velocity[1],2) + math.pow(velocity[2],2))
        #print("X: " + str(round(velocity[0]))+ " mm/s "+ "Y: " + str(round(velocity[1]))+ " mm/s " + "Z: " + str(round(velocity[2])) + " mm/s")
        print("F spray = " + str(round(self.speed_XYZ_spray)) + " mm/s")
        return speed_axis

#========================================================================
class Button_Active:
    def Disable_options_button():
        Show_Screen.Teach_option.config(state = DISABLED)
        Show_Screen.Home_option.config(state = DISABLED)
        Show_Screen.Manual_option.config(state = DISABLED)
        Show_Screen.Load_file.config(state = DISABLED)
    def Enable_options_button():
        Show_Screen.Teach_option.config(state = NORMAL)
        Show_Screen.Home_option.config(state = NORMAL)
        Show_Screen.Manual_option.config(state = NORMAL)
        Show_Screen.Load_file.config(state = NORMAL)

#========================================================================
class Teach_mode_class():

    def __init__(self):
        self.TEACH_X_AXIS_MODBUS_ADDR = 0
        self.TEACH_Y_AXIS_MODBUS_ADDR = 1
        self.TEACH_Z_AXIS_MODBUS_ADDR = 2
        self.TEACH_A_AXIS_MODBUS_ADDR = 3
        self.TEACH_SPRAY_AXIS_MODBUS_ADDR = 4
        self.TEACH_CHAIR_AXIS_MODBUS_ADDR = 5

        self.X1_RES_MODBUS_ADDR = 9
        self.X10_RES_MODBUS_ADDR = 10
        self.X100_RES_MODBUS_ADDR = 11
        self.X1000_RES_MODBUS_ADDR = 12

        self.DISABLE_ROTARY_ENCODER_ADDR = 13
        self.ENABLE_ROTARY_ENCODER_ADDR = 14

        self.SET_ZERO_POSITION_ADDR = 16

        self.SPRAY_ON_MODBUS_ADDR = 6
        self.teach_state = False
        self.Save_point = False
        self.spray_var = StringVar()
        self.spray_var.set('0') # súng sơn: 0 - off; 1 - on
        self.gain_rotary_encoder = 100 # giá trị xung mặc định khi quay rotary encoder

        self.counter_line = 0

        self.teach_axis = -1   # biến lựa chọn trục cần chạy trong teach mode
        self.TEACH_X_AXIS = 0  # teach trục X
        self.TEACH_Y_AXIS = 1  # teach truc Y
        self.TEACH_Z_AXIS = 2  # teach truc Z
        self.TEACH_A_AXIS = 3  # teach trục A
        self.TEACH_B_AXIS = 4  # teach trục B
        self.TEACH_C_AXIS = 5  # teach trục C

    def Enable_teach_options(self):
        print("enable teach options")
        try:
            Show_Screen.Disable_teach_mode.config(state = NORMAL)
            Show_Screen.Set_teach_point.config(state = NORMAL)
            Show_Screen.X_button.config(state = NORMAL)
            Show_Screen.Y_button.config(state = NORMAL)
            Show_Screen.Z_button.config(state = NORMAL)
            #Show_Screen.A_button.config(state = NORMAL)
            Show_Screen.B_button.config(state = NORMAL)
            Show_Screen.C_button.config(state = NORMAL)
            Show_Screen.spray_on.config(state = NORMAL)
            Show_Screen.spray_off.config(state = NORMAL)

            Show_Screen.save_file_button.config(state = NORMAL)
            Show_Screen.set_zero_point.config(state = NORMAL)

            Show_Screen.X1_button.config(state = NORMAL)
            Show_Screen.X10_button.config(state = NORMAL)
            Show_Screen.X100_button.config(state = NORMAL)
            Show_Screen.X1000_button.config(state = NORMAL)

            Show_Screen.Teach_option.config(state = DISABLED)
            Show_Screen.Home_option.config(state = DISABLED)
            Show_Screen.Manual_option.config(state = DISABLED)
            Show_Screen.Load_file.config(state = DISABLED)

            self.gain_rotary_encoder = 100 # giá trị xung mặc định khi quay rotary encoder
            self.teach_state = True
            # xóa nội dung trong text_box
            Show_Screen.Show_content.delete('1.0','end')
            Show_Screen.Show_content.config(state = NORMAL)
            # bật tay quay rotary encoder
            master.execute(SLAVE_02, cst.WRITE_SINGLE_COIL, self.ENABLE_ROTARY_ENCODER_ADDR, output_value = CHOOSE)
            # bật monitor số xung
            Monitor_mode.Monitor_pulse_in_teach_mode()
        except Exception as e:
            print(str(e))
            return

    def Disable_teach_options(self):
        print("disable teach options")
        Show_Screen.Disable_teach_mode.config(state = DISABLED)
        Show_Screen.Set_teach_point.config(state = DISABLED)

        Show_Screen.X_button.config(state = DISABLED, bg = "gray")
        Show_Screen.Y_button.config(state = DISABLED, bg = "gray")
        Show_Screen.Z_button.config(state = DISABLED, bg = "gray")
        Show_Screen.A_button.config(state = DISABLED, bg = "gray")
        Show_Screen.B_button.config(state = DISABLED, bg = "gray")
        Show_Screen.C_button.config(state = DISABLED, bg = "gray")
        Show_Screen.spray_on.config(state = DISABLED,bg = "gray")
        Show_Screen.spray_off.config(state = DISABLED,bg = "gray")
        Show_Screen.save_file_button.config(state = DISABLED)
        Show_Screen.set_zero_point.config(state = DISABLED)

        Show_Screen.X1_button.config(state = DISABLED, bg = "gray")
        Show_Screen.X10_button.config(state = DISABLED, bg = "gray")
        Show_Screen.X100_button.config(state = DISABLED, bg = "gray")
        Show_Screen.X1000_button.config(state = DISABLED, bg = "gray")

        Show_Screen.Teach_option.config(state = NORMAL)
        Show_Screen.Home_option.config(state = NORMAL)
        Show_Screen.Manual_option.config(state = NORMAL)
        Show_Screen.Load_file.config(state = NORMAL)

        self.teach_state = False
        self.Spray_off()
        # xóa nội dung trong text_box, trả giá trị đếm số dòng về 0
        Show_Screen.Show_content.delete('1.0','end')
        Show_Screen.Show_content.config(state = DISABLED)
        self.counter_line = 0
        # tắt tay quay rotary encoder
        master.execute(SLAVE_02, cst.WRITE_SINGLE_COIL, self.DISABLE_ROTARY_ENCODER_ADDR, output_value = CHOOSE)
        # tắt monitor xung
        Monitor_mode.monitor_off = True

    def Show_point_to_textbox(self):
        # Lấy các giá trị của các trục tay máy để hiện thị lên Show_content
        self.counter_line += 1
        show_line = (str(self.counter_line) + 'X'+str(round(Monitor_mode.pos_X,3)) +'Y' + str(round(Monitor_mode.pos_Y,3)) + 
                    'Z'+ str(round(Monitor_mode.pos_Z,3))+ 'A' + str(round(Monitor_mode.pos_A,3)) + 'B' + str(round(Monitor_mode.pos_B,3)) 
                    + 'C'+ str(round(Monitor_mode.pos_C,3)) + 'S' + self.spray_var.get() + '\n')
        Show_Screen.Show_content.insert(END,show_line) 
        Show_Screen.Show_content.yview(END)
        #Drawing.Show_position(round(Monitor_mode.pos_X,3),round(Monitor_mode.pos_Y,3),round(Monitor_mode.pos_Z,3))

    def Teach_X_Axis(self):
        Show_Screen.X_button.config(bg = "green")
        Show_Screen.Y_button.config(bg = "gray")
        Show_Screen.Z_button.config(bg = "gray")
        Show_Screen.A_button.config(bg = "gray")
        Show_Screen.B_button.config(bg = "gray")
        Show_Screen.C_button.config(bg = "gray")
        self.teach_axis = self.TEACH_X_AXIS
        print("chọn trục X")

    def Teach_Y_Axis(self):
        Show_Screen.X_button.config(bg = "gray")
        Show_Screen.Y_button.config(bg = "green")
        Show_Screen.Z_button.config(bg = "gray")
        Show_Screen.A_button.config(bg = "gray")
        Show_Screen.B_button.config(bg = "gray")
        Show_Screen.C_button.config(bg = "gray")
        self.teach_axis = self.TEACH_Y_AXIS
        print("chọn trục Y")

    def Teach_Z_Axis(self):
        Show_Screen.X_button.config(bg = "gray")
        Show_Screen.Y_button.config(bg = "gray")
        Show_Screen.Z_button.config(bg = "green")
        Show_Screen.A_button.config(bg = "gray")
        Show_Screen.B_button.config(bg = "gray")
        Show_Screen.C_button.config(bg = "gray")
        self.teach_axis = self.TEACH_Z_AXIS
        print("chọn trục Z")

    def Teach_A_Axis(self):
        Show_Screen.X_button.config(bg = "gray")
        Show_Screen.Y_button.config(bg = "gray")
        Show_Screen.Z_button.config(bg = "gray")
        Show_Screen.A_button.config(bg = "green")
        Show_Screen.B_button.config(bg = "gray")
        Show_Screen.C_button.config(bg = "gray")
        self.teach_axis = self.TEACH_A_AXIS
        print("chọn trục A")

    def Teach_B_Axis(self):
        Show_Screen.X_button.config(bg = "gray")
        Show_Screen.Y_button.config(bg = "gray")
        Show_Screen.Z_button.config(bg = "gray")
        Show_Screen.A_button.config(bg = "gray")
        Show_Screen.B_button.config(bg = "green")
        Show_Screen.C_button.config(bg = "gray")
        self.teach_axis = self.TEACH_B_AXIS
        print("chọn trục súng sơn")

    def Teach_C_Axis(self):
        Show_Screen.X_button.config(bg = "gray")
        Show_Screen.Y_button.config(bg = "gray")
        Show_Screen.Z_button.config(bg = "gray")
        Show_Screen.A_button.config(bg = "gray")
        Show_Screen.B_button.config(bg = "gray")
        Show_Screen.C_button.config(bg = "green")
        self.teach_axis = self.TEACH_C_AXIS
        print("chọn trục ghế")
    
    def X1_resolution(self):
        Show_Screen.X1_button.config(bg = "green")
        Show_Screen.X10_button.config(bg = "gray")
        Show_Screen.X100_button.config(bg = "gray")
        Show_Screen.X1000_button.config(bg = "gray") 
        self.gain_rotary_encoder = 1
        print("chọn độ phân giải x1")
    
    def X10_resolution(self):
        Show_Screen.X1_button.config(bg = "gray")
        Show_Screen.X10_button.config(bg = "green")
        Show_Screen.X100_button.config(bg = "gray")
        Show_Screen.X1000_button.config(bg = "gray") 
        self.gain_rotary_encoder = 10
        print("chọn độ phân giải x10")

    def X100_resolution(self):
        Show_Screen.X1_button.config(bg = "gray")
        Show_Screen.X10_button.config(bg = "gray")
        Show_Screen.X100_button.config(bg = "green")
        Show_Screen.X1000_button.config(bg = "gray")
        self.gain_rotary_encoder = 100
        print("chọn độ phân giải x100")
    
    def X1000_resolution(self):
        Show_Screen.X1_button.config(bg = "gray")
        Show_Screen.X10_button.config(bg = "gray")
        Show_Screen.X100_button.config(bg = "gray")
        Show_Screen.X1000_button.config(bg = "green")
        self.gain_rotary_encoder = 1000
        print("chọn độ phân giải x1000")

    def Spray_on(self):
        self.spray_var.set('1')
        Run.command_run_spray(int(self.spray_var.get()))
        print("bật phun sơn")

    def Spray_off(self):
        self.spray_var.set('0')
        Run.command_run_spray(int(self.spray_var.get()))
        print("tắt phun sơn")

    def Save_file(self):
        print('Lưu file vào máy')
        Work_file.save_file()

    def Set_zero_position(self):
        print('Set 0 các trục x,y,z,a,b,c')
        master.execute(SLAVE_02, cst.WRITE_SINGLE_COIL, self.SET_ZERO_POSITION_ADDR, output_value = CHOOSE)
        master.execute(SLAVE_03, cst.WRITE_SINGLE_COIL, self.SET_ZERO_POSITION_ADDR, output_value = CHOOSE)
#========================================================================  
class Com_box():
    def __init__(self):
        self.comports = Listbox()
        self.baudrate = Listbox()
        self.choose_COM = Combobox()
        self.choose_BAUD = Combobox()
        self.Connect = Button()
        self.Disconnect = Button()

    def Show_comunication_box(self):
        Frame2 = LabelFrame(root, text="KẾT NỐI ROBOT SƠN")
        Frame2.place(x = 10, y = 650)
        bg_frame2 = Canvas(Frame2, bg="green", height=120, width=150, bd = 1)
        bg_frame2.pack(side = LEFT)
        #========================================================================
        #========================================================================
        Label(Frame2,text = 'COM',fg ='black', justify = LEFT).place(x=10, y=20)
        Label(Frame2,text = 'BAUD',fg ='black', justify = LEFT).place(x=10, y=50)

        self.comports = ['COM1','COM2','COM3','COM4','COM5','COM6','COM7','COM8','COM9']
        self.baudrate = ['9600','19200','115200']
        self.choose_COM = Combobox(Frame2, value = self.comports, width = 10,state='readonly')
        self.choose_COM.place(x=50, y=20)
        self.choose_BAUD = Combobox(Frame2, value = self.baudrate, width = 10,state='readonly')
        self.choose_BAUD.place(x=50, y =50)
        self.Connect = Button(Frame2, text ='Connect',command = Send_to_Serial.Init_Serial)
        self.Connect.place(x = 10, y = 80)
        self.Disconnect = Button(Frame2, text ='Disconnect',command = Send_to_Serial.Disconnect_Serial, state=DISABLED)
        self.Disconnect.place(x = 75, y = 80)
#==============================================================================================================
class Run_auto():
    def __init__(self):
        self.SPRAY_ON_MODBUS_ADDR = 6
        self.POINT2POINT_MODBUS_ADDR = 7
        self.PAUSE_MOTOR_MODBUS_ADDR = 8

        self.content = StringVar()
        self.Recognize_command = False
        self.check_end_file = True
        self.Xpwm = self.Ypwm = self.Zpwm = self.Apwm = self.Bpwm = self.Cpwm = 0
        self.so_xung = [0,0,0,0,0,0]
        self.sum_xung_le = [0,0,0,0,0,0]
        self.xung_nguyen = [0,0,0,0,0,0]
        self.X_string = StringVar()
        self.Y_string = StringVar()
        self.Z_string = StringVar()
        self.A_string = StringVar()
        self.B_string = StringVar()
        self.C_string = StringVar()
        self.S_switch = '0'
        self.dx0 = self.dy0 = self.dz0 = self.da0 = self.db0 = self.dc0 = 0
        self.pause_on = 0
        self.stop_on = False
        self.pulse_index = [0,0,0,0,0,0]
        self.state_spray = 0

    def activate_run_mode(self):
        try:
            position = Work_file.file.seek(0,0) # Di chuyen con tro vi tri read file ve vi tri begining

            Show_Screen.Teach_option.config(state = DISABLED)
            Show_Screen.Home_option.config(state = DISABLED)
            Show_Screen.Manual_option.config(state = DISABLED)
            Show_Screen.Load_file.config(state = DISABLED)
            Show_Screen.Auto_run_button.config(state = DISABLED)
            Show_Screen.Stop_button.config(state = NORMAL)
            self.pause_on = 0

            for str_content in Work_file.file:
                print ('========================================================================')
                self.content = str_content.replace(" ", "") # Bo ky tu khoang trang trong chuoi
                print(self.content)
                self.content = self.content.upper()     # chuyen doi chuoi thanh chu IN HOA
                self.Monitor_str_content(self.content)  # hiện thị từng dòng trong file
                self.Recognize_command_syntax(self.content)
                if self.Recognize_command:
                    # tách số của các trục
                    self.separate_string(self.content)
                    # tính toán khoảng cách cần tịnh tiến
                    self.calculate_delta(self.X_string,self.Y_string,self.Z_string,self.A_string,self.B_string,self.C_string)
                    # tính toán số xung tịnh tiến
                    self.calculate_pulse(self.Xpwm,self.Ypwm,self.Zpwm,self.Apwm,self.Bpwm,self.Cpwm)
                    # gửi tín hiệu xung và tốc độ tới board execute
                    self.send_to_execute_board(self.xung_nguyen)
                    while True:
                        Point2point_done_slave_02 = master.execute(SLAVE_02, cst.READ_COILS, Monitor_mode.EXECUTE_PULSE_DONE, 1)
                        Point2point_done_slave_03 = master.execute(SLAVE_03, cst.READ_COILS, Monitor_mode.EXECUTE_PULSE_DONE, 1)
                        Monitor_mode.Read_pulse_PWM_from_slaves()

                        if Point2point_done_slave_02[0] == 1 and Point2point_done_slave_03[0] == 1:
                            break # nếu chạy đủ xung thì thoát khỏi while
                        if self.pause_on == 1: # dừng motor
                                master.execute(SLAVE_02, cst.WRITE_SINGLE_COIL, self.PAUSE_MOTOR_MODBUS_ADDR, output_value = CHOOSE)
                                master.execute(SLAVE_03, cst.WRITE_SINGLE_COIL, self.PAUSE_MOTOR_MODBUS_ADDR, output_value = CHOOSE)
                        if self.pause_on == 2: # tiếp tục chạy
                                self.command_run_point2point()
                                self.pause_on = 0
                
        except Exception as e:
                print(str(e))
                messagebox.showinfo("Run Auto", "Error: choose file again")
                return
        finally:
            # đưa tay máy về vị trí zero point sau khi đã chạy xong file
            print ('========================================================================')
            Monitor_mode.Go_to_home()
            self.re_init()
            print("--------------------------------------------------------------------------")
            print("END")

    def disable_run_mode(self):
       
        Show_Screen.Teach_option.config(state = NORMAL)
        Show_Screen.Home_option.config(state = NORMAL)
        Show_Screen.Manual_option.config(state = NORMAL)
        Show_Screen.Load_file.config(state = NORMAL)
        Show_Screen.Auto_run_button.config(state = NORMAL)
        Show_Screen.Stop_button.config(state = DISABLED)

        try:
            Work_file.file.close()
        except:
            return

    def separate_string(self, string):
        Range_char = ['X','Y','Z','A','B','C','S','\n']
        try:
            index = string.find('X')
            counter_line = string[0:index]
            string = string[index:]
            if string[0] == 'X':
                for char in string[1:]:
                    if char in Range_char[0:]:
                         index = string.find(char)
                         self.X_string = string[1:index]
                         string = string[index:]
                         break  # Run if function only 1 time
            if string[0] == 'Y':
                for char in string[1:]:
                    if char in Range_char[0:]:
                         index = string.find(char)
                         self.Y_string = string[1:index]
                         string = string[index:]
                         break  # Run if function only 1 time
            if string[0] == 'Z':
                for char in string[1:]:
                    if char in Range_char[0:]:
                         index = string.find(char)
                         self.Z_string = string[1:index]
                         string = string[index:]
                         break  # Run if function only 1 time
            if string[0] == 'A':
                for char in string[1:]:
                    if char in Range_char[0:]:
                         index = string.find(char)
                         self.A_string = string[1:index]
                         string = string[index:]
                         break  # Run if function only 1 time
            if string[0] == 'B':
                for char in string[1:]:
                    if char in Range_char[0:]:
                         index = string.find(char)
                         self.B_string = string[1:index]
                         string = string[index:]
                         break  # Run if function only 1 time
            if string[0] == 'C':
                for char in string[1:]:
                    if char in Range_char[0:]:
                         index = string.find(char)
                         self.C_string = string[1:index]
                         string = string[index:]
                         break  # Run if function only 1 time
            if string[0] == 'S':
                for char in string[1:]:
                    if char in Range_char[0:]:
                         index = string.find(char)
                         S_string = string[1:index]
                         self.S_switch = str(S_string)
                         string = string[index:]
                         break  # Run 'if function' only 1 time
        except Exception as e:
            print(str(e))
            pass

    def calculate_delta(self,x,y,z,a,b,c):
    # tính giá trị xung tịnh tiến
        print('Gia tri X,Y,Z,A,B,C là:',x,y,z,a,b,c)
        deltaX = float(x) - self.dx0
        deltaY = float(y) - self.dy0
        deltaZ = float(z) - self.dz0
        deltaA = float(a) - self.da0
        deltaB = float(b) - self.db0
        deltaC = float(c) - self.dc0

        self.dx0 = float(x)
        self.dy0 = float(y)
        self.dz0 = float(z)
        self.da0 = float(a)
        self.db0 = float(b)
        self.dc0 = float(c)

        self.Xpwm = float(deltaX)/Monitor_mode.gear_ratio_X
        self.Ypwm = float(deltaY)/Monitor_mode.gear_ratio_Y
        self.Zpwm = float(deltaZ)/Monitor_mode.gear_ratio_Z
        self.Apwm = float(deltaA)/Monitor_mode.gear_ratio_A
        self.Bpwm = float(deltaB)/Monitor_mode.gear_ratio_B
        self.Cpwm = float(deltaC)/Monitor_mode.gear_ratio_C

        print('Gia tri delta cua X,Y,Z,A,B,C là:',round(deltaX,3),round(deltaY,3),round(deltaZ,3),round(deltaA,3),round(deltaB,3),round(deltaC,3))
    def calculate_pulse(self,x,y,z,a,b,c):
    # tách xung nguyên và xung lẻ
        #xung_le = [0,0,0,0,0,0]
        print ('===> Gia tri xung x,y,z,a,b,c chua calib lan luot la: ',round(x,3),' ',round(y,3),' ',round(z,3),' ',round(a,3),' ',
                                                                        round(b,3),' ',round(c,3))
        self.so_xung[0]    = x       # So xung truc x
        self.so_xung[1]    = y       # So xung truc y
        self.so_xung[2]    = z       # So xung truc z
        self.so_xung[3]    = a       # So xung truc a
        self.so_xung[4]    = b       # So xung truc b
        self.so_xung[5]    = c       # So xung truc c
    
        for x in range(0,6):
            self.so_xung[x] = self.so_xung[x] + self.sum_xung_le[x]
            self.sum_xung_le[x] = 0
            self.xung_nguyen[x] = math.trunc(self.so_xung[x])
            self.sum_xung_le[x] = self.so_xung[x] - self.xung_nguyen[x]
 
             
        print ('>>> So xung nguyen truc x,y,z,a,b,c: ', self.xung_nguyen[0],' ',self.xung_nguyen[1],' ',self.xung_nguyen[2],' ',
                                                        self.xung_nguyen[3],' ',self.xung_nguyen[4],' ',self.xung_nguyen[5])
        print ('>>> So xung le truc x,y,z,a,b,c:     ', round(self.sum_xung_le[0],3),' ',round(self.sum_xung_le[1],3),' ',round(self.sum_xung_le[2],3),' ',
                                                        round(self.sum_xung_le[3],3),' ',round(self.sum_xung_le[4],3),' ',round(self.sum_xung_le[5],3))
   
    def send_to_execute_board(self,pulse):
    # truyền giá trị xung nguyên và tốc độ x,y,z,a,b,c tới board execute; giá trị 32 bit 
        send_pulse_slave_id2 = [0,0,0,0,0,0,0,0] # gói giá trị 16 bit
        send_speed_slave_id2 = [0,0,0,0,0,0,0,0] # gói giá trị 16 bit

        send_pulse_slave_id3 = [0,0,0,0,0,0,0,0] # gói giá trị 16 bit
        send_speed_slave_id3 = [0,0,0,0,0,0,0,0] # gói giá trị 16 bit
#-------------------------------------------------------
# tính tốc độ của trục x,y,z,a
        print ("gia tri packet xung pulse: ",pulse[0],pulse[1],pulse[2],pulse[3],pulse[4],pulse[5])
        speed_slaves = Monitor_mode.Calculate_speed(pulse[0],pulse[1],pulse[2],pulse[3],pulse[4],pulse[5])
        print ("gia tri tan so phat xung: ",int(speed_slaves[0]),int(speed_slaves[1]),int(speed_slaves[2]),
                                            int(speed_slaves[3]),int(speed_slaves[4]),int(speed_slaves[5]))
        # gui speed x
        send_speed_slave_id2[0] = int(speed_slaves[0]) >> 16
        send_speed_slave_id2[1] = int(speed_slaves[0]) & 65535
        # gui speed y
        send_speed_slave_id2[2] = int(speed_slaves[1]) >> 16
        send_speed_slave_id2[3] = int(speed_slaves[1]) & 65535
        # gui speed z
        send_speed_slave_id2[4] = int(speed_slaves[2]) >> 16
        send_speed_slave_id2[5] = int(speed_slaves[2]) & 65535
        # gui speed a
        send_speed_slave_id2[6] = int(speed_slaves[3]) >> 16
        send_speed_slave_id2[7] = int(speed_slaves[3]) & 65535
        # gui speed b
        send_speed_slave_id3[0] = int(speed_slaves[4]) >> 16
        send_speed_slave_id3[1] = int(speed_slaves[4]) & 65535
        # gui speed c
        send_speed_slave_id3[2] = int(speed_slaves[5]) >> 16
        send_speed_slave_id3[3] = int(speed_slaves[5]) & 65535        
#-------------------------------------------------------
        # gui xung x
        send_pulse_slave_id2[0] = pulse[0] >> 16
        send_pulse_slave_id2[1] = pulse[0] & 65535
        # gui xung y
        send_pulse_slave_id2[2] = pulse[1] >> 16
        send_pulse_slave_id2[3] = pulse[1] & 65535
        # gui xung z
        send_pulse_slave_id2[4] = pulse[2] >> 16
        send_pulse_slave_id2[5] = pulse[2] & 65535
        # gui xung a
        send_pulse_slave_id2[6] = pulse[3] >> 16
        send_pulse_slave_id2[7] = pulse[3] & 65535
        # gui xung b
        send_pulse_slave_id3[0] = pulse[4] >> 16
        send_pulse_slave_id3[1] = pulse[4] & 65535
        # gui xung c
        send_pulse_slave_id3[2] = pulse[5] >> 16
        send_pulse_slave_id3[3] = pulse[5] & 65535

        
        # gửi giá trị tốc độ x,y,z,a tới board slave id 2, gửi 8 word, bắt đầu từ địa chỉ 10
        master.execute(SLAVE_02, cst.WRITE_MULTIPLE_REGISTERS, 10, output_value = send_speed_slave_id2)
        # gửi số xung x,y,z,a cần chạy tới board slave id 2, gửi 8 word, bắt đầu từ địa chỉ 0
        master.execute(SLAVE_02, cst.WRITE_MULTIPLE_REGISTERS, 0, output_value = send_pulse_slave_id2)
        # gửi giá trị tốc độ b,c tới board slave id 3, gửi 8 word, bắt đầu từ địa chỉ 10
        master.execute(SLAVE_03, cst.WRITE_MULTIPLE_REGISTERS, 10, output_value = send_speed_slave_id3)
        # gửi số xung b,c cần chạy tới board slave id 3, gửi 4 word, bắt đầu từ địa chỉ 0
        master.execute(SLAVE_03, cst.WRITE_MULTIPLE_REGISTERS, 0, output_value = send_pulse_slave_id3)
        # gửi command bật/tắt súng sơn
        if  int(self.S_switch) != self.state_spray:
            self.command_run_spray(int(self.S_switch))
            self.state_spray = int(self.S_switch)
        # phát command chạy điểm
        self.command_run_point2point()

    def command_run_point2point(self):
# phát lệnh đến board id 2 và id 3 bắt đầu chạy điểm point to point
        master.execute(SLAVE_02, cst.WRITE_SINGLE_COIL, self.POINT2POINT_MODBUS_ADDR, output_value = CHOOSE)
        master.execute(SLAVE_03, cst.WRITE_SINGLE_COIL, self.POINT2POINT_MODBUS_ADDR, output_value = CHOOSE)
    def command_run_spray(self, state):
        master.execute(SLAVE_02, cst.WRITE_SINGLE_COIL, self.SPRAY_ON_MODBUS_ADDR, output_value = state)
        if state:
            Show_Screen.spray_on_state.config(bg = "green", text = 'BẬT PHUN SƠN')
        else:
            Show_Screen.spray_on_state.config(bg = "red", text = 'TẮT PHUN SƠN')
    def pause_motor(self):
# phát lệnh dừng tay máy
        self.pause_on += 1

# define lại giá trị sau khi đã chạy auto hoàn tất
    def re_init(self):
        self.Xpwm = self.Ypwm = self.Zpwm = self.Apwm = self.Bpwm = self.Cpwm = 0
        self.so_xung = [0,0,0,0,0,0]
        self.xung_nguyen = [0,0,0,0,0,0]
        self.dx0 = self.dy0 = self.dz0 = self.da0 = self.db0 = self.dc0 = 0
        self.pause_on = 0
        self.stop_on = False
        Show_Screen.Auto_run_button.config(state = NORMAL)
        Show_Screen.Stop_button.config(state = DISABLED)
# Hiện thị từng dòng đang chạy trong file lên label
    def Monitor_str_content(seft, string):
        Show_Screen.string_content.set(string)
        Show_Screen.label_axis_monitor.update()
# Nhận diện dòng thỏa cú pháp trong file
    def Recognize_command_syntax(self, StringArr):

        self.Recognize_command = True
        RecognizeChar = ['0','1','2','3','4','5','6','7','8','9', 
                         'X', 'Y', 'Z', 'A', 'B', 'C', 'S', '.', '-', '\n', '\0']
       
        for char in StringArr:
            if char in RecognizeChar[0:]: 
                pass
            else:
              self.Recognize_command = False
              print("Ky tu khong dung systax: ",StringArr)
              break
#==============================================================================================================
def Show_machine_infor():
    machineFont = font.Font(size=33)
    nameFont = font.Font(size = 18)

    Frame10 = LabelFrame(root)
    Frame10.place(x = 10, y = 10)
    bg_frame10 = Canvas(Frame10, bg="green", height=120, width=1500, bd = 1)
    bg_frame10.pack(side = LEFT)

    Machine_infor = Label(Frame10,text = 'CÔNG TY CỔ PHẦN NHỰA KHÔI NGUYÊN \n MÁY SƠN GHẾ TỰ ĐỘNG',font = ("Arial",33,"bold"), fg ='black', justify = CENTER, bg = 'green')
    #Machine_infor['font'] = machineFont
    Machine_infor.place(x=350, y=10)

    Name_infor = Label(Frame10,text = 'Royal Robotics \n Designer: KHANH.N.Q',fg ='black', justify = CENTER, bg = 'yellow', bd = 1, relief = 'solid')
    Name_infor['font'] = nameFont
    Name_infor.place(x=1240, y=60)

    Frame20 = LabelFrame(root)
    Frame20.place(x = 10, y = 135)
    bg_frame20 = Canvas(Frame20, bg="#999999", height=650, width=1500, bd = 1)
    bg_frame20.pack(side = LEFT)
    #ComunicationRobot.Show_comunication_box()
#========================================================================
# Hiện thị tọa độ X,Y,Z
class Drawing_3D:
    def __init__(self):
        self.x0 = 0
        self.y0 = 0
        self.x = 0
        self.y = 0
        self.z = 0
    def Show_position(self,xb,yb,zb):
        d1,d2 = 0,0
        d1pre,d2pre = 0,0
        python_red = "red"
        python_white = "white"
        # tính tọa độ x2,y2 trên cavas từ xb,yb,zb 
        # db = math.sqrt(xb-self.x0)
        
        d1 = yb*math.sin(Show_Screen.radXY)
        d2 = yb*math.cos(Show_Screen.radXY)
        # print(Show_Screen.degXY)
        # print(Show_Screen.degXY)
        print(str(d1))
        print(str(d2))

        if (yb > self.y):
            x2_index = xb + d2
            y2_index = zb - d1
            print("yb lớn")
            
        if (yb < self.y):
            x2_index = xb - d2
            y2_index = zb + d1
            print("yb nhỏ")

        if (yb == self.y):
            x2_index = xb + d2
            y2_index = zb + d1

        print(x2_index)
        print(y2_index)
        x1, y1 = self.x0,self.y0
        x2, y2 = x2_index, y2_index
        c1 = Show_Screen.bg_frame11.create_line( x1, y1, x2, y2, fill = python_red)
        #c2 = w.create_line( x2, y2, self.XC0 ,self.YC0, fill = python_white)
        self.x0,self.y0 = x2,y2
        self.y = yb
        self.x = xb
        d1pre = d1
        d2pre = d2
        Show_Screen.bg_frame11.update() # Hien thi canvas theo thoi gian thuc
        print(str(self.x0) + '_' + str(self.y0) + '_' + str(self.y))
        
#========================================================================
Show_Screen = Screen()
Monitor_mode = Monitor_Position_Class()
Teach_mode = Teach_mode_class()
Send_to_Serial = Read_Write_to_Serial()
Home = Home_position()
ComunicationRobot = Com_box()
Work_file = Save_file()
Button_act = Button_Active()
Run = Run_auto()
Drawing = Drawing_3D()
#========================================================================

Show_machine_infor()
#========================================================================
#def Show_home_box():
HomemodeFont = font.Font(size=50)
Home_mode = Button(root, image = button_01, relief = GROOVE, borderwidth= 0,
                    activebackground = 'green',  bg = "#999999",
                       command = Home.Go_Home) # width = 30, height=5, 
#Home_mode['font'] = HomemodeFont#, , font = ("Arial",50,"bold") fg ='black', relief = 'solid', justify = LEFT, text = 'VỀ CHUẨN MÁY',
Home_mode.place(x = 500, y = 300)

#test_lable = Label(root, image = button_01, bg = "#999999").place(x = 500, y = 500)
#========================================================================  
#root.bind('<F1>', Show_Screen.pause)
#def key_pressed(event):
#    print(str(event.char))

#root.bind("<Key>",key_pressed)   
root.mainloop()