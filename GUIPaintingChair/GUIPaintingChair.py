from tkinter import *
from tkinter.ttk import Combobox
from tkinter import filedialog, messagebox, ttk, Toplevel
import tkinter.font as font
#from pymodbus.client.sync import ModbusSerialClient as ModbusClient
#import modbus_tk
import modbus_tk.defines as cst
import modbus_tk.modbus_rtu as rtu
#import pickle
import serial
import serial.tools.list_ports_windows
import time
import threading # chạy song song 2 chương trình
#import queue
import math
#import webbrowser
import numpy as np
import pygcode as code
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
global CHOOSE, NOCHOOSE
global SLAVE_02, SLAVE_03
global AXIS_RUN 
CHOOSE = 1; NOCHOOSE = 0
SLAVE_02 = 2; SLAVE_03 = 3
AXIS_RUN = 6
#============================================================================================
# đưa các trục tay máy sơn về vị trí gốc máy khi mới mở phần mềm.
# phát command để các động cơ chạy tới khi nào gặp cảm biến thì dừng lại
#============================================================================================
class Home_position:
    def __init__(self):
        self.ENABLE_HOME_MODBUS_ADDR = 15
    def Go_Home(self):
        try:
            #phải kết nối được đường truyền data modbus để mở giao diện điều khiển
            state = Send_to_Serial.Init_Serial()
            if state == 1:
                print("ACTIVATED MACHINE")
            else:
                return
            time.sleep(4)
            ComunicationRobot.Home_mode.destroy()
            ComunicationRobot.Frame2.destroy()
            Show_Screen.Show_screen_options()
            Show_Screen.Show_screen_teach_mode()
            Show_Screen.Show_screen_monitor()
            Show_Screen.Show_screen_res()
            Show_Screen.Show_XYZ()
            Show_Screen.Speed_toolbar()
            Show_Screen.Text_box()
            Monitor_in_out.Monitor_input_output()
            Monitor_mode.Read_pulse_PWM_from_slaves()
            creat_threading() # bật chế độ monitor coil XY

        except Exception as e:
            messagebox.showinfo("Serial Comunication","OPEN SOFWARE FAILED")
            print(str(e))
            return
   
#============================================================================================
class Save_file:  
    def __init__(self):
        self.initial_directory = StringVar()
        self.initial_directory.set("NO FILE LOADED")

    def open_file(self):
        Show_Screen.Show_content.delete('1.0','end')
        Show_Screen.Show_content.config(state = NORMAL)
        self.file = filedialog.askopenfilename(title = 'Open file .pnt', filetypes =[('file pulse', '*.pnt')],initialdir='/')
        self.show_initial_directory()
        Show_status.write_status("File: " + str(self.file))
        try:
            self._file = open(self.file,'r')
            self.show_file = self._file.read()
            Show_Screen.Show_content.insert(END,self.show_file) # insert all the characters of file into T
            countVar = IntVar()
            Counter = self.count_line()
            words = ['X', 'Y', 'Z','A', 'B', 'C', 'S','F']
            for i in range(Counter):
                for j in range(len(words)):
                    searched_position = Show_Screen.Show_content.search(pattern = words[j], index= str(str(i+1) + '.'+'0'), 
                                                stopindex= "end", count=countVar)
                    endindex = "{}+{}c".format(searched_position, countVar.get())
                    Show_Screen.Show_content.tag_add("a", searched_position, endindex)
        except Exception as err:
            print(str(err))
            return

    def save_file(self):
        Show_Screen.Show_content.insert(END, Run.turn_off_spray)
        Show_Screen.Show_content.insert(END, Run.go_to_1st_point) # command về vị trí zero
        Show_Screen.Show_content.insert(END, Run.table_rotary) # ghi ký tự command xoay bàn sơn
        Show_Screen.Show_content.insert(END, Run.end_symbol) # ghi ký tự nhận diện end file
        retrieve_text = Show_Screen.Show_content.get('1.0','end-1c')
        savefile = filedialog.asksaveasfile(mode='w+', defaultextension='*.pnt', filetypes =[('file pulse', '*.pnt')])
        try:
            savefile.write(retrieve_text)  # retrieve_text phải là các ký tự không có dấu.
            savefile.close()
            Show_Screen.Inform_App_Status("SAVED")
            
        except Exception as err:
            print(str(err))
            return

    # hiển thị đường dẫn tới file
    def show_initial_directory(self):
        initial_directory = self.file
        self.initial_directory.set("File: " + str(initial_directory))
        Show_Screen.file_name.update()

    def remove_directory(self):
        self.initial_directory.set("NO FILE LOADED")
        Show_Screen.file_name.update()
    def count_line(self):
        Cnt = 0
        CoList = self.show_file.split("\n")
        for i in CoList:
            if i: Cnt += 1
        return Cnt
#============================================================================================
class Read_Write_to_Serial:
    def Init_Serial(self): # Connect to Arduino
        global master
        connect = 0
        baud = 115200
        com = ComunicationRobot.choose_COM.get()
        try:
            master = rtu.RtuMaster(serial.Serial(port= com, baudrate = baud, bytesize=8, parity='N', stopbits=1, xonxoff=0))
            master.set_timeout(5.0)
            master.set_verbose(True)
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
            messagebox.showinfo("Serial Comunication", "FAILURE CONNECTION")
            return connect
    def Disconnect_Serial(self):
        try:
            master_closed = master._do_close()
            if master_closed:
                messagebox.showinfo("Serial Comunication", "DISCONNECTED")
        except:
                return
#========================================================================
class Screen:
    def __init__(self):
       
        self.spray_on_state = Label()
        self.label_axis_monitor = Label()

        self.speed_value = DoubleVar()
        self.speed_scale = Scale()
        self.Show_content = Text()
        # góc của trục Y so với trục X hiện thị trên canvas

        self.string_content = StringVar()
        self._speed_value = StringVar()
        
#========================================================================
# THANH CÔNG CỤ TÙY CHỌN 
    def Show_screen_options(self):
        Frame0 = LabelFrame(root)
        Frame0.place(x = 900, y = 150)
        bg_frame0 = Canvas(Frame0, bg="#333333", height=40, width=610)
        bg_frame0.pack(side = LEFT)
        #========================================================================
        self.button_option = []
        self.button_option_name = ['TEACH MODE','CHOOSE FILE','MANUAL','GOTO ZERO','MACHINE AXIS']
        command_option = [Teach_mode.Enable_teach_options, Work_file.open_file,
                 Monitor_in_out.enable_radio_button, Monitor_mode.Go_to_zero_position, Monitor_mode.Go_to_machine_axis]
        for i in range(len(self.button_option_name)):
            self.button_option.append(Button(Frame0, text =self.button_option_name[i], justify = LEFT, width = 12, activebackground = 'green',
                                command = command_option[i], font = ("Arial",10,"bold"), fg = 'white',bg = '#555555'))
            self.button_option[i].place(x = 30+110*i, y = 10)

        self.button_option[4].config(bg ='#990000')

    def disable_screen_option(self):
        for i in range(len(self.button_option_name)): 
                    self.button_option[i].config(state = DISABLED)
    def enable_screen_option(self):
        for i in range(len(self.button_option_name)): 
                    self.button_option[i].config(state = NORMAL)
#========================================================================
# CỬA SỔ CHẾ ĐỘ DẠY ROBOT SƠN
    def Show_screen_teach_mode(self):
        Frame1 = LabelFrame(root)
        Frame1.place(x = 10, y = 150)
        bg_frame1 = Canvas(Frame1, bg="#333333", height=370, width=300, bd = 1)
        bg_frame1.pack(side = LEFT)
        Label(Frame1,text = 'TEACHING MODE',fg ='white', bg = '#333333', justify = LEFT,font = ("Arial",11,"bold")).place(x=150, y=3)
        bg_frame1.create_line(120,0,120,402,fill = 'white',width = 2)
        bg_frame1.create_line(125,0,125,402,fill = 'white',width = 2)
        bg_frame1.create_line(125,30,400,30,fill = 'white',width = 2)
        bg_frame1.create_line(125,100,400,100,fill = 'white',width = 2)
        #========================================================================
        self.teach_option = []
        self.teach_option_name = ['SET POINT','SAVE FILE','SET ZERO','EXIT']
        teach_command = [Teach_mode.Show_point_to_textbox,
                         Teach_mode.Save_file, Teach_mode.Set_zero_position, Teach_mode.Disable_teach_options]
        for i in range(len(self.teach_option_name)):
            self.teach_option.append(Button(Frame1, text =self.teach_option_name[i], justify = LEFT, width = 9, activebackground = 'green', 
                                    font = ("Arial",16,"bold"), fg ='white', bg = "#666666",  command = teach_command[i]))
            self.teach_option[i].place(x = 150, y = 120 + 60*i)
            self.teach_option[i].config(state = DISABLED)
        self.teach_option[3].config(bg ='#990000')

        self.button_teach = []
        #self.button_teach_name = ['TRỤC X+/X-','TRỤC Y+/Y-','TRỤC Z+/Z-','TRỤC B+/B-','TRỤC C+/C-','SPRAY ON','SPRAY OFF'] #,'TRỤC A+/A-' Teach_mode.Teach_A_Axis,
        #button_teach_command = [Teach_mode.Teach_X_Axis, Teach_mode.Teach_Y_Axis, Teach_mode.Teach_Z_Axis,
        #                             Teach_mode.Teach_B_Axis, Teach_mode.Teach_C_Axis,Teach_mode.Spray_on,Teach_mode.Spray_off]
        
        self.button_teach_name = ['TABLE FW','TABLE RW','SPRAY ON','SPRAY OFF'] 
        button_teach_command = [    Teach_mode.Table_fw,Teach_mode.Table_rw,
                                     Teach_mode.Spray_on,Teach_mode.Spray_off]
        
        for i in range(len(self.button_teach_name)):
            self.button_teach.append(Button(Frame1, text =self.button_teach_name[i], justify = LEFT, width = 10, activebackground = 'green', 
                                font = ("Arial",10,"bold"), fg = 'white', bg = "gray", command = button_teach_command[i], state=DISABLED))
            self.button_teach[i].place(x= 10, y = 72 +40*i)
        
        _speed_label = Label(Frame1, text = 'Speed(%)',font = ("Arial",12,"bold"), fg = 'white', bg="#333333")
        _speed_label.place(x =140, y=60)
        self._speed_entry = Entry(Frame1,bd =5, width = 6, state = DISABLED, font = ("Arial",11,"bold"), textvariable = self._speed_value)
        self._speed_entry.place(x = 214, y = 60)

    def disable_teach_option(self):
        for i in range(len(self.teach_option_name)):
            self.teach_option[i].config(state = DISABLED)
        self._speed_entry.config(state = DISABLED)
    def enable_teach_option(self):
        for i in range(len(self.teach_option_name)):
            self.teach_option[i].config(state = NORMAL)
        self._speed_entry.config(state = NORMAL)
        self._speed_value.set('0')
    def disable_button_teach(self):
        for i in range(len(self.button_teach_name)):
            self.button_teach[i].config(state = DISABLED, bg = "gray")
    def enable_button_teach(self,index):
        for i in range(len(self.button_teach_name)):
            self.button_teach[i].config(state = NORMAL, bg = "gray")
        if 0 <= index < len(self.button_teach_name):
            self.button_teach[index].config(bg = "green")  
