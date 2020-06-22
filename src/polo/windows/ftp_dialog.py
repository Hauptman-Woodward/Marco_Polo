from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QBrush, QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QGridLayout
from polo.designer.UI_FTP_Dialog import Ui_FTPDialog
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
    
    @property
    def host(self):
        '''Get user entered FTP host

        :return: host address
        :rtype: string
        '''
        return self.ui.lineEdit_3.text()
    
    @property
    def password(self):
        '''Return user entered password

        :return: password
        :rtype: str
        '''
        return self.ui.lineEdit_2.text()
    
    @property
    def username(self):
        '''Return username

        :return: username
        :rtype: str
        '''
        return self.ui.lineEdit.text()


    def connect_ftp(self):
        '''Attempt to establish connection to ftp server. If the connection is
        successful then recursively walk through the user's home directory
        and display available directories and files to the user via the
        fileBrowser widget. If the user has an extremely large number of
        files this can take a while. If the connection fails show the user
        the error code thrown by ftplib.
        '''
        if self.host:
            self.ui.fileBrowser.clear()
            QApplication.setOverrideCursor(Qt.WaitCursor)
            self.ftp = logon(host=self.host, username=self.username,
                             password=self.password)
            if isinstance(self.ftp, ftplib.FTP):
                try:
                    self.home_dir = self.ftp.pwd()
                    self.ui.fileBrowser.grow_tree_using_mlsd(self.ftp, self.home_dir)
                    logger.info('Connected to FTP server')
                    self.set_connection_status(connected=True)
                    self.make_message_box(
                        message='Connected to {}! They say {}'.format(
                        self.host,
                        self.ftp.getwelcome())
                    ).exec_()
                    QApplication.restoreOverrideCursor()
                except Exception as e:
                    QApplication.restoreOverrideCursor()
                    self.make_message_box(
                        message='After connecting to {}. This error occured {}'.format(
                            self.host, e
                        ).exec_()
                    )
                    self.set_connection_status(connected=False)
            
            else:
                QApplication.restoreOverrideCursor()
                m = self.make_message_box(message='Connection Failed: {}'.format(
                    self.ftp), buttons=QtWidgets.QMessageBox.Ok)
                logger.info('FTP connection failed with code {}'.format(
                    self.ftp
                ))
                self.set_connection_status(connected=False)
                m.exec_()
        else:
            QApplication.restoreOverrideCursor() 
            self.make_message_box(
                message='Please enter a host to connect to'
            ).exec_()

    
    def set_connection_status(self, connected=False):
        '''Change the Qlabel that displays the current connection status
        to the user

        :param connected: If FTP confection is successful, defaults to False
        :type connected: bool, optional
        :return: None
        :rtype: None
        '''
        if connected:
            self.ui.label_3.setText('Connected')
        else:
            self.ui.label_3.setText('Disconnected')

        # want to return the error message as some kind of flash

    def download_selected_files(self):
        '''Signals to the fileBrowser widget to download all files / dirs the
        user has selected. Downloading occurs in the background and the FTP
        browser dialog is closed after a download has successfully begun.
        Additionally, another download should not be initiated while one is
        already in progress.
        '''
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

    def make_message_box(self, message, icon=QtWidgets.QMessageBox.Information,
                         buttons=QtWidgets.QMessageBox.Ok,
                         connected_function=None):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(icon)
        msg.setText(message)
        msg.setStandardButtons(buttons)
        if connected_function:
            msg.buttonClicked.connect(connected_function)
        return msg
