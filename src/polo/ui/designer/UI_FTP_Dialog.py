# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ethan/Documents/github/Polo_Builder/pyqt_designer/FTP_Dialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_FTPDialog(object):
    def setupUi(self, FTPDialog):
        FTPDialog.setObjectName("FTPDialog")
        FTPDialog.resize(641, 487)
        self.gridLayout = QtWidgets.QGridLayout(FTPDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox_4 = QtWidgets.QGroupBox(FTPDialog)
        self.groupBox_4.setMaximumSize(QtCore.QSize(250, 70))
        self.groupBox_4.setObjectName("groupBox_4")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.groupBox_4)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.lineEdit_3 = QtWidgets.QLineEdit(self.groupBox_4)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.verticalLayout_4.addWidget(self.lineEdit_3)
        self.gridLayout.addWidget(self.groupBox_4, 0, 0, 1, 1)
        self.groupBox = QtWidgets.QGroupBox(FTPDialog)
        self.groupBox.setMaximumSize(QtCore.QSize(250, 250))
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.pushButton_3 = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridLayout_2.addWidget(self.pushButton_3, 5, 0, 1, 1)
        self.pushButton = QtWidgets.QPushButton(self.groupBox)
        self.pushButton.setDefault(True)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout_2.addWidget(self.pushButton, 5, 1, 1, 1)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.gridLayout_2.addWidget(self.lineEdit_2, 3, 0, 1, 2)
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.lineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout_2.addWidget(self.lineEdit, 1, 0, 1, 2)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 2, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout_2.addItem(spacerItem, 4, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 1, 0, 1, 1)
        self.groupBox_3 = QtWidgets.QGroupBox(FTPDialog)
        self.groupBox_3.setMaximumSize(QtCore.QSize(250, 100))
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_3 = QtWidgets.QLabel(self.groupBox_3)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_3.addWidget(self.label_3)
        self.gridLayout.addWidget(self.groupBox_3, 2, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 3, 0, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(FTPDialog)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.fileBrowser = fileBrowser(self.groupBox_2)
        self.fileBrowser.setObjectName("fileBrowser")
        self.verticalLayout_2.addWidget(self.fileBrowser)
        self.pushButton_2 = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_2.setObjectName("pushButton_2")
        self.verticalLayout_2.addWidget(self.pushButton_2)
        self.gridLayout.addWidget(self.groupBox_2, 0, 1, 4, 1)

        self.retranslateUi(FTPDialog)
        QtCore.QMetaObject.connectSlotsByName(FTPDialog)

    def retranslateUi(self, FTPDialog):
        _translate = QtCore.QCoreApplication.translate
        FTPDialog.setWindowTitle(_translate("FTPDialog", "FTP Browser"))
        self.groupBox_4.setTitle(_translate("FTPDialog", "Enter Host"))
        self.lineEdit_3.setText(_translate("FTPDialog", "ftp.hwi.buffalo.edu"))
        self.groupBox.setTitle(_translate("FTPDialog", "FTP Logon"))
        self.pushButton_3.setText(_translate("FTPDialog", "Cancel"))
        self.pushButton.setText(_translate("FTPDialog", "Connect"))
        self.label.setText(_translate("FTPDialog", "Username"))
        self.label_2.setText(_translate("FTPDialog", "Password"))
        self.groupBox_3.setTitle(_translate("FTPDialog", "Connection Status"))
        self.label_3.setText(_translate("FTPDialog", "Disconnected "))
        self.groupBox_2.setTitle(_translate("FTPDialog", "File Browser"))
        self.pushButton_2.setText(_translate("FTPDialog", "Download Selected Files"))
from polo.ui.widgets.file_browser import fileBrowser
