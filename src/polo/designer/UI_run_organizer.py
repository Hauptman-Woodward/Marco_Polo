# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ethan/Documents/github/Marco_Polo/pyqt_designer/run_organizer.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(318, 580)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.label_30 = QtWidgets.QLabel(Form)
        self.label_30.setObjectName("label_30")
        self.gridLayout.addWidget(self.label_30, 4, 0, 1, 1)
        self.label_31 = QtWidgets.QLabel(Form)
        self.label_31.setObjectName("label_31")
        self.gridLayout.addWidget(self.label_31, 2, 0, 1, 2)
        self.label_32 = QtWidgets.QLabel(Form)
        self.label_32.setObjectName("label_32")
        self.gridLayout.addWidget(self.label_32, 4, 1, 1, 1)
        self.runTree = RunTree(Form)
        self.runTree.setMinimumSize(QtCore.QSize(0, 0))
        self.runTree.setObjectName("runTree")
        self.gridLayout.addWidget(self.runTree, 0, 0, 1, 2)
        self.progressBar = QtWidgets.QProgressBar(Form)
        self.progressBar.setToolTip("")
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout.addWidget(self.progressBar, 3, 0, 1, 2)
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 1, 0, 1, 2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_30.setText(_translate("Form", "Est Time"))
        self.label_31.setText(_translate("Form", "Classification Progress"))
        self.label_32.setText(_translate("Form", "0"))
        self.runTree.headerItem().setText(0, _translate("Form", "Samples"))
        self.pushButton.setToolTip(_translate("Form", "Run the MARCO model on the currently selected run. MARCO has been trained on visible light images and will only run on runs photographed using standard visible light imaging.\n"
""))
        self.pushButton.setText(_translate("Form", "Classify Selected Run"))
from polo.widgets.run_tree import RunTree
