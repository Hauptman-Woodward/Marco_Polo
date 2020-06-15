from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QBrush, QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QGridLayout

from polo.ui.designer.UI_settings import Ui_Settings
from polo.utils.ftp_utils import list_dir, logon

# TODO: Downloading function and reflect files in the actual FTP server
# Probably want to look into threads for downloading so not being done on
# the GUI thread

class SettingsDialog(QtWidgets.QDialog):


    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        self.ui = Ui_Settings()
        self.ui.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.exec_()
    
    def validate_shortcut(self):
        pass
    # makes sure shortcut isnt already taken
    
    def change_shortcuts(self):
        pass
    # changes shortcuts in the main window to reflect what is
    # in settings
    
    def read_current_shortcuts(self, window):
        pass
    # reads current shortcuts fromn the given window
    
    def read_current_settings(self):
        # read current settings stored in mainwindow object
        # read the shorcuts directly from the buttons in main
        # not the dictionart
        pass