#========================================================================
# "HIỂN THỊ VỊ TRÍ CÁC TRỤC CỦA MÁY SƠN"
    def Show_screen_monitor(self):
        Frame3 = LabelFrame(root)
        Frame3.place(x = 350, y = 150)
        bg_frame3 = Canvas(Frame3, bg="#333333", height=210, width=300)
        bg_frame3.pack(side = LEFT)

        Label(Frame3,text = 'AXIS',fg ='white', bg = '#333333', justify = LEFT, font = ("Arial",11,"bold")).place(x=30, y=3)
        Label(Frame3,text = 'G54 WORK',fg ='white', bg = '#333333', justify = LEFT, font = ("Arial",11,"bold")).place(x=100, y=3)
        Label(Frame3,text = 'MACHINE',fg ='white', bg = '#333333', justify = LEFT, font = ("Arial",11,"bold")).place(x=200, y=3)             
        # biến lưu tọa độ so với gốc máy
        machine_axis_value = [Monitor_mode.var1,Monitor_mode.var2,Monitor_mode.var3,
                                   Monitor_mode.var4,Monitor_mode.var5,Monitor_mode.var6]
        work_axis_value =  [Monitor_mode.var11,Monitor_mode.var12,Monitor_mode.var13,
                                 Monitor_mode.var14,Monitor_mode.var15,Monitor_mode.var16]
        label_name_axis = []
        self.label_machine_axis_value = []
        self.label_work_axis_value = []
        self.name_axis = ['X AXIS', 'Y AXIS', 'Z AXIS','A AXIS', 'B AXIS', 'C AXIS']
        #========================================================================
        for i in range(len(self.name_axis)):
            label_name_axis.append(Label(Frame3,text = self.name_axis[i],fg ='white', bg = '#777777', justify = LEFT, relief = 'solid',width=8,
                                                     font = ("Arial",11,"bold")).place(x=10, y=30 + 30*i))
            self.label_machine_axis_value.append(Label(Frame3, text= 0,fg ='red', textvariable = machine_axis_value[i], bd = 1,width=10,relief = 'solid',
                                                     font = ("Arial",11,"bold")))
            self.label_machine_axis_value[i].place(x = 100, y = 30 + 30*i)
            self.label_work_axis_value.append(Label(Frame3, text= 0,fg ='red', textvariable = work_axis_value[i], bd = 1,width=10,relief = 'solid',
                                                     font = ("Arial",11,"bold")))
            self.label_work_axis_value[i].place(x = 200, y = 30 + 30*i)

    def update_axis_label(self):
        for i in range(len(self.name_axis)):
            self.label_machine_axis_value[i].update()
            self.label_work_axis_value[i].update()
#========================================================================
# ĐỘ PHÂN GIẢI KHI DÙNG TAY QUAY ENCODER
    def Show_screen_res(self):
        Frame4 = LabelFrame(root)
        Frame4.place(x = 10, y = 545)
        bg_frame4 = Canvas(Frame4, bg="#333333", height=80, width=300, bd = 1)
        bg_frame4.pack(side = LEFT)

        bg_frame4.create_line(0,30,120,30, fill = 'white',width = 1)
        #========================================================================
        Label(Frame4,text = 'RESOLUTION',fg ='white', bg = '#333333', justify = LEFT,font = ("Arial",11,"bold")).place(x=5, y=3)
        resolution_command = [Teach_mode.X1_resolution,Teach_mode.X10_resolution,Teach_mode.X100_resolution,Teach_mode.X1000_resolution]
        self.resolution_name = ['x1','x10','x100','x1000']
        self.resolution_button = []
        #========================================================================
        for i in range(len(self.resolution_name)):
            self.resolution_button.append(Button(Frame4, text =self.resolution_name[i], justify = LEFT, width = 5, activebackground = 'green', 
                    fg ='white',font = ("Arial",11,"bold"), command = resolution_command[i], state=DISABLED, bg = "gray"))
            self.resolution_button[i].place(x = 20+70*i, y = 45)

    def disable_resolution_button(self):
        for i in range(len(self.resolution_name)):
            self.resolution_button[i].config(state = DISABLED, bg = "gray")
    def enable_resolution_button(self,index):
        for i in range(len(self.resolution_name)):
            self.resolution_button[i].config(state = NORMAL, bg = "gray")
        if 0 <= index < len(self.resolution_name):
            self.resolution_button[index].config( bg = "green")
#========================================================================
# "HIỂN THỊ TỌA ĐỘ SÚNG SƠN"
    def Show_XYZ(self):
        Frame12 = LabelFrame(root)
        Frame12.place(x = 660, y = 150)
        bg_frame12 = Canvas(Frame12, bg="#333333", height=210, width=200)
        bg_frame12.pack(side = LEFT)
        Label(Frame12,text = 'SPRAY GUN',fg ='white', bg = '#333333', justify = LEFT,font = ("Arial",11,"bold")).place(x=10, y=3)

        spray_axis_name = ['X', 'Y', 'Z', 'B']
        spray_value = [Monitor_mode.var1, Monitor_mode.var20, Monitor_mode.var21, Monitor_mode.var5]
        spray_label = []
        spray_value_label = []
        for i in range(len(spray_axis_name)):
            spray_label.append(Label(Frame12,text =spray_axis_name[i],fg ='white', bg = '#777777',justify = LEFT, relief = 'solid', 
                                    width=5, font = ("Arial",11,"bold")).place(x=10, y=30+30*i))
            spray_value_label.append(Label(Frame12, text= 0,fg ='black', textvariable = spray_value[i], bd = 1,
                                    width=12, relief = 'solid', font = ("Arial",11,"bold")))
            spray_value_label[i].place(x = 70, y = 30+30*i)                        

        self.spray_on_state = Label(Frame12,text = 'SPRAY OFF',fg ='white', justify = LEFT, relief = 'solid',width=10, bg = 'gray',font = ("Arial",11,"bold"))
        self.spray_on_state.place(x=10, y=180)
      
#======================================================================== 
#, text="TỐC ĐỘ SƠN (%)")
    def Speed_toolbar(self):
        Frame13 = LabelFrame(root ,text = 'SPEED',font = ("Arial",11,"bold"))
        Frame13.place(x = 10, y = 650)

        self.speed_scale = Scale( Frame13, variable = (self.speed_value), from_ = 30, to = 200, orient = HORIZONTAL,  bg = '#888888',
                                length = 300, width=15, fg = 'white',font = ("Arial",10,"bold"))   
        self.speed_scale.pack(anchor = CENTER) 
        self.speed_scale.set(30) # khởi tạo giá trị mặc định
#========================================================================
#, text="BẢNG GIÁM SÁT")
    def Text_box(self):
        Frame14 = LabelFrame(root)
        Frame14.place(x = 900, y = 246)#(x = 350, y = 415)
        scroll1 = Scrollbar(Frame14,  orient = VERTICAL)
        scroll2 = Scrollbar(Frame14,  orient = HORIZONTAL)

        self.Show_content = Text(Frame14, height=22, width=74, bd = 1, bg = "#CCCCCC", font = ("Arial",11,"bold"),
                                 xscrollcommand = scroll2.set, yscrollcommand = scroll1.set, wrap = 'none')
        scroll1.config (command = self.Show_content.yview)
        scroll2.config (command = self.Show_content.xview)
        scroll1.pack(side=RIGHT, fill= Y)
        scroll2.pack(side=BOTTOM, fill= X)
        self.Show_content.pack(side = LEFT)
        self.Show_content.config(state = DISABLED)
        Show_Screen.Show_content.tag_config("a", foreground="blue")
        Frame15 = LabelFrame(root) # Giám sát từng dòng
        Frame15.place(x = 900, y = 669)
        bg_frame15 = Canvas(Frame15, bg="#333333", height=110, width=610)
        bg_frame15.pack(side = LEFT)
    
        self.label_axis_monitor = Label(Frame15, text= 0,fg ='white', bg = '#333333', textvariable = self.string_content,
                                        font = ("Arial",13,"bold"), width=54, bd = 1,relief = 'solid')
        self.label_axis_monitor.place(x = 37, y = 10 )
       
        self.button_control = []
        button_control_name = ['AUTO','PAUSE','STATUS','E-STOP']
        button_control_command = [Run.activate_run_mode,Run.pause_motor,
                                        Show_status.show_new_window,Run.disable_run_mode]
        for i in range(len(button_control_name)):
            self.button_control.append(Button(Frame15, text =button_control_name[i], fg = 'white',
                        activebackground = 'green', bg = "#555555", justify = LEFT,  width = 6,
                        bd = 2,font = ("Arial",16,"bold"),command = button_control_command[i]))
            self.button_control[i].place(x =90 + 120*i, y = 60)
        self.button_control[3].config(bg ='#990000')
        self.Show_file_name()

    def Show_file_name(self):
        Frame16 = LabelFrame(root)
        Frame16.place(x = 900, y = 205)
        bg_frame16 = Canvas(Frame16, bg="#333333", height=30, width=610, bd = 1)
        bg_frame16.pack(side = LEFT)
        self.file_name = Label(Frame16, text = 0 ,textvariable = Work_file.initial_directory, fg = 'white',bg = '#333333',
                                justify = LEFT,font = ("Arial",10,"bold"))
        self.file_name.place(x = 5, y = 6)

    def disable_button_control(self,index = 100):
        if index != 100:
            self.button_control[index].config(state = DISABLED)
    def enable_button_control(self, index = 100):
        if index != 100:
            self.button_control[index].config(state = NORMAL)

    def pause(self, event):
        Run.pause_motor()
        print("pause button")

    def insert_instruction(self):
        string = "HUONG DAN SU DUNG MAY SON"
        self.Show_content.insert("1.0",string)

    def Inform_App_Status(self,a):
        messagebox.showinfo("Inform", a)
