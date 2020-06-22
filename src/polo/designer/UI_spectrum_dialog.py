# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ethan/Documents/github/Polo/src/PyQt_Designer/spectrum_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(638, 371)
        self.gridLayout_2 = QtWidgets.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setDefault(True)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout_2.addWidget(self.pushButton, 1, 2, 1, 1)
        self.groupBox_5 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_5.setObjectName("groupBox_5")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_5)
        self.gridLayout.setObjectName("gridLayout")
        self.label_3 = QtWidgets.QLabel(self.groupBox_5)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 3, 1, 1)
        self.listWidget = QtWidgets.QListWidget(self.groupBox_5)
        self.listWidget.setMaximumSize(QtCore.QSize(150, 16777215))
        self.listWidget.setObjectName("listWidget")
        self.gridLayout.addWidget(self.listWidget, 2, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupBox_5)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 2, 1, 1)
        self.label = QtWidgets.QLabel(self.groupBox_5)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.listWidget_2 = QtWidgets.QListWidget(self.groupBox_5)
        self.listWidget_2.setMaximumSize(QtCore.QSize(150, 16777215))
        self.listWidget_2.setObjectName("listWidget_2")
        self.gridLayout.addWidget(self.listWidget_2, 2, 1, 1, 1)
        self.listWidget_4 = QtWidgets.QListWidget(self.groupBox_5)
        self.listWidget_4.setMaximumSize(QtCore.QSize(150, 16777215))
        self.listWidget_4.setObjectName("listWidget_4")
        self.gridLayout.addWidget(self.listWidget_4, 2, 3, 1, 1)
        self.listWidget_3 = QtWidgets.QListWidget(self.groupBox_5)
        self.listWidget_3.setMaximumSize(QtCore.QSize(150, 16777215))
        self.listWidget_3.setObjectName("listWidget_3")
        self.gridLayout.addWidget(self.listWidget_3, 2, 2, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.groupBox_5)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 1, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox_5, 0, 0, 1, 3)
        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout_2.addWidget(self.pushButton_2, 1, 0, 1, 1)
        self.pushButton_3 = QtWidgets.QPushButton(Dialog)
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridLayout_2.addWidget(self.pushButton_3, 1, 1, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.pushButton.setText(_translate("Dialog", "Submit Assignment "))
        self.groupBox_5.setTitle(_translate("Dialog", "Select runs from different spectrum types to link"))
        self.label_3.setText(_translate("Dialog", "Other"))
        self.label_2.setText(_translate("Dialog", "SHG"))
        self.label.setText(_translate("Dialog", "Visible"))
        self.label_4.setText(_translate("Dialog", "UV-TPEF"))
        self.pushButton_2.setText(_translate("Dialog", "Cancel"))
        self.pushButton_3.setToolTip(_translate("Dialog", "Suggest runs to pair based on their imaging date. Runs imaged on the same date with different imaging tech will be suggested."))
        self.pushButton_3.setText(_translate("Dialog", "Suggest Links"))
