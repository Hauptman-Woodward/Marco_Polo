import base64
import os

import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QBrush, QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QGridLayout

from polo.designer.UI_secure_save_dialog import Ui_Dialog
from polo.utils.ftp_utils import list_dir, logon

# file name should have .xtals for xtal secure

class SecureSaveDialog(QtWidgets.QDialog):

    def __init__(self, file_path, decrypt=True):  # set mode to descript by default
        QtWidgets.QDialog.__init__(self)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.file_path = file_path
        if decrypt:
            self.ui.pushButton_2.clicked.connect(self.decryption_routine)
        else:
            self.ui.pushButton_2.clicked.connect(self.encryption_routine)
        self.ui.pushButton.clicked.connect(self.close)

        self.exec_()
    
    def compare_passwords(self):
        entry_a, entry_b = self.ui.lineEdit.text(), self.ui.lineEdit_2.text()
        if entry_a == entry_b:
            return entry_a
        else:
            return False
    
    def make_key_from_password(self, password):
        password = password.encode()
        kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=password,
        iterations=100000,
        backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(password))
    
    def encryption_routine(self):
        password = self.compare_passwords()
        if password:
            self.encrypt_file(password)
        else:
            print('error')
            # show error message

    def decryption_routine(self):
        password = self.compare_passwords()
        if password:
            self.decrypt_file(password)
        else:
            print('error')

    def encrypt_file(self, password):
        with open(self.file_path, 'rb') as f:
            contents = f.read()
        
        key = self.make_key_from_password(password)
        fernet = Fernet(key)
        encrypted_contents = fernet.encrypt(contents)

        with open(self.file_path, 'wb') as f:
            f.write(encrypted_contents)
        self.close()

    def decrypt_file(self, password):
        with open(self.file_path, 'rb') as f:
            encrypted_contents = f.read()
        try:
            key = self.make_key_from_password(password)
            fernet = Fernet(key)
            decrypted_contents = fernet.decrypt(encrypted_contents)
        except cryptography.fernet.InvalidToken:
            print('Wrong password my guy')

        with open(self.file_path, 'wb') as f:
            f.write(decrypted_contents)