#========================================================================
class Monitor_Input_Output():
    def __init__(self):
        self.toggle_coilY_state = 0
        self.coilY_packet = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        self.send_coilY_value = 0
        self.coilY = []
        self.coilX = []
        self.sensor_value = []
        self.radio_button = []
        self.coilY_name = ['Y1','Y2','Y3','Y4','Y5','Y6','Y7','Y8','Y9','Y10','Y11','Y12','Y13','Y14','Y15','Y16']
        self.coilX_name = ['X1','X2','X3','X4','X5','X6','X7','X8','X9','X10','X11','X12','X13','X14','X15','X16']
        self.var = StringVar()
        self.INPUT_OUTPUT_VALUE_MODBUS_ADDR = 12
        self.COIL_Y1_FIRST_MODBUS_ADDR = 32
        self.COIL_X1_FIRST_MODBUS_ADDR = 64
        self.STOP_MOTOR_MODBUS_ADDR = 1
        self.CHANGE_STATE_COIL_Y_MODBUS_ADDR = 12
        self.WRITE_YCOIL = 24
        self.button_active = 0
        self.forward = 1
        self.reverse = -1

# Hiển thị các label input và output, radio button trong cửa sổ MONITOR
    def Monitor_input_output(self):
        Frame17 = LabelFrame(root)
        Frame17.place(x = 350, y = 380)
        self.bg_frame17 = Canvas(Frame17, bg="#333333", height=400, width=510)
        self.bg_frame17.pack(side = LEFT)
        self.monitor_label = Label(Frame17, text = 'MANUAL', fg = 'white',bg = '#333333',
                                justify = LEFT,font = ("Arial",10,"bold"))
        self.monitor_label.place(x = 10, y = 5)
        self.bg_frame17.create_line(421,0,421,402,fill = 'white',width = 2)
        self.bg_frame17.create_line(310,0,310,402,fill = 'white',width = 2)
        self.bg_frame17.create_line(0,30,512,30,fill = 'white',width = 2)
        self.bg_frame17.create_text(442,15,anchor = W, text = 'INPUT', fill = 'white',font = ("Arial",10,"bold"))
        self.bg_frame17.create_text(350,15,anchor = W, text = 'OUTPUT', fill = 'white',font = ("Arial",10,"bold"))
       
        # tạo label,radio button cho output Y
        for i in range(len(self.coilY_name)):
            self.radio_button.append(Radiobutton(Frame17, variable=self.var, value= i, state = DISABLED,
                                     bg = '#333333', activebackground = '#333333', command = self.toggle_coilY))
            self.radio_button[i].place(x = 320, y = (50 + 20*i))
            self.coilY.append(Label(Frame17,text = self.coilY_name[i],fg = 'white', bg = 'gray', width=5, relief = 'solid',font = ("Arial",10,"bold")))
            self.coilY[i].place(x = 350, y = (50 + 20*i))
  
        for i in range(len(self.coilX_name)):
            self.coilX.append(Label(Frame17, text = self.coilX_name[i],fg ='white', bg = 'gray', width=5, relief = 'solid',font = ("Arial",10,"bold")))
            self.coilX[i].place(x = 442, y = (50 + 20*i))

        self.manual_mode()

# Lệnh bật output Y và giám sát trạng thái đóng mở của Y
    def toggle_coilY(self):
        self.toggle_coilY_state += 1
        if self.toggle_coilY_state == 1:
            for i in range(len(self.coilY_name)):
                if self.var.get() == str(i): self.coilY_packet[i] = 1; self.send_coilY_value |= (1 << i)
        if self.toggle_coilY_state == 2:
            for i in range(len(self.coilY_name)):
                if self.var.get() == str(i): self.coilY_packet[i] = 0; self.send_coilY_value &= ~(1 << i)
            self.toggle_coilY_state = 0
        
        master.execute(SLAVE_02, cst.WRITE_SINGLE_REGISTER, self.WRITE_YCOIL, output_value = self.send_coilY_value) # gửi giá trị coilY xuống slave
        master.execute(SLAVE_02, cst.WRITE_SINGLE_COIL, self.CHANGE_STATE_COIL_Y_MODBUS_ADDR, output_value= CHOOSE) # command xuất giá trị coilY 

# Cho phép đọc trạng thái coil X từ board slave
    def read_coilXY(self):
        # input bình thường ở mức cao. khi có tín hiệu thì sẽ kéo xuống mức thấp
        input_output_packet = master.execute (SLAVE_02, cst.READ_HOLDING_REGISTERS, self.INPUT_OUTPUT_VALUE_MODBUS_ADDR, 2)
        input_packet = []
        output_packet = []
        for i in range(len(self.coilX_name)):
            input_packet.append((input_output_packet[0] >> i) & 0x00001)
            if input_packet[i] == 1: self.coilX[i].config(bg = 'gray') # không có tín hiệu input
            else: self.coilX[i].config(bg = 'green')    # có tín hiệu input
        
        for i in range(len(self.coilY_name)):
            output_packet.append((input_output_packet[1] >> i) & 0x0001)   
            if output_packet[i] == 1: self.coilY[i].config(bg = 'green')  # có tín hiệu
            else: self.coilY[i].config(bg = 'gray')   # không có tín hiệu
        
        return input_packet
# 
    def monitor_coil_XY(self):
        while True:
            #if Teach_mode.teach_state == False:
            #    Monitor_mode.Read_pulse_PWM_from_slaves()
            self.sensor_value = self.read_coilXY()
            time.sleep(0.1) # 100 ms đọc data coilXY 1 lần

    def enable_radio_button(self):
        for i in range(len(self.coilY_name)):
            self.radio_button[i].config(state = NORMAL)
            
    def disable_radio_button(self):
        for i in range(len(self.coilY_name)):
            self.radio_button[i].config(state = DISABLED)
    
    def manual_mode(self):
        axis_name_forward = ['X-','Y-','Z-','B-','C-','A-','Z1-']
        axis_name_reverse = ['X+','Y+','Z+','B+','C+','A+','Z1+']
        manual_command_01_active   = [self.buttonX_forward, self.buttonY_forward, self.buttonZ_forward, 
                                      self.buttonB_forward, self.buttonC_forward, self.buttonA_forward,  self.buttonZ1_forward]

        manual_command_02_active = [self.buttonX_reverse, self.buttonY_reverse, self.buttonZ_reverse, 
                                    self.buttonB_reverse, self.buttonC_reverse, self.buttonA_reverse, self.buttonZ1_reverse]

        manual_command_deactive = [self._inactive, self._inactive, self._inactive, self._inactive, 
                                   self._inactive, self._inactive, self._inactive]
        manual_button_01 = []
        manual_button_02 = []

        for i in range(len(axis_name_forward)):
            manual_button_01.append(Button(self.bg_frame17, text =axis_name_forward [i], fg = 'white',
                        activebackground = 'green', bg = "gray", justify = LEFT,  width = 9, borderwidth=0, highlightthickness=0,
                        bd = 1, font = ("Arial",12,"bold")))
            manual_button_01[i].place(x = 45,y = 50+ 50*i)
            manual_button_01[i].bind("<ButtonPress>", manual_command_01_active[i])
            manual_button_01[i].bind("<ButtonRelease>", manual_command_deactive[i])

        for i in range(len(axis_name_reverse)):
            manual_button_02.append(Button(self.bg_frame17, text =axis_name_reverse [i], fg = 'white',
                        activebackground = 'green', bg = "gray", justify = LEFT,  width = 9, borderwidth=0, highlightthickness=0,
                        bd = 1, font = ("Arial",12,"bold")))
            manual_button_02[i].place(x = 170,y = 50+ 50*i)
            manual_button_02[i].bind("<ButtonPress>", manual_command_02_active[i])
            manual_button_02[i].bind("<ButtonRelease>", manual_command_deactive[i])

    def buttonX_forward(self, event):
        print ("Dang nhan button X-")
        Teach_mode.teach_axis = Teach_mode.TEACH_X_AXIS
        self.button_active = self.forward
    def buttonX_reverse(self, event):
        print ("Dang nhan button X+")
        Teach_mode.teach_axis = Teach_mode.TEACH_X_AXIS
        self.button_active = self.reverse
    def buttonY_forward(self, event):
        print ("Dang nhan button Y-")
        Teach_mode.teach_axis = Teach_mode.TEACH_Y_AXIS
        self.button_active = self.forward
    def buttonY_reverse(self, event):
        print ("Dang nhan button Y+")
        Teach_mode.teach_axis = Teach_mode.TEACH_Y_AXIS
        self.button_active = self.reverse
    def buttonZ_forward(self, event):
        print ("Dang nhan button Z-")
        Teach_mode.teach_axis = Teach_mode.TEACH_Z_AXIS
        self.button_active = self.forward
    def buttonZ_reverse(self, event):
        print ("Dang nhan button Z+")
        Teach_mode.teach_axis = Teach_mode.TEACH_Z_AXIS
        self.button_active = self.reverse
    def buttonB_forward(self, event):
        print ("Dang nhan button B-")
        Teach_mode.teach_axis = Teach_mode.TEACH_B_AXIS
        self.button_active = self.forward
    def buttonB_reverse(self, event):
        print ("Dang nhan button B+")
        Teach_mode.teach_axis = Teach_mode.TEACH_B_AXIS
        self.button_active = self.reverse
    def buttonC_forward(self, event):
        print ("Dang nhan button C-")
        Teach_mode.teach_axis = Teach_mode.TEACH_C_AXIS
        self.button_active = self.forward
    def buttonC_reverse(self, event):
        print ("Dang nhan button C+")
        Teach_mode.teach_axis = Teach_mode.TEACH_C_AXIS
        self.button_active = self.reverse

    def buttonA_forward(self, event):
        print ("Dang nhan button A-")
        Teach_mode.teach_axis = Teach_mode.TEACH_A_AXIS
        self.button_active = self.forward

    def buttonA_reverse(self, event):
        print ("Dang nhan button A+")
        Teach_mode.teach_axis = Teach_mode.TEACH_A_AXIS
        self.button_active = self.reverse    

    def buttonZ1_forward(self, event):
        print ("Dang nhan button Z1-")
        Teach_mode.teach_axis = Teach_mode.TEACH_Z1_AXIS
        self.button_active = self.forward

    def buttonZ1_reverse(self, event):
        print ("Dang nhan button Z1+")
        Teach_mode.teach_axis = Teach_mode.TEACH_Z1_AXIS
        self.button_active = self.reverse


    def _inactive(self, event):
        print("Release button")
        self.button_active = 0
        
    def stop_motor(self):
        master.execute(SLAVE_02, cst.WRITE_SINGLE_COIL, self.STOP_MOTOR_MODBUS_ADDR, output_value = CHOOSE)
        print ("Stop motor")
