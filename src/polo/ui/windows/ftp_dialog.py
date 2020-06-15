from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QBrush, QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QGridLayout
from polo.ui.designer.UI_FTP_Dialog import Ui_FTPDialog
from polo.utils.ftp_utils import logon, list_dir
import os
from polo import make_default_logger, ICON_DICT
import ftplib
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from polo.threads.thread import FTPDownloadThread


# TODO: Downloading function and reflect files in the actual FTP server
# Probably want to look into threads for downloading so not being done on
# the GUI thread

logger = make_default_logger(__name__)

class FTPDialog(QtWidgets.QDialog):

    FTP_HOSTS = ['ftp.hwi.buffalo.edu']
    DOWNLOAD_ICON = str(ICON_DICT['download'])
    CONNECTED_ICON = str(ICON_DICT['connected'])
    DISCONNECTED_ICON = str(ICON_DICT['disconnected'])

    def __init__(self, ftp_connection=None):
        QtWidgets.QDialog.__init__(self)
        self.ui = Ui_FTPDialog()
        self.ui.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.ui.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.ui.pushButton_2.clicked.connect(self.download_selected_files)
        self.ui.pushButton.clicked.connect(self.connect_ftp)
        self.ftp = ftp_connection
        self.download_files = None
        self.save_dir = None
        self.home_dir = None

        self.ui.pushButton_2.setIcon(QIcon(self.DOWNLOAD_ICON))

        logger.info('Opened FTP Dialog')
        self.exec_()

    def connect_ftp(self):
        username, password = self.read_username(), self.read_password()
        if username and password:
            self.ui.fileBrowser.clear()
            QApplication.setOverrideCursor(Qt.WaitCursor)
            self.ftp = logon(host=self.FTP_HOSTS[0], username=username,
                            password=password)
            if isinstance(self.ftp, ftplib.FTP):
                self.home_dir = self.ftp.pwd()
                self.ui.fileBrowser.grow_tree_using_mlsd(self.ftp, self.home_dir)
                logger.info('Connected to FTP server')
                self.set_connection_status(connected=True)
            else:
                QApplication.restoreOverrideCursor()
                m = self.make_message_box(message='Connection Failed: {}'.format(
                    self.ftp), buttons=QtWidgets.QMessageBox.Ok)
                logger.info('FTP connection failed with code {}'.format(
                    self.ftp
                ))
                self.set_connection_status(connected=False)
                m.exec_()
        QApplication.restoreOverrideCursor()
    
    def set_connection_status(self, connected=False):
        if connected:
            self.ui.label_3.setText('Connected')
        else:
            self.ui.label_3.setText('Disconnected')

        # want to return the error message as some kind of flash

    def download_selected_files(self):
        file_dlg = QtWidgets.QFileDialog()
        file_dlg.setFileMode(QtWidgets.QFileDialog.Directory)
        file_dlg.exec_()
        filenames = file_dlg.selectedFiles()
        if filenames:
            self.save_dir = filenames[0]
            self.download_files = self.ui.fileBrowser.get_checked_files(
                self.home_dir)
            message = 'Your files are being downloaded to {} in the background. Polo will notify you when the download is completed. This window will now close.'.format(
                self.save_dir)
            start_box = self.make_message_box(
                message, buttons=QtWidgets.QMessageBox.Ok)
            start_box.exec_()
            logger.info('Attempting to download over FTP to {}'.format(
                self.save_dir))
            self.close()

    # will need to open dialog to browse directory to place downloads in

    def read_password(self):
        return self.ui.lineEdit_2.text()

    def read_username(self):
        return self.ui.lineEdit.text()

    def make_message_box(self, message, icon=QtWidgets.QMessageBox.Information,
                         buttons=None, connected_function=None):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(icon)
        msg.setText(message)
        msg.setStandardButtons(buttons)
        if connected_function:
            msg.buttonClicked.connect(connected_function)
        return msg
