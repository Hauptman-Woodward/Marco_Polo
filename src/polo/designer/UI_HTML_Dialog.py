# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ethan/Documents/github/Polo_Builder/pyqt_designer/HTML_Dialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_HTMLReportDialog(object):
    def setupUi(self, HTMLReportDialog):
        HTMLReportDialog.setObjectName("HTMLReportDialog")
        HTMLReportDialog.resize(377, 245)
        self.gridLayout = QtWidgets.QGridLayout(HTMLReportDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton = QtWidgets.QPushButton(HTMLReportDialog)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 1, 0, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(HTMLReportDialog)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 1, 1, 1, 1)
        self.groupBox = QtWidgets.QGroupBox(HTMLReportDialog)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.checkBox_6 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_6.setChecked(True)
        self.checkBox_6.setObjectName("checkBox_6")
        self.verticalLayout.addWidget(self.checkBox_6)
        self.checkBox_7 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_7.setChecked(True)
        self.checkBox_7.setObjectName("checkBox_7")
        self.verticalLayout.addWidget(self.checkBox_7)
        self.checkBox_5 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_5.setObjectName("checkBox_5")
        self.verticalLayout.addWidget(self.checkBox_5)
        self.checkBox_4 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_4.setObjectName("checkBox_4")
        self.verticalLayout.addWidget(self.checkBox_4)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(HTMLReportDialog)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.radioButton = QtWidgets.QRadioButton(self.groupBox_2)
        self.radioButton.setTabletTracking(False)
        self.radioButton.setChecked(True)
        self.radioButton.setObjectName("radioButton")
        self.verticalLayout_2.addWidget(self.radioButton)
        self.radioButton_2 = QtWidgets.QRadioButton(self.groupBox_2)
        self.radioButton_2.setObjectName("radioButton_2")
        self.verticalLayout_2.addWidget(self.radioButton_2)
        self.radioButton_3 = QtWidgets.QRadioButton(self.groupBox_2)
        self.radioButton_3.setObjectName("radioButton_3")
        self.verticalLayout_2.addWidget(self.radioButton_3)
        self.radioButton_4 = QtWidgets.QRadioButton(self.groupBox_2)
        self.radioButton_4.setObjectName("radioButton_4")
        self.verticalLayout_2.addWidget(self.radioButton_4)
        self.gridLayout.addWidget(self.groupBox_2, 0, 1, 1, 1)

        self.retranslateUi(HTMLReportDialog)
        QtCore.QMetaObject.connectSlotsByName(HTMLReportDialog)

    def retranslateUi(self, HTMLReportDialog):
        _translate = QtCore.QCoreApplication.translate
        HTMLReportDialog.setWindowTitle(_translate("HTMLReportDialog", "HTML Report Settings"))
        self.pushButton.setText(_translate("HTMLReportDialog", "Cancel"))
        self.pushButton_2.setText(_translate("HTMLReportDialog", "Generate Report"))
        self.groupBox.setTitle(_translate("HTMLReportDialog", "Include in Report"))
        self.checkBox_6.setText(_translate("HTMLReportDialog", "Plate Annotations"))
        self.checkBox_7.setText(_translate("HTMLReportDialog", "Image Annotations"))
        self.checkBox_5.setText(_translate("HTMLReportDialog", "Plate Summary Stats"))
        self.checkBox_4.setText(_translate("HTMLReportDialog", "Plate Heatmaps"))
        self.groupBox_2.setTitle(_translate("HTMLReportDialog", "Sort Entries By"))
        self.radioButton.setText(_translate("HTMLReportDialog", "Human Classification"))
        self.radioButton_2.setText(_translate("HTMLReportDialog", "MARCO Classification"))
        self.radioButton_3.setText(_translate("HTMLReportDialog", "Well Number"))
        self.radioButton_4.setText(_translate("HTMLReportDialog", "Cocktail Number"))
