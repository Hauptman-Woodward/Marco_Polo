# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ethan/Documents/github/Marco_Polo/pyqt_designer/optimizeWidget.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(685, 615)
        self.gridLayout_4 = QtWidgets.QGridLayout(Form)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.tableWidget = QtWidgets.QTableWidget(Form)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.gridLayout_4.addWidget(self.tableWidget, 0, 0, 4, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_4.addItem(spacerItem, 3, 1, 1, 1)
        self.groupBox_17 = QtWidgets.QGroupBox(Form)
        self.groupBox_17.setMaximumSize(QtCore.QSize(250, 200))
        self.groupBox_17.setObjectName("groupBox_17")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_17)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_25 = QtWidgets.QLabel(self.groupBox_17)
        self.label_25.setObjectName("label_25")
        self.gridLayout_3.addWidget(self.label_25, 0, 0, 1, 4)
        self.label_26 = QtWidgets.QLabel(self.groupBox_17)
        self.label_26.setObjectName("label_26")
        self.gridLayout_3.addWidget(self.label_26, 1, 0, 1, 1)
        self.spinBox_2 = QtWidgets.QSpinBox(self.groupBox_17)
        self.spinBox_2.setMaximum(1536)
        self.spinBox_2.setObjectName("spinBox_2")
        self.gridLayout_3.addWidget(self.spinBox_2, 1, 1, 1, 1)
        self.label_27 = QtWidgets.QLabel(self.groupBox_17)
        self.label_27.setObjectName("label_27")
        self.gridLayout_3.addWidget(self.label_27, 1, 2, 1, 1)
        self.label_34 = QtWidgets.QLabel(self.groupBox_17)
        self.label_34.setObjectName("label_34")
        self.gridLayout_3.addWidget(self.label_34, 2, 0, 1, 2)
        self.unitComboBox_2 = UnitComboBox(self.groupBox_17)
        self.unitComboBox_2.setMinimumSize(QtCore.QSize(40, 50))
        self.unitComboBox_2.setObjectName("unitComboBox_2")
        self.gridLayout_3.addWidget(self.unitComboBox_2, 2, 3, 1, 2)
        self.label = QtWidgets.QLabel(self.groupBox_17)
        self.label.setObjectName("label")
        self.gridLayout_3.addWidget(self.label, 3, 0, 1, 2)
        self.spinBox_3 = QtWidgets.QSpinBox(self.groupBox_17)
        self.spinBox_3.setMaximum(1536)
        self.spinBox_3.setObjectName("spinBox_3")
        self.gridLayout_3.addWidget(self.spinBox_3, 1, 3, 1, 2)
        self.comboBox_16 = QtWidgets.QComboBox(self.groupBox_17)
        self.comboBox_16.setObjectName("comboBox_16")
        self.comboBox_16.addItem("")
        self.comboBox_16.addItem("")
        self.comboBox_16.addItem("")
        self.gridLayout_3.addWidget(self.comboBox_16, 3, 3, 1, 2)
        self.gridLayout_4.addWidget(self.groupBox_17, 0, 1, 1, 1)
        self.groupBox_27 = QtWidgets.QGroupBox(Form)
        self.groupBox_27.setMaximumSize(QtCore.QSize(250, 350))
        self.groupBox_27.setObjectName("groupBox_27")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_27)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_35 = QtWidgets.QLabel(self.groupBox_27)
        self.label_35.setObjectName("label_35")
        self.gridLayout_2.addWidget(self.label_35, 0, 0, 1, 1)
        self.comboBox_12 = QtWidgets.QComboBox(self.groupBox_27)
        self.comboBox_12.setObjectName("comboBox_12")
        self.gridLayout_2.addWidget(self.comboBox_12, 0, 1, 1, 1)
        self.tabWidget_2 = QtWidgets.QTabWidget(self.groupBox_27)
        self.tabWidget_2.setObjectName("tabWidget_2")
        self.tab_11 = QtWidgets.QWidget()
        self.tab_11.setObjectName("tab_11")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.tab_11)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.label_29 = QtWidgets.QLabel(self.tab_11)
        self.label_29.setObjectName("label_29")
        self.gridLayout_5.addWidget(self.label_29, 0, 0, 1, 1)
        self.label_38 = QtWidgets.QLabel(self.tab_11)
        self.label_38.setObjectName("label_38")
        self.gridLayout_5.addWidget(self.label_38, 2, 0, 1, 1)
        self.doubleSpinBox_4 = QtWidgets.QDoubleSpinBox(self.tab_11)
        self.doubleSpinBox_4.setProperty("value", 1.0)
        self.doubleSpinBox_4.setObjectName("doubleSpinBox_4")
        self.gridLayout_5.addWidget(self.doubleSpinBox_4, 3, 0, 1, 1)
        self.label_39 = QtWidgets.QLabel(self.tab_11)
        self.label_39.setObjectName("label_39")
        self.gridLayout_5.addWidget(self.label_39, 3, 1, 1, 1)
        self.label_33 = QtWidgets.QLabel(self.tab_11)
        self.label_33.setObjectName("label_33")
        self.gridLayout_5.addWidget(self.label_33, 4, 0, 1, 1)
        self.unitComboBox = UnitComboBox(self.tab_11)
        self.unitComboBox.setObjectName("unitComboBox")
        self.gridLayout_5.addWidget(self.unitComboBox, 5, 0, 1, 2)
        self.comboBox_6 = QtWidgets.QComboBox(self.tab_11)
        self.comboBox_6.setObjectName("comboBox_6")
        self.gridLayout_5.addWidget(self.comboBox_6, 1, 0, 1, 2)
        self.tabWidget_2.addTab(self.tab_11, "")
        self.tab_12 = QtWidgets.QWidget()
        self.tab_12.setObjectName("tab_12")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.tab_12)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.label_40 = QtWidgets.QLabel(self.tab_12)
        self.label_40.setObjectName("label_40")
        self.gridLayout_6.addWidget(self.label_40, 0, 0, 1, 1)
        self.label_41 = QtWidgets.QLabel(self.tab_12)
        self.label_41.setObjectName("label_41")
        self.gridLayout_6.addWidget(self.label_41, 2, 0, 1, 1)
        self.doubleSpinBox_5 = QtWidgets.QDoubleSpinBox(self.tab_12)
        self.doubleSpinBox_5.setProperty("value", 1.0)
        self.doubleSpinBox_5.setObjectName("doubleSpinBox_5")
        self.gridLayout_6.addWidget(self.doubleSpinBox_5, 3, 0, 1, 1)
        self.label_42 = QtWidgets.QLabel(self.tab_12)
        self.label_42.setObjectName("label_42")
        self.gridLayout_6.addWidget(self.label_42, 3, 1, 1, 1)
        self.label_43 = QtWidgets.QLabel(self.tab_12)
        self.label_43.setObjectName("label_43")
        self.gridLayout_6.addWidget(self.label_43, 4, 0, 1, 1)
        self.unitComboBox_3 = UnitComboBox(self.tab_12)
        self.unitComboBox_3.setObjectName("unitComboBox_3")
        self.gridLayout_6.addWidget(self.unitComboBox_3, 5, 0, 1, 2)
        self.comboBox_13 = QtWidgets.QComboBox(self.tab_12)
        self.comboBox_13.setObjectName("comboBox_13")
        self.gridLayout_6.addWidget(self.comboBox_13, 1, 0, 1, 2)
        self.tabWidget_2.addTab(self.tab_12, "")
        self.tab_13 = QtWidgets.QWidget()
        self.tab_13.setObjectName("tab_13")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.tab_13)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.label_36 = QtWidgets.QLabel(self.tab_13)
        self.label_36.setObjectName("label_36")
        self.gridLayout_7.addWidget(self.label_36, 0, 0, 1, 2)
        self.listWidget_4 = QtWidgets.QListWidget(self.tab_13)
        self.listWidget_4.setObjectName("listWidget_4")
        self.gridLayout_7.addWidget(self.listWidget_4, 1, 0, 1, 2)
        self.label_37 = QtWidgets.QLabel(self.tab_13)
        self.label_37.setObjectName("label_37")
        self.gridLayout_7.addWidget(self.label_37, 2, 0, 1, 2)
        self.unitComboBox_4 = UnitComboBox(self.tab_13)
        self.unitComboBox_4.setMinimumSize(QtCore.QSize(0, 50))
        self.unitComboBox_4.setObjectName("unitComboBox_4")
        self.gridLayout_7.addWidget(self.unitComboBox_4, 3, 0, 1, 2)
        self.label_44 = QtWidgets.QLabel(self.tab_13)
        self.label_44.setObjectName("label_44")
        self.gridLayout_7.addWidget(self.label_44, 4, 0, 1, 1)
        self.doubleSpinBox_8 = QtWidgets.QDoubleSpinBox(self.tab_13)
        self.doubleSpinBox_8.setProperty("value", 1.0)
        self.doubleSpinBox_8.setObjectName("doubleSpinBox_8")
        self.gridLayout_7.addWidget(self.doubleSpinBox_8, 4, 1, 1, 1)
        self.tabWidget_2.addTab(self.tab_13, "")
        self.gridLayout_2.addWidget(self.tabWidget_2, 1, 0, 1, 2)
        self.gridLayout_4.addWidget(self.groupBox_27, 1, 1, 1, 1)
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setMaximumSize(QtCore.QSize(16777215, 70))
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_26 = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_26.setObjectName("pushButton_26")
        self.gridLayout.addWidget(self.pushButton_26, 0, 0, 1, 1)
        self.pushButton_27 = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_27.setObjectName("pushButton_27")
        self.gridLayout.addWidget(self.pushButton_27, 0, 1, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox, 2, 1, 1, 1)

        self.retranslateUi(Form)
        self.tabWidget_2.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.tableWidget.setToolTip(_translate("Form", "<html><head/><body><p>The current optimization screen will be displayed here.</p></body></html>"))
        self.groupBox_17.setTitle(_translate("Form", "Plate Setup"))
        self.label_25.setText(_translate("Form", "Plate Dimensions"))
        self.label_26.setText(_translate("Form", "X"))
        self.spinBox_2.setToolTip(_translate("Form", "Change the x (number of rows) dimension of your screening plate."))
        self.label_27.setText(_translate("Form", "Y"))
        self.label_34.setToolTip(_translate("Form", "<html><head/><body><p>Set the volume of an individual well in your optimization plate.</p></body></html>"))
        self.label_34.setText(_translate("Form", "Well Volume"))
        self.label.setToolTip(_translate("Form", "<html><head/><body><p>Set the units to display reagent volumes in.</p></body></html>"))
        self.label.setText(_translate("Form", "Output Units"))
        self.spinBox_3.setToolTip(_translate("Form", "Change the y (number of columns) dimension of your screening plate."))
        self.comboBox_16.setToolTip(_translate("Form", "Set the stock solution unit in the final output."))
        self.comboBox_16.setItemText(0, _translate("Form", "ul"))
        self.comboBox_16.setItemText(1, _translate("Form", "ml"))
        self.comboBox_16.setItemText(2, _translate("Form", "l"))
        self.groupBox_27.setTitle(_translate("Form", "Reagents Controls"))
        self.label_35.setText(_translate("Form", "Hit Well"))
        self.comboBox_12.setToolTip(_translate("Form", "<html><head/><body><p>Well numbers of images you have classified as crystal containing. MARCO classifications are not included. Pick from these wells to optimize.</p></body></html>"))
        self.tab_11.setToolTip(_translate("Form", "Set the reagent to be varried on the x-axis of the plate"))
        self.label_29.setText(_translate("Form", "Assign Reagent"))
        self.label_38.setText(_translate("Form", "Varry each well by"))
        self.doubleSpinBox_4.setToolTip(_translate("Form", "Percent difference of each well along the x axis in reference to the x reagent hit concentration."))
        self.label_39.setText(_translate("Form", "%"))
        self.label_33.setText(_translate("Form", "Stock Concentration"))
        self.unitComboBox.setToolTip(_translate("Form", "<html><head/><body><p>Set the stock concentration of your selected x reagent</p></body></html>"))
        self.comboBox_6.setToolTip(_translate("Form", "Select the reagent to vary across the x axis of the plate."))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_11), _translate("Form", "X Reagent"))
        self.tab_12.setToolTip(_translate("Form", "Set the reagent to be varried in the y-axis of the plate"))
        self.label_40.setText(_translate("Form", "Assign Reagent"))
        self.label_41.setText(_translate("Form", "Vary each well by"))
        self.doubleSpinBox_5.setToolTip(_translate("Form", "Percent difference of each well along the y axis in reference to the y reagent hit concentration."))
        self.label_42.setText(_translate("Form", "%"))
        self.label_43.setText(_translate("Form", "Stock Concentration"))
        self.unitComboBox_3.setToolTip(_translate("Form", "<html><head/><body><p>Set the stock concentration of your selected y reagent.</p></body></html>"))
        self.comboBox_13.setToolTip(_translate("Form", "Select the reagent to vary on the y axis of the plate."))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_12), _translate("Form", "Y Reagent"))
        self.label_36.setText(_translate("Form", "Constant Reagents"))
        self.listWidget_4.setToolTip(_translate("Form", "<html><head/><body><p>Reagents that have not been selected as the x nor y reagent appear hear.</p></body></html>"))
        self.label_37.setText(_translate("Form", "Stock Concentration"))
        self.label_44.setText(_translate("Form", "pH"))
        self.doubleSpinBox_8.setToolTip(_translate("Form", "Set the pH of your screen across the optimization plate."))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_13), _translate("Form", "Constants"))
        self.groupBox.setTitle(_translate("Form", "Display"))
        self.pushButton_26.setToolTip(_translate("Form", "Export the current optimization screen to an html file. Will open a file browser and ask you to specify a location and filename for your export."))
        self.pushButton_26.setText(_translate("Form", "Export"))
        self.pushButton_27.setToolTip(_translate("Form", "Render the optimization plate to the screen."))
        self.pushButton_27.setText(_translate("Form", "Show Screen"))
from polo.widgets.unit_combo import UnitComboBox
