# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ethan/Documents/github/Polo_Builder/pyqt_designer/table_inspector.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(743, 515)
        self.gridLayout_3 = QtWidgets.QGridLayout(Form)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.tableViewer = TableViewer(Form)
        self.tableViewer.setMinimumSize(QtCore.QSize(250, 300))
        self.tableViewer.setObjectName("tableViewer")
        self.gridLayout_3.addWidget(self.tableViewer, 0, 0, 2, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(Form)
        self.groupBox_2.setMaximumSize(QtCore.QSize(200, 700))
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(self.groupBox_2)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.listWidget = QtWidgets.QListWidget(self.groupBox)
        self.listWidget.setObjectName("listWidget")
        self.gridLayout.addWidget(self.listWidget, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_11 = QtWidgets.QGroupBox(self.groupBox_2)
        self.groupBox_11.setMaximumSize(QtCore.QSize(200, 16777215))
        self.groupBox_11.setObjectName("groupBox_11")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_11)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.groupBox_14 = QtWidgets.QGroupBox(self.groupBox_11)
        self.groupBox_14.setMaximumSize(QtCore.QSize(16777215, 150))
        self.groupBox_14.setObjectName("groupBox_14")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.groupBox_14)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.checkBox_7 = QtWidgets.QCheckBox(self.groupBox_14)
        self.checkBox_7.setChecked(False)
        self.checkBox_7.setObjectName("checkBox_7")
        self.verticalLayout_7.addWidget(self.checkBox_7)
        self.checkBox_8 = QtWidgets.QCheckBox(self.groupBox_14)
        self.checkBox_8.setObjectName("checkBox_8")
        self.verticalLayout_7.addWidget(self.checkBox_8)
        self.checkBox_9 = QtWidgets.QCheckBox(self.groupBox_14)
        self.checkBox_9.setObjectName("checkBox_9")
        self.verticalLayout_7.addWidget(self.checkBox_9)
        self.checkBox_10 = QtWidgets.QCheckBox(self.groupBox_14)
        self.checkBox_10.setObjectName("checkBox_10")
        self.verticalLayout_7.addWidget(self.checkBox_10)
        self.gridLayout_2.addWidget(self.groupBox_14, 0, 0, 1, 1)
        self.groupBox_15 = QtWidgets.QGroupBox(self.groupBox_11)
        self.groupBox_15.setMaximumSize(QtCore.QSize(16777215, 100))
        self.groupBox_15.setObjectName("groupBox_15")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.groupBox_15)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.checkBox_11 = QtWidgets.QCheckBox(self.groupBox_15)
        self.checkBox_11.setObjectName("checkBox_11")
        self.verticalLayout_8.addWidget(self.checkBox_11)
        self.checkBox_12 = QtWidgets.QCheckBox(self.groupBox_15)
        self.checkBox_12.setObjectName("checkBox_12")
        self.verticalLayout_8.addWidget(self.checkBox_12)
        self.gridLayout_2.addWidget(self.groupBox_15, 1, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_11)
        self.pushButton = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)
        self.gridLayout_3.addWidget(self.groupBox_2, 0, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 8, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem, 1, 1, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "TableInspector"))
        self.groupBox_2.setTitle(_translate("Form", "Table Settings"))
        self.groupBox.setTitle(_translate("Form", "Columns"))
        self.listWidget.setToolTip(_translate("Form", "Select what columns to include in the current tableview."))
        self.groupBox_11.setTitle(_translate("Form", "Table Filters"))
        self.groupBox_14.setTitle(_translate("Form", "Image Type"))
        self.checkBox_7.setText(_translate("Form", "Crystal"))
        self.checkBox_8.setText(_translate("Form", "Clear"))
        self.checkBox_9.setText(_translate("Form", "Precipitate"))
        self.checkBox_10.setText(_translate("Form", "Other"))
        self.groupBox_15.setTitle(_translate("Form", "Classifier"))
        self.checkBox_11.setText(_translate("Form", "MARCO"))
        self.checkBox_12.setText(_translate("Form", "Human"))
        self.pushButton.setText(_translate("Form", "Apply Settings"))
from polo.widgets.table_viewer import TableViewer