#========================================================================
# BẬT TẮT NGUỒN ĐIỆN THÔNG QUA SOFWARE
    def Turn_on_Power(self):
        pass

    def Turn_off_Power(self):
        pass
#========================================================================
class Terminal():
    def __init__(self):
        self.status = StringVar()
    def show_new_window(self):
        newWindow = Toplevel()
        self.labelExample = Label(newWindow, text = 0, textvariable = self.status)
        self.labelExample.pack()

    def write_status(self, string):
        try:
            self.status.set(string)
            self.labelExample.update()
        except:
            pass
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

        self.var11 = StringVar()
        self.var12 = StringVar()
        self.var13 = StringVar()
        self.var14 = StringVar()
        self.var15 = StringVar()
        self.var16 = StringVar()

        self.varG54 = []

        self.var20 = StringVar()
        self.var21 = StringVar()

        self.CURRENT_POSITION_MODBUS_ADDR = 0           # Địa chỉ lưu giá trị xung trục X
        self.PWM_VALUE_Y_AXIS_MODBUS_ADDR = 2           # Địa chỉ lưu giá trị xung trục Y
        self.PWM_VALUE_Z_AXIS_MODBUS_ADDR = 4           # Địa chỉ lưu giá trị xung trục Z
        self.PWM_VALUE_A_AXIS_MODBUS_ADDR = 6           # Địa chỉ lưu giá trị xung trục A
        self.PWM_VALUE_SPRAY_AXIS_MODBUS_ADDR = 8       # Địa chỉ lưu giá trị xung trục B
        self.PWM_VALUE_CHAIR_AXIS_MODBUS_ADDR = 10      # Địa chỉ lưu giá trị xung trục C
        self.ROTARY_ENCODER_MODBUS_ADDR       = 20      # Địa chỉ lưu giá trị xung ROTARY ENCODER

        self.SET_ZERO_POSITION_ADDR = 16
        self.ENABLE_HOME_MODBUS_ADDR = 15

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

        self.pos_X = 0; self.pos_Y = 0; self.pos_Z = 0; self.pos_A = 0; self.pos_B = 0; self.pos_C = 0
        self.offset_x_axis = 0; self.offset_y_axis = 0; self.offset_z_axis = 0
        self.offset_a_axis = 0; self.offset_b_axis = 0; self.offset_c_axis = 0
        self.pos_Yspray = 0; self.pos_Zspray = 0

        self.gear_ratio_X = ((80*math.pi)/(1600*5))    # truc X cài vi bước 6400 xung/vòng, không có hộp số
        self.gear_ratio_Y = ((80*math.pi)/(25600))  # trục Y cài vi bước 3200 xung/vòng, hộp số 1/5
        self.gear_ratio_Z = ((80*math.pi)/(3200*5))  # trục Z cài vi bước 3200 xung/vòng, hộp số 1/5
        self.gear_ratio_A = (360/(12800*5))          # trục A cài vi bước 12800 xung/vong, hộp số 1/5
        self.gear_ratio_B = (360/12800)              # trục B cài vi bước 12800 xung/vòng, không có hộp số
        self.gear_ratio_C = (360/12800)              # trục C cài vi bước 12800 xung/vong, không có hộp số

        self.spray_axis = 550    # chiều dài trục súng sơn
        self.pre_button_state = 0 

        self.machine_axis = False  # khóa machine axis sao cho chỉ sử dụng được 1 lần

    def read_state_button(self):
        state = Monitor_in_out.button_active
        return state

    def Kinematics_Zaxis(self):
        if Teach_mode.teach_axis == Teach_mode.TEACH_Z_AXIS:
            Yspray_expect = self.pos_Yspray
            while Teach_mode.teach_axis == Teach_mode.TEACH_Z_AXIS:
                self.rotary_encoder = self.Read_rotary_encoder()
                #self.Read_pulse_PWM_from_slaves()

                if (self.rotary_encoder > self.pre_rotary_encoder):
                    pulse_A_teach = -1*Teach_mode.gain_rotary_encoder
                    new_pos_A = self.pos_A + (pulse_A_teach*self.gear_ratio_A)
                    if(self.pos_Z > 0): 
                        pulse_Z_teach = pulse_A_teach
                        self.pulse_teach_packet = [0,0,pulse_Z_teach,0,0,0]
                    else: 
                        new_pos_Y = Yspray_expect - self.spray_axis*math.cos((new_pos_A*math.pi)/180)
                        pulse_Y_teach = int((new_pos_Y - self.pos_Y)/self.gear_ratio_Y) # số xung trục quay Y cần quay
                        self.pulse_teach_packet = [0,pulse_Y_teach,0,pulse_A_teach,0,0]

                if (self.rotary_encoder < self.pre_rotary_encoder):
                    pulse_A_teach = Teach_mode.gain_rotary_encoder
                    new_pos_A = self.pos_A + (pulse_A_teach*self.gear_ratio_A)
                    if(new_pos_A > 90): 
                        pulse_Z_teach = pulse_A_teach
                        self.pulse_teach_packet = [0,0,pulse_Z_teach,0,0,0]
                    else: 
                        new_pos_Y = Yspray_expect - self.spray_axis*math.cos((new_pos_A*math.pi)/180)
                        pulse_Y_teach = int((new_pos_Y - self.pos_Y)/self.gear_ratio_Y) # số xung trục quay Y cần quay
                        self.pulse_teach_packet = [0,pulse_Y_teach,0,pulse_A_teach,0,0]

                if self.rotary_encoder != self.pre_rotary_encoder:
                    self.pre_rotary_encoder = self.rotary_encoder
                    Run.send_to_execute_board(self.pulse_teach_packet,0)
                    while True:
                        new_position_done_slave_02 = master.execute(SLAVE_02, cst.READ_COILS, self.EXECUTE_PULSE_DONE, 1)
                        #self.Read_pulse_PWM_from_slaves()
                        if new_position_done_slave_02[0] == 1: 
                           break 

                if (self.monitor_off == True):
                    self.rotary_encoder = 0
                    self.pre_rotary_encoder = 0
                    break
        else: pass
# thực hiện chạy động cơ và giám sát số xung phát ra trong chế độ teach mode dùng rotary encoder
    def Monitor_pulse_in_teach_mode_01(self):
        Teach_mode.teach_axis = Teach_mode.no_choise_axis
        pulse_teach = 0
        while True:
            self.pulse_teach_packet = [0,0,0,0,0,0]
            state_runing = False
            self.rotary_encoder = self.Read_rotary_encoder()
            #self.Read_pulse_PWM_from_slaves()
            self.Kinematics_Zaxis()
            #print("gia tri rotary encoder: ", self.rotary_encoder, self.pre_rotary_encoder)

            if (self.rotary_encoder > self.pre_rotary_encoder):  pulse_teach = -1*Teach_mode.gain_rotary_encoder
            if (self.rotary_encoder < self.pre_rotary_encoder):  pulse_teach = 1*Teach_mode.gain_rotary_encoder
            
            if Teach_mode.teach_axis == Teach_mode.TEACH_X_AXIS:
                    new_pos_X = self.pos_X + (pulse_teach*self.gear_ratio_X)
                    if new_pos_X < 0 or new_pos_X > 1000: self.pre_rotary_encoder = self.rotary_encoder

            if Teach_mode.teach_axis == Teach_mode.TEACH_Y_AXIS:
                new_pos_Y = self.pos_Y + (pulse_teach*self.gear_ratio_Y)
                if new_pos_Y < 0 or new_pos_Y > 1000: self.pre_rotary_encoder = self.rotary_encoder

            if Teach_mode.teach_axis == Teach_mode.TEACH_A_AXIS:
                new_pos_A = self.pos_A + (pulse_teach*self.gear_ratio_A)
                if new_pos_A < 0 or new_pos_A > 90: self.pre_rotary_encoder = self.rotary_encoder

            if Teach_mode.teach_axis == Teach_mode.TEACH_B_AXIS:
                new_pos_B = self.pos_B + (pulse_teach*self.gear_ratio_B)
                if new_pos_B < -90 or new_pos_B > 90: self.pre_rotary_encoder = self.rotary_encoder
                    
            if Teach_mode.teach_axis == Teach_mode.TEACH_C_AXIS:
                new_pos_C = self.pos_C + (pulse_teach*self.gear_ratio_C)
                if new_pos_C < -360 or new_pos_C > 360: self.pre_rotary_encoder = self.rotary_encoder 
        
            if (self.rotary_encoder != self.pre_rotary_encoder):
                self.pre_rotary_encoder = self.rotary_encoder
                self.pulse_teach_packet[Teach_mode.teach_axis] = pulse_teach
                Run.send_to_execute_board(self.pulse_teach_packet,0)
                state_runing = True
                                    
            while state_runing:
                # Đọc trạng thái phát xung đã hoàn tất chưa
                new_position_done_slave_02 = master.execute(SLAVE_02, cst.READ_COILS, self.EXECUTE_PULSE_DONE, 1)
                #self.Read_pulse_PWM_from_slaves()
                if new_position_done_slave_02[0] == 1: 
                    break  # thoat khỏi vong lặp while

            if (self.monitor_off == True):
                self.monitor_off = False
                self.rotary_encoder = 0
                self.pre_rotary_encoder = 0
                Teach_mode.teach_axis = Teach_mode.no_choise_axis
                break
