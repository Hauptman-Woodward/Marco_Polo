# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ethan/Documents/github/HWI/Marco_Polo/pyqt_designer/run_exporter.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_PptxExporterDialog(object):
    def setupUi(self, PptxExporterDialog):
        PptxExporterDialog.setObjectName("PptxExporterDialog")
        PptxExporterDialog.resize(617, 339)
        PptxExporterDialog.setMaximumSize(QtCore.QSize(1000, 500))
        self.gridLayout = QtWidgets.QGridLayout(PptxExporterDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox = QtWidgets.QGroupBox(PptxExporterDialog)
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
        self.groupBox_3 = QtWidgets.QGroupBox(PptxExporterDialog)
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
        self.groupBox_2 = QtWidgets.QGroupBox(PptxExporterDialog)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.textBrowser = QtWidgets.QTextBrowser(self.groupBox_2)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout_2.addWidget(self.textBrowser)
        self.gridLayout.addWidget(self.groupBox_2, 0, 1, 3, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(PptxExporterDialog)
        self.buttonBox.setMaximumSize(QtCore.QSize(150, 50))
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)

        self.retranslateUi(PptxExporterDialog)
        QtCore.QMetaObject.connectSlotsByName(PptxExporterDialog)

    def retranslateUi(self, PptxExporterDialog):
        _translate = QtCore.QCoreApplication.translate
        PptxExporterDialog.setWindowTitle(_translate("PptxExporterDialog", "Run Exporter"))
        self.groupBox.setTitle(_translate("PptxExporterDialog", "Select Export Format"))
        self.comboBox.setItemText(0, _translate("PptxExporterDialog", "xtal Format"))
        self.comboBox.setItemText(1, _translate("PptxExporterDialog", "HTML Report"))
        self.comboBox.setItemText(2, _translate("PptxExporterDialog", "PDF Report"))
        self.comboBox.setItemText(3, _translate("PptxExporterDialog", "CSV - All Data"))
        self.comboBox.setItemText(4, _translate("PptxExporterDialog", "CSV - Human Classifications Only"))
        self.groupBox_3.setTitle(_translate("PptxExporterDialog", "Export Settings"))
        self.checkBox.setText(_translate("PptxExporterDialog", "Encode Images?"))
        self.checkBox_2.setText(_translate("PptxExporterDialog", "Something Else?"))
        self.groupBox_2.setTitle(_translate("PptxExporterDialog", "Format Information"))
