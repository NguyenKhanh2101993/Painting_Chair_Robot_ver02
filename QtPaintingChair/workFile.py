import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog as myfile
from PyQt5.QtWidgets import QWidget

#class Ui_workingFile(object):
#    def setupUi(self, workingfile):


class workingFile:  
    # hiển thị đường dẫn tới file trong lable directory
    def __init__(self):
        #self.fileDirectory = ''
        self.saveFileDirectory = ''
        self.saveFileStatus = ''
        self._myfile = QWidget()
        #self.fname = ["",""]

    def show_initial_directory(self):
        self.fname, _ = myfile.getOpenFileName(caption = 'Open file', directory = '/home/orangepi/filePNT',filter = 'pnt files (*.pnt)')
        if not self.fname:
            return
        #if self.fname != '':
        else: 
            fileDirectory = self.fname
            return fileDirectory
   
    # lấy nội dung file hiện thị lên brower text lable
    def get_file(self, path):
        self.file = open(path, 'r')
        text = self.file.read()
        return text
     

    def save_file(self, content):
        self.savefilePath, _ = myfile.getSaveFileName(caption = 'Save file', directory =  '/home/orangepi/filePNT',filter = 'pnt files (*.pnt)')
        #if not self.savefilePath:
        #    return
        #else:
        self.saveFileDirectory = self.savefilePath
        try:
            with open(self.savefilePath, 'w+') as f:
                f.write(content)  # retrieve_text phải là các ký tự không có dấu.
                f.close()

            self.saveFileStatus = ("- save file done")
        except Exception as err:
            self.saveFileStatus = ("- save file error: "+ str(err))
            return
