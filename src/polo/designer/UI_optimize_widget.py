# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ethan/Documents/github/Polo_Builder/src/PyQt_Designer/optimizeWidget.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(513, 559)
        self.gridLayout_3 = QtWidgets.QGridLayout(Form)
        self.gridLayout_3.setObjectName("gridLayout_3")
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
        self.gridLayout_3.addWidget(self.groupBox, 2, 1, 1, 1)
        self.groupBox_17 = QtWidgets.QGroupBox(Form)
        self.groupBox_17.setMaximumSize(QtCore.QSize(250, 200))
        self.groupBox_17.setObjectName("groupBox_17")
        self.gridLayout_24 = QtWidgets.QGridLayout(self.groupBox_17)
        self.gridLayout_24.setObjectName("gridLayout_24")
        self.label_27 = QtWidgets.QLabel(self.groupBox_17)
        self.label_27.setObjectName("label_27")
        self.gridLayout_24.addWidget(self.label_27, 1, 3, 1, 1)
        self.label_26 = QtWidgets.QLabel(self.groupBox_17)
        self.label_26.setObjectName("label_26")
        self.gridLayout_24.addWidget(self.label_26, 1, 0, 1, 1)
        self.spinBox_3 = QtWidgets.QSpinBox(self.groupBox_17)
        self.spinBox_3.setMaximum(1536)
        self.spinBox_3.setObjectName("spinBox_3")
        self.gridLayout_24.addWidget(self.spinBox_3, 1, 4, 1, 1)
        self.label_25 = QtWidgets.QLabel(self.groupBox_17)
        self.label_25.setObjectName("label_25")
        self.gridLayout_24.addWidget(self.label_25, 0, 0, 1, 5)
        self.spinBox_2 = QtWidgets.QSpinBox(self.groupBox_17)
        self.spinBox_2.setMaximum(1536)
        self.spinBox_2.setObjectName("spinBox_2")
        self.gridLayout_24.addWidget(self.spinBox_2, 1, 1, 1, 2)
        self.spinBox_4 = QtWidgets.QSpinBox(self.groupBox_17)
        self.spinBox_4.setMaximum(1536)
        self.spinBox_4.setObjectName("spinBox_4")
        self.gridLayout_24.addWidget(self.spinBox_4, 3, 0, 1, 2)
        self.comboBox_11 = QtWidgets.QComboBox(self.groupBox_17)
        self.comboBox_11.setObjectName("comboBox_11")
        self.comboBox_11.addItem("")
        self.comboBox_11.addItem("")
        self.comboBox_11.addItem("")
        self.gridLayout_24.addWidget(self.comboBox_11, 3, 2, 1, 3)
        self.label_34 = QtWidgets.QLabel(self.groupBox_17)
        self.label_34.setObjectName("label_34")
        self.gridLayout_24.addWidget(self.label_34, 2, 0, 1, 3)
        self.gridLayout_3.addWidget(self.groupBox_17, 0, 1, 1, 1)
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
        self.gridLayout_27 = QtWidgets.QGridLayout(self.tab_11)
        self.gridLayout_27.setObjectName("gridLayout_27")
        self.label_29 = QtWidgets.QLabel(self.tab_11)
        self.label_29.setObjectName("label_29")
        self.gridLayout_27.addWidget(self.label_29, 0, 0, 1, 2)
        self.comboBox_6 = QtWidgets.QComboBox(self.tab_11)
        self.comboBox_6.setObjectName("comboBox_6")
        self.gridLayout_27.addWidget(self.comboBox_6, 1, 0, 1, 3)
        self.label_38 = QtWidgets.QLabel(self.tab_11)
        self.label_38.setObjectName("label_38")
        self.gridLayout_27.addWidget(self.label_38, 2, 0, 1, 2)
        self.doubleSpinBox_4 = QtWidgets.QDoubleSpinBox(self.tab_11)
        self.doubleSpinBox_4.setProperty("value", 1.0)
        self.doubleSpinBox_4.setObjectName("doubleSpinBox_4")
        self.gridLayout_27.addWidget(self.doubleSpinBox_4, 3, 0, 1, 2)
        self.label_39 = QtWidgets.QLabel(self.tab_11)
        self.label_39.setObjectName("label_39")
        self.gridLayout_27.addWidget(self.label_39, 3, 2, 1, 1)
        self.label_33 = QtWidgets.QLabel(self.tab_11)
        self.label_33.setObjectName("label_33")
        self.gridLayout_27.addWidget(self.label_33, 4, 0, 1, 3)
        self.doubleSpinBox = QtWidgets.QDoubleSpinBox(self.tab_11)
        self.doubleSpinBox.setProperty("value", 1.0)
        self.doubleSpinBox.setObjectName("doubleSpinBox")
        self.gridLayout_27.addWidget(self.doubleSpinBox, 5, 0, 1, 1)
        self.comboBox_8 = QtWidgets.QComboBox(self.tab_11)
        self.comboBox_8.setObjectName("comboBox_8")
        self.comboBox_8.addItem("")
        self.comboBox_8.addItem("")
        self.comboBox_8.addItem("")
        self.comboBox_8.addItem("")
        self.gridLayout_27.addWidget(self.comboBox_8, 5, 1, 1, 2)
        self.tabWidget_2.addTab(self.tab_11, "")
        self.tab_12 = QtWidgets.QWidget()
        self.tab_12.setObjectName("tab_12")
        self.gridLayout_23 = QtWidgets.QGridLayout(self.tab_12)
        self.gridLayout_23.setObjectName("gridLayout_23")
        self.label_40 = QtWidgets.QLabel(self.tab_12)
        self.label_40.setObjectName("label_40")
        self.gridLayout_23.addWidget(self.label_40, 0, 0, 1, 2)
        self.comboBox_13 = QtWidgets.QComboBox(self.tab_12)
        self.comboBox_13.setObjectName("comboBox_13")
        self.gridLayout_23.addWidget(self.comboBox_13, 1, 0, 1, 3)
        self.label_41 = QtWidgets.QLabel(self.tab_12)
        self.label_41.setObjectName("label_41")
        self.gridLayout_23.addWidget(self.label_41, 2, 0, 1, 2)
        self.doubleSpinBox_5 = QtWidgets.QDoubleSpinBox(self.tab_12)
        self.doubleSpinBox_5.setProperty("value", 1.0)
        self.doubleSpinBox_5.setObjectName("doubleSpinBox_5")
        self.gridLayout_23.addWidget(self.doubleSpinBox_5, 3, 0, 1, 2)
        self.label_42 = QtWidgets.QLabel(self.tab_12)
        self.label_42.setObjectName("label_42")
        self.gridLayout_23.addWidget(self.label_42, 3, 2, 1, 1)
        self.label_43 = QtWidgets.QLabel(self.tab_12)
        self.label_43.setObjectName("label_43")
        self.gridLayout_23.addWidget(self.label_43, 4, 0, 1, 3)
        self.doubleSpinBox_6 = QtWidgets.QDoubleSpinBox(self.tab_12)
        self.doubleSpinBox_6.setProperty("value", 1.0)
        self.doubleSpinBox_6.setObjectName("doubleSpinBox_6")
        self.gridLayout_23.addWidget(self.doubleSpinBox_6, 5, 0, 1, 1)
        self.comboBox_14 = QtWidgets.QComboBox(self.tab_12)
        self.comboBox_14.setObjectName("comboBox_14")
        self.comboBox_14.addItem("")
        self.comboBox_14.addItem("")
        self.comboBox_14.addItem("")
        self.comboBox_14.addItem("")
        self.gridLayout_23.addWidget(self.comboBox_14, 5, 1, 1, 2)
        self.tabWidget_2.addTab(self.tab_12, "")
        self.tab_13 = QtWidgets.QWidget()
        self.tab_13.setObjectName("tab_13")
        self.gridLayout_29 = QtWidgets.QGridLayout(self.tab_13)
        self.gridLayout_29.setObjectName("gridLayout_29")
        self.label_36 = QtWidgets.QLabel(self.tab_13)
        self.label_36.setObjectName("label_36")
        self.gridLayout_29.addWidget(self.label_36, 0, 0, 1, 3)
        self.listWidget_4 = QtWidgets.QListWidget(self.tab_13)
        self.listWidget_4.setObjectName("listWidget_4")
        self.gridLayout_29.addWidget(self.listWidget_4, 1, 0, 1, 3)
        self.label_37 = QtWidgets.QLabel(self.tab_13)
        self.label_37.setObjectName("label_37")
        self.gridLayout_29.addWidget(self.label_37, 2, 0, 1, 3)
        self.doubleSpinBox_7 = QtWidgets.QDoubleSpinBox(self.tab_13)
        self.doubleSpinBox_7.setProperty("value", 1.0)
        self.doubleSpinBox_7.setObjectName("doubleSpinBox_7")
        self.gridLayout_29.addWidget(self.doubleSpinBox_7, 3, 0, 1, 1)
        self.comboBox_15 = QtWidgets.QComboBox(self.tab_13)
        self.comboBox_15.setObjectName("comboBox_15")
        self.comboBox_15.addItem("")
        self.comboBox_15.addItem("")
        self.comboBox_15.addItem("")
        self.comboBox_15.addItem("")
        self.gridLayout_29.addWidget(self.comboBox_15, 3, 1, 1, 2)
        self.label_44 = QtWidgets.QLabel(self.tab_13)
        self.label_44.setObjectName("label_44")
        self.gridLayout_29.addWidget(self.label_44, 4, 0, 1, 2)
        self.doubleSpinBox_8 = QtWidgets.QDoubleSpinBox(self.tab_13)
        self.doubleSpinBox_8.setProperty("value", 1.0)
        self.doubleSpinBox_8.setObjectName("doubleSpinBox_8")
        self.gridLayout_29.addWidget(self.doubleSpinBox_8, 4, 2, 1, 1)
        self.tabWidget_2.addTab(self.tab_13, "")
        self.gridLayout_2.addWidget(self.tabWidget_2, 1, 0, 1, 2)
        self.gridLayout_3.addWidget(self.groupBox_27, 1, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem, 3, 1, 1, 1)
        self.tableWidget = QtWidgets.QTableWidget(Form)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.gridLayout_3.addWidget(self.tableWidget, 0, 0, 4, 1)

        self.retranslateUi(Form)
        self.tabWidget_2.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.groupBox.setTitle(_translate("Form", "Display"))
        self.pushButton_26.setText(_translate("Form", "Export"))
        self.pushButton_27.setText(_translate("Form", "Show Screen"))
        self.groupBox_17.setTitle(_translate("Form", "Plate Setup"))
        self.label_27.setText(_translate("Form", "Y"))
        self.label_26.setText(_translate("Form", "X"))
        self.label_25.setText(_translate("Form", "Plate Dimensions"))
        self.comboBox_11.setItemText(0, _translate("Form", "ul"))
        self.comboBox_11.setItemText(1, _translate("Form", "ml"))
        self.comboBox_11.setItemText(2, _translate("Form", "l"))
        self.label_34.setText(_translate("Form", "Well Volume"))
        self.groupBox_27.setTitle(_translate("Form", "Reagents Controls"))
        self.label_35.setText(_translate("Form", "Hit Well"))
        self.comboBox_12.setToolTip(_translate("Form", "Well numbers of images you have classified as crystal containing. MARCO classifications are not included."))
        self.tab_11.setToolTip(_translate("Form", "Set the reagent to be varried on the x-axis of the plate"))
        self.label_29.setText(_translate("Form", "Assign Reagent"))
        self.label_38.setText(_translate("Form", "Varry each well by"))
        self.label_39.setText(_translate("Form", "%"))
        self.label_33.setText(_translate("Form", "Stock Concentration"))
        self.comboBox_8.setItemText(0, _translate("Form", "M"))
        self.comboBox_8.setItemText(1, _translate("Form", "uM"))
        self.comboBox_8.setItemText(2, _translate("Form", "%v/v"))
        self.comboBox_8.setItemText(3, _translate("Form", "%w/v"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_11), _translate("Form", "X Reagent"))
        self.tab_12.setToolTip(_translate("Form", "Set the reagent to be varried in the y-axis of the plate"))
        self.label_40.setText(_translate("Form", "Assign Reagent"))
        self.label_41.setText(_translate("Form", "Varry each well by"))
        self.label_42.setText(_translate("Form", "%"))
        self.label_43.setText(_translate("Form", "Stock Concentration"))
        self.comboBox_14.setItemText(0, _translate("Form", "M"))
        self.comboBox_14.setItemText(1, _translate("Form", "uM"))
        self.comboBox_14.setItemText(2, _translate("Form", "%v/v"))
        self.comboBox_14.setItemText(3, _translate("Form", "%w/v"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_12), _translate("Form", "Y Reagent"))
        self.label_36.setText(_translate("Form", "Constant Reagents"))
        self.label_37.setText(_translate("Form", "Stock Concentration"))
        self.comboBox_15.setItemText(0, _translate("Form", "M"))
        self.comboBox_15.setItemText(1, _translate("Form", "uM"))
        self.comboBox_15.setItemText(2, _translate("Form", "%v/v"))
        self.comboBox_15.setItemText(3, _translate("Form", "%w/v"))
        self.label_44.setText(_translate("Form", "pH"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_13), _translate("Form", "Constants"))
