import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog as myfile

class workingFile:  
    # hiển thị đường dẫn tới file trong lable directory
    def __init__(self):
        self.fileDirectory = ''

    def show_initial_directory(self):
        fname = myfile.getOpenFileName(caption = 'Open file', directory = 'C:\\',filter = 'pnt files (*.pnt)')
        if fname[0] != '':
            self.fileDirectory = fname[0]
        return self.fileDirectory
   
    # lấy nội dung file hiện thị lên brower text lable
    def get_file(self, path):
        with open(path,'r') as self.file:
                text = self.file.read()
        return text

    def save_file(self, content):
        pass

"""""
    def save_file(self):
  
        retrieve_text = Show_Screen.Show_content.get('1.0','end-1c')
        savefile = filedialog.asksaveasfile(mode='w+', defaultextension='*.pnt', filetypes =[('file pulse', '*.pnt')])
        try:
            savefile.write(retrieve_text)  # retrieve_text phải là các ký tự không có dấu.
            savefile.close()
            Show_Screen.Inform_App_Status("SAVED")
            
        except Exception as err:
            print(str(err))
            return

"""