#=========================================================================================
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
#============================================================================
# che do teach mode qua nut nhan
    def Monitor_pulse_in_teach_mode_02(self):
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

# phát lệnh cho các động cơ chạy về điểm zero: điểm gốc máy so với vị trí hiện tại của tay máy
    def Go_to_zero_position(self):
        print("Going to zero position")
        Show_Screen.disable_screen_option()
        self.go_home_state = True
        master.execute(SLAVE_02, cst.WRITE_SINGLE_COIL, self.ENABLE_HOME_MODBUS_ADDR, output_value = CHOOSE)
        while True:
            # Đọc trạng thái phát xung đã hoàn tất chưa
            Go_to_Home_done_slave_02 = master.execute(SLAVE_02, cst.READ_COILS, self.EXECUTE_PULSE_DONE, 1)
            # Đọc giá trị thanh ghi lưu giá trị xung đang phát ra
            self.Read_pulse_PWM_from_slaves()
            if (Go_to_Home_done_slave_02[0] == 1):
                self.go_home_state = False
                break  # thoat khỏi vong lặp while
        Show_Screen.enable_screen_option()

# phát lệnh cho các động cơ chạy về vị trí cảm biến: gốc tọa độ máy - machine axis
    def Go_to_machine_axis(self):

        if self.machine_axis == False:
            
            pulse_to_machine_axis_X = [-25600, 0, 0, 0, 0, 0]
            pulse_to_machine_axis_Y = [0, -25600, 0, 0, 0, 0]
            pulse_to_machine_axis_Z = [0, 0, -25600, 0, 0, 0]
            pulse_to_machine_axis_A = [0, 0, 0, -16000, 0, 0]
            pulse_to_machine_axis_B = [0, 0, 0, 0, -12800, 0]
            pulse_to_machine_axis_C = [0, 0, 0, 0, 0, -12800]

            pulse_to_machine_axis = [pulse_to_machine_axis_X, pulse_to_machine_axis_Y, pulse_to_machine_axis_Z, 
                                        pulse_to_machine_axis_A, pulse_to_machine_axis_B, pulse_to_machine_axis_C ]
            pulse_to_begin_position = [12800, 12800, 12800, 12800, 12800, 12800]
            speed_axis = [200,200,200,200,200,200]

            print("Going to machine axis")

            Show_Screen.disable_screen_option()
            # khai báo mảng chứa giá trị cảm biến gốc máy
            self.sensor_machine_axis = [Monitor_in_out.sensor_value[0], Monitor_in_out.sensor_value[1], Monitor_in_out.sensor_value[2],
                                        Monitor_in_out.sensor_value[3], Monitor_in_out.sensor_value[4], Monitor_in_out.sensor_value[5]]
            # set lại các thông số motor, đưa giá trị current_position về 0
            master.execute(SLAVE_02, cst.WRITE_SINGLE_COIL, self.SET_ZERO_POSITION_ADDR, output_value = CHOOSE)

            for i in range(AXIS_RUN):
                Run.send_to_execute_board(pulse_to_machine_axis[i],speed_axis[i])
                self.go_machine_axis_state = False
                while True: 
                    # Đọc giá trị thanh ghi lưu giá trị xung đang phát ra
                    
                    Go_to_machine_axis_done_slave_02 = master.execute(SLAVE_02, cst.READ_COILS, self.EXECUTE_PULSE_DONE, 1)
                    self.Read_pulse_PWM_from_slaves()

                    if (Go_to_machine_axis_done_slave_02[0]==1):
                    #if (self.sensor_machine_axis[i] == 0):  # nếu cảm biến on 
                        # dừng động cơ
                        #master.execute(SLAVE_02, cst.WRITE_SINGLE_COIL, Run.PAUSE_MOTOR_MODBUS_ADDR, output_value = CHOOSE)
                        # set lại các thông số motor, đưa giá trị current_position về 0
                        #master.execute(SLAVE_02, cst.WRITE_SINGLE_COIL, self.SET_ZERO_POSITION_ADDR, output_value = CHOOSE)
                        
                        self.go_machine_axis_state = True
                        break  # thoat khỏi vong lặp while

            # sau khi chạy hết các động cơ về vị trí cảm biến
            # tịnh tiến các trục X,Y,Z ra khỏi vị trí cảm biến và set lại 0
            """"
            time.sleep(2)
            Run.send_to_execute_board(pulse_to_begin_position,100)
            while True:
                self.Read_pulse_PWM_from_slaves()
                # Đọc trạng thái phát xung đã hoàn tất chưa
                Go_to_machine_axis_done_slave_02 = master.execute(SLAVE_02, cst.READ_COILS, self.EXECUTE_PULSE_DONE, 1)
                # Đọc giá trị thanh ghi lưu giá trị xung đang phát ra
                if (Go_to_machine_axis_done_slave_02[0]==1 and Go_to_machine_axis_done_slave_03[0] == 1): 
                    # set lại các thông số motor, đưa giá trị current_position về 0
                    #master.execute(SLAVE_02, cst.WRITE_SINGLE_COIL, self.SET_ZERO_POSITION_ADDR, output_value = CHOOSE)
                    break
            """""
            Show_Screen.enable_screen_option()
            self.machine_axis = True # đã về home

# đọc giá trị tay quay encoder
    def Read_rotary_encoder(self):
        # Đọc giá trị thanh ghi rotary encoder ở địa chỉ bắt đầu từ 20, đọc 2 giá trị 16 bit
        rotaty_encoder_packet = master.execute(SLAVE_02, cst.READ_HOLDING_REGISTERS, self.ROTARY_ENCODER_MODBUS_ADDR , 2)
        counter = ((rotaty_encoder_packet[1] & 65535) | (rotaty_encoder_packet[0] << 16))
        counter = self.check_negative_num(counter)
        return counter
         
# giám sát vị trí các trục tay máy
    def Read_pulse_PWM_from_slaves(self):
        current_position_motor = []
        index = 0
        # Đọc giá trị xung của tất cả động cơ 
        try:
            # Đọc giá trị current position ở địa chỉ bắt đầu từ 0, đọc 12 giá trị 16 bit
            current_position = master.execute (SLAVE_02, cst.READ_HOLDING_REGISTERS, self.CURRENT_POSITION_MODBUS_ADDR, 12)
            for i in range(AXIS_RUN):
                current_position_motor.append((current_position[index] << 16) | (current_position[index+1] & 65535))
                index = index + 2

            # kiểm tra giá trị âm
            self.pwm_value_x_axis = self.check_negative_num(current_position_motor[0])
            self.pwm_value_y_axis = self.check_negative_num(current_position_motor[1])
            self.pwm_value_z_axis = self.check_negative_num(current_position_motor[2])
            self.pwm_value_a_axis = self.check_negative_num(current_position_motor[3])
            self.pwm_value_b_axis = self.check_negative_num(current_position_motor[4])
            self.pwm_value_c_axis = self.check_negative_num(current_position_motor[5])
            
            # lưu giá trị xung cần chạy để về vị trí zero point ở thời điểm hiện tại
            self.pulse_to_home = [-(self.pwm_value_x_axis),-(self.pwm_value_y_axis),-(self.pwm_value_z_axis),
                                  -(self.pwm_value_a_axis),-(self.pwm_value_b_axis),-(self.pwm_value_c_axis)]
            # lưu giá trị xung đã chạy được ở thời điểm hiện tại
            self.current_pulse = [self.pwm_value_x_axis,self.pwm_value_y_axis,self.pwm_value_z_axis,
                                  self.pwm_value_a_axis,self.pwm_value_b_axis,self.pwm_value_c_axis]
            
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

# hien thi so xung
        """"
        self.var1.set(str(self.pwm_value_x_axis)+ " p")
        self.var2.set(str(self.pwm_value_y_axis)+ " p")
        self.var3.set(str(self.pwm_value_z_axis)+ " p")
        self.var4.set(str(self.pwm_value_a_axis)+ " p")
        self.var5.set(str(self.pwm_value_b_axis)+ " p")
        self.var6.set(str(self.pwm_value_c_axis)+ " p")
        """""
# hien thi khoang cach mm/deg  
        #""""
        self.var1.set(str(round(self.pos_X,3))+ " mm")
        self.var2.set(str(round(self.pos_Y,3))+ " mm")
        self.var3.set(str(round(self.pos_Z,3))+ " mm")
        self.var4.set(str(round(self.pos_A,3))+ " deg")
        self.var5.set(str(round(self.pos_B,3))+ " deg")
        self.var6.set(str(round(self.pos_C,3))+ " deg")

        #"""""
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
        
