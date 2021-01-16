import ftplib
import os
from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QBrush, QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QApplication, QGridLayout

from polo import ICON_DICT, make_default_logger
from polo.designer.UI_FTP_Dialog import Ui_FTPDialog
from polo.threads.thread import FTPDownloadThread, QuickThread
from polo.utils.dialog_utils import make_message_box
from polo.utils.ftp_utils import logon


logger = make_default_logger(__name__)


class FTPDialog(QtWidgets.QDialog):
    '''FTPDialog class acts as the interface for interacting
    with a remote FTP server. Allows for browsing and downloading
    files stored on the server.

    :param ftp_connection: Existing FTP connection, defaults to None
    :type ftp_connection: FTP, optional
    :param parent: Parent widget, defaults to None
    :type parent: QWidget, optional
    '''

    DOWNLOAD_ICON = str(ICON_DICT['download'])
    CONNECTED_ICON = str(ICON_DICT['connected'])
    DISCONNECTED_ICON = str(ICON_DICT['disconnected'])

    def __init__(self, ftp_connection=None, parent=None):
        super(FTPDialog, self).__init__(parent)
        self.ui = Ui_FTPDialog()
        self.ui.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.ui.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.ui.pushButton_2.clicked.connect(self.download_selected_files)
        self.ui.pushButton.clicked.connect(self.connect_ftp)
        self.ui.pushButton_3.clicked.connect(self.close)
        self.ftp = ftp_connection
        self._connected = False 
        self.download_files = None
        self.save_dir = None
        self.home_dir = None

        self.ui.pushButton_2.setIcon(QIcon(self.DOWNLOAD_ICON))
        self.ui.pushButton_2.setEnabled(False)  # disable download until connected

        logger.debug('Created {}'.format(self))
        
    @property
    def host(self):
        '''Get user entered FTP host.

        :return: host address
        :rtype: str
        '''
        return self.ui.lineEdit_3.text()

    @property
    def password(self):
        '''Return user entered password.

        :return: password
        :rtype: str
        '''
        return self.ui.lineEdit_2.text()

    @property
    def username(self):
        '''Return username.

        :return: username
        :rtype: str
        '''
        return self.ui.lineEdit.text()
    
    @property
    def connected(self):
        return self._connected
    
    @connected.setter
    def connected(self, status):
        self._connected = status
        if status == True:
            self.ui.label_3.setText('Connected')
        else:
            self.ui.label_3.setText('Disconnected')
        
        self.ui.pushButton_2.setEnabled(status)

    def connect_ftp(self):
        '''Attempt to establish a connection to an ftp server. If the connection is
        successful then recursively walk through the user's home directory
        and display available directories and files via the
        `fileBrowser` widget. If the user has an extremely large number of
        files this can take a while. If the connection fails show the user
        the error code thrown by ftplib.
        '''
        if self.host and self.username:
            self.ui.fileBrowser.clear()
            QApplication.setOverrideCursor(Qt.WaitCursor)

            logon_thread = QuickThread(
                logon, host=self.host, username=self.username,
                password=self.password)
            message = make_message_box(
                'Attempting to connect to host', parent=self)

            def fin_connection_attempt():
                self.ftp = logon_thread.result
                if isinstance(self.ftp, ftplib.FTP):
                    try:  # connection attempt was good
                        self.home_dir = self.ftp.pwd()
                        self.ui.fileBrowser.grow_tree_using_mlsd(
                            self.ftp, self.home_dir)
                        # probably want to list files on new thread
                        # TODO
                        QApplication.restoreOverrideCursor()
                        message.close()
                        logger.debug('Connected to FTP server')
                        self.connected = True
                        make_message_box(
                            message='Connected to {}! They say {}'.format(
                                self.host,
                                self.ftp.getwelcome()),
                            parent=self
                        ).exec_()
                        message.close()
                        self.setEnabled(True)
                    except Exception as e:
                        message.close()
                        QApplication.restoreOverrideCursor()
                        self.setEnabled(True)
                        make_message_box(
                            message='After connecting to {}. This error occured {}'.format(
                                self.host, e),
                                parent=self
                            ).exec_()
                        self.connected = False
                else:  # did not connect in the first place
                    message.close()
                    self.setEnabled(True)
                    QApplication.restoreOverrideCursor()
                    m = make_message_box(message='Connection Failed: {}'.format(
                        self.ftp), buttons=QtWidgets.QMessageBox.Ok, parent=self)
                    logger.debug('FTP connection failed with code {}'.format(
                        self.ftp
                    ))
                    self.connected = False
                    m.exec_()
            

            logon_thread.finished.connect(fin_connection_attempt)
            logon_thread.start()
            self.setEnabled(False)
            message.exec_()

        else:
            self.setEnabled(True)
            QApplication.restoreOverrideCursor()
            make_message_box(
                message='Please enter a host and username to connect to', parent=self
            ).exec_()


    def set_connection_status(self, connected=False):
        '''Change the Qlabel that displays the current connection status
        to the user.

        :param connected: If FTP connection is successful, defaults to False
        :type connected: bool, optional
        '''
        if connected:
            self.ui.label_3.setText('Connected')
        else:
            self.ui.label_3.setText('Disconnected')


    def download_selected_files(self):
        '''Opens a file dialog for the user to select a location to download
        remote files to. All files / directories that are currently selected
        in the `FTPDialog` will then be appended to `download_files`
        attribute, marking them for download. A message box informing the user
        that files are downloading is shown and then the FTPDialog closes.

        At this point the method that originally created the `FTPDialog`
        instance should realize the dialog is closed and check for an open
        FTP connection and the presence of files in the `download_file`
        attribute (indicating the user had selecting files for downloading).

        An `FTPDownloadThread` instance can then be created to download files
        in the background without interrupting other Polo interfaces.
        '''
        file_dlg = QtWidgets.QFileDialog()
        file_dlg.setFileMode(QtWidgets.QFileDialog.Directory)
        file_dlg.exec_()
        filenames = file_dlg.selectedFiles()
        if filenames:
            self.save_dir = filenames[0]
            self.download_files = self.ui.fileBrowser.get_checked_files(
                self.home_dir)
            # This string is really long because adding \ makes it look weird
            # as a dialog.
            message = 'Your files are being downloaded to {} in the background. Polo will notify you when the download is completed. This window will now close.'.format(
                self.save_dir)
            start_box = make_message_box(
                message, buttons=QtWidgets.QMessageBox.Ok, parent=self)
            start_box.exec_()
            logger.debug('Attempting to download over FTP to {}'.format(
                self.save_dir))
            self.close()

