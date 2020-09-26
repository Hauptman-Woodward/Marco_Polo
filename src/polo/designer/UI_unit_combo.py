# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ethan/Documents/github/HWI/Marco_Polo/pyqt_designer/unit_combo.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_unitCombo(object):
    def setupUi(self, unitCombo):
        unitCombo.setObjectName("unitCombo")
        unitCombo.resize(225, 48)
        self.gridLayout = QtWidgets.QGridLayout(unitCombo)
        self.gridLayout.setObjectName("gridLayout")
        self.doubleSpinBox = QtWidgets.QDoubleSpinBox(unitCombo)
        self.doubleSpinBox.setMinimumSize(QtCore.QSize(50, 30))
        self.doubleSpinBox.setFrame(True)
        self.doubleSpinBox.setObjectName("doubleSpinBox")
        self.gridLayout.addWidget(self.doubleSpinBox, 0, 0, 1, 1)
        self.comboBox = QtWidgets.QComboBox(unitCombo)
        self.comboBox.setMinimumSize(QtCore.QSize(40, 30))
        self.comboBox.setObjectName("comboBox")
        self.gridLayout.addWidget(self.comboBox, 0, 1, 1, 1)

        self.retranslateUi(unitCombo)
        QtCore.QMetaObject.connectSlotsByName(unitCombo)

    def retranslateUi(self, unitCombo):
        _translate = QtCore.QCoreApplication.translate
        unitCombo.setWindowTitle(_translate("unitCombo", "Form"))