# lấy giá trị tốc độ        
    def Call_speed(self):
        Fspray = Show_Screen.speed_scale.get()
        return Fspray
# tính tốc độ của 6 trục ứng với giá trị xung tương ứng
    def Calculate_speed(self,pwm_value):
        speed_axis  = [0,0,0,0,0,0]     # tốc độ 6 trục
        velocity    = [0,0,0,0,0,0]     # vận tốc 6 trục
        ratio       = [0,0,0,0,0,0]     # tỉ lệ 6 trục so với trục lớn nhất
        abs_ratio   = []
        if ((Teach_mode.teach_state == True) or (self.go_home_state == True)):
            #Fspray = 80
            Fspray = Show_Screen.speed_scale.get()
            if Fspray > 80: Fspray = 80
        else:
            Fspray = Show_Screen.speed_scale.get() # tốc độ sơn, đơn vị mm/s

        index_axis = self.spray_axis*math.sin((self.gear_ratio_A*math.pi)/180)
        # tính giá trị xung lớn nhất trong các trục
        pwm_value_max = max(abs(pwm_value[0]),abs(pwm_value[1]),abs(pwm_value[2]),
                            abs(pwm_value[3]),abs(pwm_value[4]),abs(pwm_value[5]))
        # tính tỉ lệ giá trị xung từng trục so với giá trị xung lớn nhất
        if pwm_value_max != 0:
            for i in range(len(pwm_value)):
                abs_ratio.append(abs(pwm_value[i])/pwm_value_max)
                ratio[i] = abs_ratio[i]
            # nếu trường hợp chỉ có trục B hoặc C quay, các trục còn lại đứng yên
            if (ratio[0] == 0 and ratio[1] == 0 and ratio[2] == 0 and ratio[3] == 0):
                max_speed = 8000
            # tính bình phương của giá trị Fspray
            else:
                Fspray_pow2 = math.pow(Fspray,2) 
                index_Xpow2 = math.pow((ratio[0]*self.gear_ratio_X),2)
                index_Ypow2 = math.pow((ratio[1]*self.gear_ratio_Y),2)
                index_Zpow2 = math.pow((ratio[2]*self.gear_ratio_Z),2) + 2*ratio[2]*ratio[3]*self.gear_ratio_Z*index_axis + math.pow((ratio[3]*index_axis),2)
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
        for i in range(len(speed_axis)):
            speed_axis[i] = ratio[i]*max_speed
        # tính tốc độ trục X,Y,Z của đầu súng sơn theo đơn vị mm/s
        velocity[0] = int(speed_axis[0])*self.gear_ratio_X
        velocity[1] = int(speed_axis[1])*self.gear_ratio_Y
        velocity[2] = int(speed_axis[2])*self.gear_ratio_Z + int(speed_axis[3])*index_axis
        speed_XYZ_spray = math.sqrt(math.pow(velocity[0],2) + math.pow(velocity[1],2) + math.pow(velocity[2],2))
        print("F spray = " + str(round(speed_XYZ_spray)) + " mm/s")
        print("------------------------------------")
        return speed_axis
#========================================================================
#========================================================================
class Teach_mode_class():
    def __init__(self):
        self.TEACH_X_AXIS_MODBUS_ADDR = 0
        self.TEACH_Y_AXIS_MODBUS_ADDR = 1
        self.TEACH_Z_AXIS_MODBUS_ADDR = 2
        self.TEACH_A_AXIS_MODBUS_ADDR = 3
        self.TEACH_SPRAY_AXIS_MODBUS_ADDR = 4
        self.TEACH_CHAIR_AXIS_MODBUS_ADDR = 5

        self.DISABLE_ROTARY_ENCODER_ADDR = 13
        self.ENABLE_ROTARY_ENCODER_ADDR = 14

        self.SPRAY_ON_MODBUS_ADDR = 6
        self.teach_state = False
        self.Save_point = False
        self.spray_var = StringVar()
        self.spray_var.set('0') # súng sơn: 0 - off; 1 - on
        self.gain_rotary_encoder = 100 # giá trị xung mặc định khi quay rotary encoder

        self.no_choise_axis = -1
        self.teach_axis = -1   # biến lựa chọn trục cần chạy trong teach mode
        self.TEACH_X_AXIS = 0  # teach trục X
        self.TEACH_Y_AXIS = 1  # teach truc Y
        self.TEACH_Z_AXIS = 2  # teach truc Z
        self.TEACH_A_AXIS = 3  # teach trục A
        self.TEACH_B_AXIS = 4  # teach trục B
        self.TEACH_C_AXIS = 5  # teach trục C
        self.TEACH_Z1_AXIS = 6  # teach trục C

        self.button_encoder = 0; self.pre_button_encoder = 0
        self.Init_string_value()

    def Init_string_value(self):
        self.pre_string_value = [(' X'+'0.0'),(' Y'+'0.0'),(' Z'+'0.0'),(' A'+'0.0'),(' B'+'0.0'),(' C'+'0.0'),
                                 (' S'+'0'),(' F'+'0')]
        self.counter_line = 0

    def Enable_teach_options(self):
        print("enable teach options")
        try:
            Show_Screen.enable_teach_option()
            Show_Screen.enable_button_teach(100)
            Show_Screen.enable_resolution_button(100)
            Show_Screen.disable_screen_option()
            Show_Screen.disable_button_control(0)
            Show_Screen.disable_button_control(1)
            
            self.gain_rotary_encoder = 100 # giá trị xung mặc định khi quay rotary encoder
            self.teach_state = True
            # xóa nội dung trong text_box
            Show_Screen.Show_content.delete('1.0','end')
            Show_Screen.Show_content.config(state = NORMAL)
            # bật tay quay rotary encoder
            # master.execute(SLAVE_02, cst.WRITE_SINGLE_COIL, self.ENABLE_ROTARY_ENCODER_ADDR, output_value = CHOOSE)
            # bật monitor số xung
            #Monitor_mode.Monitor_pulse_in_teach_mode_01()
            Monitor_mode.Monitor_pulse_in_teach_mode_02()
        except Exception as e:
            print(str(e))
            return

    def Disable_teach_options(self):
        print("disable teach options")
        self.Spray_off()
        Show_Screen.disable_teach_option()
        Show_Screen.disable_button_teach()
        Show_Screen.enable_screen_option()
        Show_Screen.disable_resolution_button()
        Show_Screen.enable_button_control(0)
        Show_Screen.enable_button_control(1)

        self.Init_string_value()
        self.teach_state = False
        # xóa nội dung trong text_box, trả giá trị đếm số dòng về 0
        Show_Screen.Show_content.delete('1.0','end')
        Show_Screen.Show_content.config(state = DISABLED)
        # tắt tay quay rotary encoder
        # master.execute(SLAVE_02, cst.WRITE_SINGLE_COIL, self.DISABLE_ROTARY_ENCODER_ADDR, output_value = CHOOSE)
        # tắt monitor xung
        Monitor_mode.monitor_off = True

# Lấy các giá trị của các trục tay máy để hiện thị lên Show_content
    def Show_point_to_textbox(self):

        show_line = (' '+ str(self.counter_line))
        different_value = False
        # lay gia tri
        F_speed = int(Show_Screen._speed_value.get())
        X_value = round(Monitor_mode.pos_X,3); Y_value = round(Monitor_mode.pos_Y,3); Z_value = round(Monitor_mode.pos_Z,3)
        A_value = round(Monitor_mode.pos_A,3); B_value = round(Monitor_mode.pos_B,3); C_value = round(Monitor_mode.pos_C,3)
        Spray_state = self.spray_var.get()

        if  F_speed < 0: F_speed = 0
        if  F_speed > 200: F_speed = 200

        current_string_value = [(' X'+str(X_value)), (' Y'+str(Y_value)), (' Z'+str(Z_value)), (' A'+str(A_value)), 
                                (' B'+str(B_value)),(' C'+str(C_value)), (' S'+str(Spray_state)), (' F'+str(F_speed))]
        # print("gia tri cac thong so: ",current_string_value)
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
            show_line = show_line + '\n'
            self.counter_line += 1
            Show_Screen.Show_content.insert(END,show_line) 
            Show_Screen.Show_content.yview(END)
    
    def Teach_X_Axis(self):
        Show_Screen.enable_button_teach(0)
        self.teach_axis = self.TEACH_X_AXIS
        print("chọn trục X")

    def Teach_Y_Axis(self):
        Show_Screen.enable_button_teach(1)
        self.teach_axis = self.TEACH_Y_AXIS
        print("chọn trục Y")

    def Teach_Z_Axis(self):
        Show_Screen.enable_button_teach(2)
        self.teach_axis = self.TEACH_Z_AXIS
        print("chọn trục Z")

    def Teach_A_Axis(self):
        Show_Screen.enable_button_teach(100)
        self.teach_axis = self.TEACH_A_AXIS
        print("chọn trục A")

    def Teach_B_Axis(self):
        Show_Screen.enable_button_teach(3)
        self.teach_axis = self.TEACH_B_AXIS
        print("chọn trục B")

    def Teach_C_Axis(self):
        Show_Screen.enable_button_teach(4)
        self.teach_axis = self.TEACH_C_AXIS
        print("chọn trục C")
#=============================================================
    def Table_fw(self):
        Show_Screen.enable_button_teach(0)
        Run.command_table_rotate()
        print("Xoay bàn sơn lần 1")

    def Table_rw(self):
        Show_Screen.enable_button_teach(1)
        Run.command_table_rotate()
        print("Xoay bàn sơn lần 2")
    
    def Spray_on(self):
        Show_Screen.enable_button_teach(2)
        self.spray_var.set('1')
        Run.command_run_spray(1)
        print("Bật phun sơn")

    def Spray_off(self):
        Show_Screen.enable_button_teach(3)
        self.spray_var.set('0')
        Run.command_run_spray(0)
        print("Tắt phun sơn")
