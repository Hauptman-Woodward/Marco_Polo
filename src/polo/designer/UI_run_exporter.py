# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ethan/Documents/github/Polo_Builder/pyqt_designer/run_exporter.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ExporDialog(object):
    def setupUi(self, ExporDialog):
        ExporDialog.setObjectName("ExporDialog")
        ExporDialog.resize(617, 339)
        ExporDialog.setMaximumSize(QtCore.QSize(1000, 500))
        self.gridLayout = QtWidgets.QGridLayout(ExporDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox = QtWidgets.QGroupBox(ExporDialog)
        self.groupBox.setMaximumSize(QtCore.QSize(300, 1000))
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.comboBox = QtWidgets.QComboBox(self.groupBox)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.verticalLayout.addWidget(self.comboBox)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)
        self.groupBox_3 = QtWidgets.QGroupBox(ExporDialog)
        self.groupBox_3.setMaximumSize(QtCore.QSize(300, 1000))
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.checkBox = QtWidgets.QCheckBox(self.groupBox_3)
        self.checkBox.setObjectName("checkBox")
        self.verticalLayout_3.addWidget(self.checkBox)
        self.checkBox_2 = QtWidgets.QCheckBox(self.groupBox_3)
        self.checkBox_2.setObjectName("checkBox_2")
        self.verticalLayout_3.addWidget(self.checkBox_2)
        self.gridLayout.addWidget(self.groupBox_3, 1, 0, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(ExporDialog)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.textBrowser = QtWidgets.QTextBrowser(self.groupBox_2)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout_2.addWidget(self.textBrowser)
        self.gridLayout.addWidget(self.groupBox_2, 0, 1, 3, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(ExporDialog)
        self.buttonBox.setMaximumSize(QtCore.QSize(150, 50))
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)

        self.retranslateUi(ExporDialog)
        QtCore.QMetaObject.connectSlotsByName(ExporDialog)

    def retranslateUi(self, ExporDialog):
        _translate = QtCore.QCoreApplication.translate
        ExporDialog.setWindowTitle(_translate("ExporDialog", "Run Exporter"))
        self.groupBox.setTitle(_translate("ExporDialog", "Select Export Format"))
        self.comboBox.setItemText(0, _translate("ExporDialog", "xtal Format"))
        self.comboBox.setItemText(1, _translate("ExporDialog", "HTML Report"))
        self.comboBox.setItemText(2, _translate("ExporDialog", "PDF Report"))
        self.comboBox.setItemText(3, _translate("ExporDialog", "CSV - All Data"))
        self.comboBox.setItemText(4, _translate("ExporDialog", "CSV - Human Classifications Only"))
        self.groupBox_3.setTitle(_translate("ExporDialog", "Export Settings"))
        self.checkBox.setText(_translate("ExporDialog", "Encode Images?"))
        self.checkBox_2.setText(_translate("ExporDialog", "Something Else?"))
        self.groupBox_2.setTitle(_translate("ExporDialog", "Format Information"))