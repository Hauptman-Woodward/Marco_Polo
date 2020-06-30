# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ethan/Documents/github/Marco_Polo/pyqt_designer/unit_converter.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_UnitConverter(object):
    def setupUi(self, UnitConverter):
        UnitConverter.setObjectName("UnitConverter")
        UnitConverter.resize(452, 381)
        self.lineEdit = QtWidgets.QLineEdit(UnitConverter)
        self.lineEdit.setGeometry(QtCore.QRect(20, 60, 113, 25))
        self.lineEdit.setObjectName("lineEdit")
        self.comboBox = QtWidgets.QComboBox(UnitConverter)
        self.comboBox.setGeometry(QtCore.QRect(150, 60, 86, 25))
        self.comboBox.setObjectName("comboBox")
        self.label = QtWidgets.QLabel(UnitConverter)
        self.label.setGeometry(QtCore.QRect(30, 30, 67, 17))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(UnitConverter)
        self.label_2.setGeometry(QtCore.QRect(150, 30, 81, 17))
        self.label_2.setObjectName("label_2")

        self.retranslateUi(UnitConverter)
        QtCore.QMetaObject.connectSlotsByName(UnitConverter)

    def retranslateUi(self, UnitConverter):
        _translate = QtCore.QCoreApplication.translate
        UnitConverter.setWindowTitle(_translate("UnitConverter", "Unit Converter"))
        self.label.setText(_translate("UnitConverter", "Input Unit"))
        self.label_2.setText(_translate("UnitConverter", "Input Value"))