#=============================================================
    def X1_resolution(self):
        Show_Screen.enable_resolution_button(0)
        self.gain_rotary_encoder = 1
        print("chọn độ phân giải x1")
    
    def X10_resolution(self):
        Show_Screen.enable_resolution_button(1)
        self.gain_rotary_encoder = 10
        print("chọn độ phân giải x10")

    def X100_resolution(self):
        Show_Screen.enable_resolution_button(2)
        self.gain_rotary_encoder = 100
        print("chọn độ phân giải x100")
    
    def X1000_resolution(self):
        Show_Screen.enable_resolution_button(3)
        self.gain_rotary_encoder = 1000
        print("chọn độ phân giải x1000")

    def Save_file(self):
        print('Save execute file.pnt')
        Work_file.save_file()
# set 0 cho các trục theo hệ tọa độ tương đối G54
    def Set_zero_position(self):
        print('SET ZERO X,Y,Z,A,B,C')
        Monitor_mode.offset_x_axis = Monitor_mode.pos_X
        Monitor_mode.offset_y_axis = Monitor_mode.pos_Y
        Monitor_mode.offset_z_axis = Monitor_mode.pos_Z
        Monitor_mode.offset_a_axis = Monitor_mode.pos_A
        Monitor_mode.offset_b_axis = Monitor_mode.pos_B
        Monitor_mode.offset_c_axis = Monitor_mode.pos_C

        master.execute(SLAVE_02, cst.WRITE_SINGLE_COIL, Monitor_mode.SET_ZERO_POSITION_ADDR, output_value = CHOOSE)

        # lưu vị trí set 0 
#========================================================================  
class Com_box():
    def __init__(self):
        self.comports = []
        self.choose_COM = Combobox()

    def detect_comports(self):
        comports = []
        portdata = serial.tools.list_ports_windows.comports()
        for i in range(len(portdata)):
            port = portdata[i]
            str_port = str(port) 
            split_port = str_port.split(" ")
            comports.append(split_port[0])
        return comports   

    def get_comports(self):
        self.comports = self.detect_comports()
        self.choose_COM.set('')
        self.choose_COM['value'] = self.comports

    def show_comunication_box(self):
        self.Frame2 = LabelFrame(root)
        self.Frame2.place(x = 650, y = 630)
        bg_frame2 = Canvas(self.Frame2, bg= "#333333", height=50, width=200,  relief = GROOVE, borderwidth = 0)
        bg_frame2.pack(side = LEFT)
        #========================================================================
        Label(self.Frame2,text = 'COM',fg ='black', justify = LEFT).place(x=10, y=15)
        self.choose_COM = Combobox(self.Frame2, width = 10,state='readonly')
        self.choose_COM.place(x=50, y=15)
        self.get_comports()
        self.refresh_comports()

    def refresh_comports(self):
        reset_button = Button(self.Frame2, text = 'Refresh', activebackground = 'green', fg ='black',bg = "white",
                                command = self.get_comports)
        reset_button.place(x = 140, y = 13)

    def go_home(self):
        self.Home_mode = Button(root, image = button_01, relief = GROOVE, borderwidth= 0,
                    activebackground = 'green',  bg = "#999999",
                       command = Home.Go_Home) 
        self.Home_mode.place(x = 550, y = 300)
#==============================================================================================================
class Run_auto():
    def __init__(self):

        self.TABLE_CHANGE_STATE_MODBUS_ADDR = 4
        self.SPRAY_OFF_MODBUS_ADDR = 5
        self.SPRAY_ON_MODBUS_ADDR = 6
        self.POINT2POINT_MODBUS_ADDR = 7
        self.PAUSE_MOTOR_MODBUS_ADDR = 8
        self.RESUME_MOTOR_MODBUS_ADDR = 9
        self.SAVE_PACKET_DATA_MODBUS_ADDR = 10
        self.CHANGE_STATE_RUN_BLOCK_MODBUS_ADDR = 11

        self.sum_xung_le = [0,0,0,0,0,0]
        self.pause_on = 0
        self.state_spray = 0; self.new_state_spray = 0
        self.pre_result_value = [0,0,0,0,0,0,0,0]
        self.pre_points = [0,0,0,0,0,0]
        self.gear = [Monitor_mode.gear_ratio_X, Monitor_mode.gear_ratio_Y, Monitor_mode.gear_ratio_Z, 
                    Monitor_mode.gear_ratio_A, Monitor_mode.gear_ratio_B, Monitor_mode.gear_ratio_C]
        self.old_Fspeed = 0; self.new_Fspeed = 0
        self.run_auto_mode = False          # trạng thái vào chế độ auto run
        self.counter = 0                    # lưu tổng số điểm đã truyền tới data_packet slave để chạy block mode
    
        self.MAX_POINT_IN_BLOCK = 140       # số điểm tối đa có thể truyền tới data_packet slave trong block mode
        self.end_symbol = 'M30\n'           #command kết thúc chương trình
        self.start_run_block = 'G05.0\n'    #command bắt đầu chạy theo block N điểm
        self.end_run_block = 'G05.1\n'      #command kết thúc chạy theo block N điểm
        self.go_to_2nd_point = 'G30\n'      #command quay về điểm gốc thứ 2
        self.go_to_1st_point = 'G28\n'      #command quay về vị trí gốc 0 (điểm bắt đầu chạy)
        self.turn_on_spray = 'M08\n'        #command lệnh bật súng sơn
        self.turn_off_spray = 'M09\n'       #command lệnh tắt súng sơn
        self.table_rotary = 'M10\n'         #command xoay bàn sơn
        self.run_block_done = False

        self.e_stop = False                 # trạng thái tín hiệu nút nhấn ESTOP
#=============================================================
    def activate_run_mode(self):
        try:
            position = Work_file._file.seek(0,0) # Di chuyen con tro vi tri read file ve vi tri đầu file
            Show_Screen.disable_screen_option()
            Show_Screen.disable_button_control(0)
            self.run_auto_mode = True
            
            for str_content in Work_file._file:
                if self.e_stop == True: # nếu có tín hiệu nhấn E-STOP
                    break

                print ('========================================================================')
                content_line = str_content.replace(" ", "") # Bo ky tu khoang trang trong chuoi
                print(content_line)
                content_line = content_line.upper()         # chuyen doi chuoi thanh chu IN HOA
                self.Monitor_str_content(str_content)  # hiện thị từng dòng trong file
                Recognize_stringArr = self.Recognize_command_syntax(content_line)   # Kiểm tra các ký tự đúng cú pháp hay không

                if Recognize_stringArr == True:
                    # tách số của các trục
                    result_string = self.separate_string(content_line)
                    # tính toán khoảng cách cần tịnh tiến
                    result_delta = self.calculate_delta(result_string)
                    # tính toán số xung tịnh tiến
                    result_xung_nguyen = self.calculate_pulse(result_delta)
                    # gửi khoảng cách theo đơn vị xung và tốc độ tới board execute
                    self.send_to_execute_board(result_xung_nguyen, self.new_Fspeed)
                    self.command_run_point2point()  # phát lệnh chạy mode point to point bình thường
                    self.monitor_run_auto_next()    # giám sát chạy lệnh point to point 
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
                        Monitor_mode.Go_to_zero_position()

                    if content_line == self.go_to_2nd_point: # đi tới điểm gốc thứ 2
                        pass
                    
                    if content_line == self.start_run_block:
                        print("=====> G05.0 START BLOCK RUN MODE")
                        result_run_block = self.send_packet_to_slave()  # giá trị trả về luôn trong khoảng [0:140]
                        if result_run_block == False: 
                            print("=====> G05.1 Error !!!")
                            break
                        else: 
                            # gửi lần 2 lệnh change_state_run_block để tắt chế độ run block mode
                            print("BLOCK RUN MODE DONE")
                            self.counter = 0

        except Exception as e:
                print('activate_run_mode error: ',str(e))
                messagebox.showinfo("Run Auto", "Error: ")

        finally:
            print ('========================================================================')
            self.re_init()
            print("--------------------------------------------------------------------------")
            print("END")

#=============================================================
# gui N packet tới board slave, hàm trả về số điểm đã gửi tới board slave            
    def send_packet_to_slave(self):
        sent_packet_done = False
        sent_point = 0
        target_line = ' '
        run_block = False

        for str_content in Work_file._file:
            print ('========================================================================')
            content_line = str_content.replace(" ", "") # Bo ky tu khoang trang trong chuoi
            print(content_line)
            content_line = content_line.upper()     # chuyen doi chuoi thanh chu IN HOA
            Recognize_stringArr = self.Recognize_command_syntax(content_line)   # Kiểm tra các ký tự đúng cú pháp hay không

            if Recognize_stringArr == True:
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
                print("=====> G05.1 END BLOCK RUN MODE")
                self.Monitor_str_content(target_line)  # hiện thị điểm đến cuối cùng trong block data đã chuyển đi   

                if 0 < sent_point <= self.MAX_POINT_IN_BLOCK:  # kiểm tra trường hợp 2
                    # cho chạy auto 
                    print("=====> START BLOCK RUN MODE - POINT NUMBER: ",sent_point)
                    self.send_end_run_block_mode()
                    self.monitor_run_block_begin()
                    run_block = self.run_block_done
                break
                # thoát khỏi vòng lặp for 

        return run_block

