import json
import os

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QBrush, QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QGridLayout
from polo.designer.UI_log_dialog import Ui_LogDialog

from polo import LOG_PATH


class LogDialog(QtWidgets.QDialog):
    '''Small dialog for displaying the contents of the Polo log file
    '''

    def __init__(self):

        QtWidgets.QDialog.__init__(self)
        self.ui = Ui_LogDialog()
        self.ui.setupUi(self)
        #self.ui.pushButton_2.clicked.connect(self.save_log_file)
        self.ui.pushButton.clicked.connect(self.clear_log)
        self.ui.pushButton_3.clicked.connect(self.close)
        
        self.display_log_text()
        self.exec_()
    
    def display_log_text(self):
        '''Opens the log file and writes the contents to textBrowser widget
        for display to the user.
        '''
        with open(str(LOG_PATH), 'r') as log_file:
            log_contents = log_file.read()
            self.ui.textBrowser.setText(log_contents)
    
    def save_log_file(self):
        '''Saves the current log file contents to a new location.
        '''
        dir_dialog = QtWidgets.QFileDialog()
        dir_dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        dir_name = dir_dialog.getSaveFileName()[0]
        
        if dir_name:  # need more error checking here
            log_file_path = os.path.join(dir_name, 'polo.log')
            self.log.write_log_to_file(log_file_path)
    
    def clear_log(self):
        '''Deletes the contents of the log file.
        '''
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText('Are you sure you want to clear the log? All contents will be deleted forever.')
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        choice = msg.exec_()
        if choice == 1024:  # int code for ok button
            new_log = open(str(LOG_PATH), 'w')
            new_log.close()
            self.display_log_text()  # update the log view to show cleared
            # overwrite the current log contents

            

        
        