#=============================================================
# chay block point đã gửi tới board slave
    def monitor_run_block_begin(self):
        self.run_block_done = False
        self.pause_on = 0
        master.execute(SLAVE_02, cst.WRITE_SINGLE_COIL, self.CHANGE_STATE_RUN_BLOCK_MODBUS_ADDR, output_value = CHOOSE)
        
        while True:
            point_done_slave_02 = master.execute(SLAVE_02, cst.READ_COILS, Monitor_mode.EXECUTE_PULSE_DONE, 1)
            Monitor_mode.Read_pulse_PWM_from_slaves()

            if point_done_slave_02[0] == 1: # slave đã chạy xong hết block
                self.run_block_done = True
                break

            if self.pause_on == 1: # dừng motor
                master.execute(SLAVE_02, cst.WRITE_SINGLE_COIL, self.PAUSE_MOTOR_MODBUS_ADDR, output_value = CHOOSE)
                        
            if self.pause_on == 2: # tiếp tục chạy
                master.execute(SLAVE_02, cst.WRITE_SINGLE_COIL, self.RESUME_MOTOR_MODBUS_ADDR, output_value = CHOOSE)
                self.pause_on = 0

#=============================================================
    def monitor_run_auto_next(self):
        self.pause_on = 0

        while True:
            point_done_slave_02 = master.execute(SLAVE_02, cst.READ_COILS, Monitor_mode.EXECUTE_PULSE_DONE, 1)
            Monitor_mode.Read_pulse_PWM_from_slaves()

            if point_done_slave_02[0] == 1: 
                break

            if self.pause_on == 1: # dừng motor
                master.execute(SLAVE_02, cst.WRITE_SINGLE_COIL, self.PAUSE_MOTOR_MODBUS_ADDR, output_value = CHOOSE)
                        
            if self.pause_on == 2: # tiếp tục chạy
                master.execute(SLAVE_02, cst.WRITE_SINGLE_COIL, self.RESUME_MOTOR_MODBUS_ADDR, output_value = CHOOSE)
                self.pause_on = 0
     
#=============================================================
# gửi mã thoát khỏi chế độ run block point tới board slave
    def send_end_run_block_mode(self):
        send_to_slave_id2 = []
        pulse_end = [0,0,0,0,0,0]
        speed_end = -1

        # lưu giá trị xung để truyền đi
        for i in range(AXIS_RUN):
            send_to_slave_id2.append(pulse_end[i] >> 16)
            send_to_slave_id2.append(pulse_end[i] & 65535)
        # lưu giá trị tốc độ truyền đi
        send_to_slave_id2.append(speed_end >> 16)
        send_to_slave_id2.append(speed_end & 65535)
        master.execute(SLAVE_02, cst.WRITE_MULTIPLE_REGISTERS, 0, output_value = send_to_slave_id2)

        self.save_to_packet_data()

#=============================================================
# Dừng chương trình chạy auto
    def disable_run_mode(self):
        if self.run_auto_mode == True:
            Monitor_in_out.stop_motor() # dừng motor khẩn cấp
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

            self.new_state_spray = int(result_value[6])     # trạng thái coil súng sơn
            self.new_Fspeed = int(result_value[7])          # tốc độ sơn

        except Exception as e:
            print('separate_string error:', str(e))
            return
        return result_value

# tính khoảng cách giữa các điểm theo đơn vị xung
    def calculate_delta(self,result_array):
    # result_array là mảng chứa kết quả của hàm separate_string    
    # tính giá trị xung tịnh tiến
        print('Giá trị X,Y,Z,A,B,C,S,F là:',result_array)
        print('giá trị pre_points: ', self.pre_points)
        result_value    = []
        delta           = []
        print_delta     = []
        for i in range(len(self.pre_points)):
            delta.append(float(result_array[i])- self.pre_points[i])
            self.pre_points[i] = float(result_array[i])
            result_value.append(float(delta[i])/self.gear[i])
            print_delta.append(round(delta[i],3))

        print('Gia tri delta cua X,Y,Z,A,B,C là:', print_delta)
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
        print("------------------------------------")
        print ('>>> Gia tri xung x,y,z,a,b,c chua calib lan luot la: ',print_delta_array)
        print ('>>> So xung nguyen truc x,y,z,a,b,c: ',xung_nguyen)
        print ('>>> So xung le truc x,y,z,a,b,c:     ',xung_le)
        print("------------------------------------")
        return xung_nguyen

#-------------------------------------------------------
# truyền giá trị xung và tốc độ x,y,z,a,b,c tới board execute; giá trị 32 bit
    def send_to_execute_board(self, pulse, _speed):
        send_to_slave_id2 = [] # gói giá trị 16 bit

        # tính tốc độ của trục x,y,z,a,b,c
        if _speed <= 30:
            speed_slaves = Monitor_mode.Call_speed()
        else: speed_slaves = _speed

        print("toc do chay dong co: ",int(speed_slaves),"%")
        print("gia tri packet xung pulse: ",pulse) 
            # tách giá trị 32 bit thành packets 16 bit để gửi đến slaves
       
        # lưu giá trị xung để truyền đi
        for i in range(AXIS_RUN):
            send_to_slave_id2.append(pulse[i] >> 16)
            send_to_slave_id2.append(pulse[i] & 65535)
        # lưu giá trị tốc độ truyền đi
        send_to_slave_id2.append(speed_slaves >> 16)
        send_to_slave_id2.append(speed_slaves & 65535)

        # gửi số xung x,y,z,a,b,c,speed cần chạy tới board slave id 2, gửi 14 word, bắt đầu từ địa chỉ 0
        master.execute(SLAVE_02, cst.WRITE_MULTIPLE_REGISTERS, 0, output_value = send_to_slave_id2)
      
        if self.run_auto_mode == False:
        # phát command tới board slave chạy đến điểm đã gửi
            self.command_run_point2point()
#-------------------------------------------------------
    def command_run_point2point(self):
# phát lệnh đến board id 2 và id 3 bắt đầu chạy điểm point to point
        master.execute(SLAVE_02, cst.WRITE_SINGLE_COIL, self.POINT2POINT_MODBUS_ADDR, output_value = CHOOSE)
#-------------------------------------------------------   
# command bật tắt súng sơn 
    def command_run_spray(self, state):
        if state:
            master.execute(SLAVE_02, cst.WRITE_SINGLE_COIL, self.SPRAY_ON_MODBUS_ADDR, output_value = state)
            Show_Screen.spray_on_state.config(bg = "green", text = 'SPRAY ON')
        else:
            master.execute(SLAVE_02, cst.WRITE_SINGLE_COIL, self.SPRAY_OFF_MODBUS_ADDR, output_value = state)
            Show_Screen.spray_on_state.config(bg = "gray", text = 'SPRAY OFF')
#-------------------------------------------------------    
# command xoay bàn sơn
    def command_table_rotate(self):
        master.execute(SLAVE_02, cst.WRITE_SINGLE_COIL, self.TABLE_CHANGE_STATE_MODBUS_ADDR, output_value = CHOOSE)
        print("Xoay bàn sơn")

#-------------------------------------------------------            
    def pause_motor(self):
# phát lệnh dừng tay máy
        self.pause_on += 1
        print("pause")

# gửi index packet data tới slaves khi nhấn auto
    def save_to_packet_data(self):
        master.execute(SLAVE_02, cst.WRITE_SINGLE_COIL, self.SAVE_PACKET_DATA_MODBUS_ADDR, output_value = CHOOSE)
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
        Show_Screen.enable_button_control(0)

# Hiện thị từng dòng đang chạy trong file lên label
    def Monitor_str_content(seft, string):
        Show_Screen.string_content.set(string)
        Show_Screen.label_axis_monitor.update()

# Nhận diện dòng thỏa cú pháp trong file
    def Recognize_command_syntax(self, StringArr):
        if StringArr == '\0' or StringArr == '\n':
            print("Ky tu khong dung systax: ",StringArr)
            Recognize_command = False
            return Recognize_command
        Recognize_command = True
        RecognizeChar = ['0','1','2','3','4','5','6','7','8','9', 
                         'X', 'Y', 'Z', 'A', 'B', 'C', 'S', 'F', '.', '-', '\n', '\0']
        for char in StringArr:
            if char in RecognizeChar[0:]: 
                pass
            else:
              Recognize_command = False
              print("Ky tu khong dung systax: ",StringArr)
              break
        return Recognize_command
#==============================================================================================================
# Hiện thị backgrough và thông tin máy
def Show_machine_infor():
    Frame10 = LabelFrame(root)
    Frame10.place(x = 10, y = 10)
    bg_frame10 = Canvas(Frame10, bg="green", height=120, width=1500, bd = 1)
    bg_frame10.pack(side = LEFT)

    Machine_infor = Label(Frame10,text = 'KHOI NGUYEN PLASTIC.JSC \n AUTOMATIC CHAIR PAINTING MACHINE',
                            font = ("Arial",33,"bold"), fg ='black', justify = CENTER, bg = 'green')
 
    Machine_infor.place(x=350, y=10)

    Frame20 = LabelFrame(root)
    Frame20.place(x = 10, y = 135)
    bg_frame20 = Canvas(Frame20, bg="#333333", height=650, width=1500, bd = 1)
    bg_frame20.pack(side = LEFT)

    Name_infor = Label(Frame20,text = 'Royal Robotics \n Designer: KHANH.N.Q',fg ='black',
                font = ("Arial",16,"bold"), justify = CENTER, bg = 'yellow', bd = 1, relief = 'solid')
    Name_infor.place(x=2, y=600)

    ComunicationRobot.show_comunication_box()
    ComunicationRobot.go_home()
#========================================================================
#========================================================================
def creat_threading():
    monitor_coil = threading.Thread(name='monitor_coil', target=Monitor_in_out.monitor_coil_XY)
    monitor_coil.setDaemon(True)
    monitor_coil.start()
#========================================================================
Show_Screen = Screen()
Monitor_mode = Monitor_Position_Class()
Monitor_in_out = Monitor_Input_Output()
Teach_mode = Teach_mode_class()
Send_to_Serial = Read_Write_to_Serial()
Home = Home_position()
ComunicationRobot = Com_box()
Work_file = Save_file()
Run = Run_auto()
Show_status = Terminal()
#========================================================================
Show_machine_infor()
#========================================================================
root.mainloop()