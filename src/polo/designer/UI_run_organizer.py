# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ethan/Documents/github/Marco_Polo/pyqt_designer/run_organizer.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_runOrganizer(object):
    def setupUi(self, runOrganizer):
        runOrganizer.setObjectName("runOrganizer")
        runOrganizer.resize(177, 580)
        self.gridLayout = QtWidgets.QGridLayout(runOrganizer)
        self.gridLayout.setObjectName("gridLayout")
        self.runTree = RunTree(runOrganizer)
        self.runTree.setObjectName("runTree")
        self.gridLayout.addWidget(self.runTree, 0, 0, 1, 2)
        self.label_31 = QtWidgets.QLabel(runOrganizer)
        self.label_31.setObjectName("label_31")
        self.gridLayout.addWidget(self.label_31, 1, 0, 1, 2)
        self.progressBar = QtWidgets.QProgressBar(runOrganizer)
        self.progressBar.setToolTip("")
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout.addWidget(self.progressBar, 2, 0, 1, 2)
        self.label_30 = QtWidgets.QLabel(runOrganizer)
        self.label_30.setObjectName("label_30")
        self.gridLayout.addWidget(self.label_30, 3, 0, 1, 1)
        self.label_32 = QtWidgets.QLabel(runOrganizer)
        self.label_32.setObjectName("label_32")
        self.gridLayout.addWidget(self.label_32, 3, 1, 1, 1)

        self.retranslateUi(runOrganizer)
        QtCore.QMetaObject.connectSlotsByName(runOrganizer)

    def retranslateUi(self, runOrganizer):
        _translate = QtCore.QCoreApplication.translate
        runOrganizer.setWindowTitle(_translate("runOrganizer", "Form"))
        self.runTree.headerItem().setText(0, _translate("runOrganizer", "Samples"))
        self.label_31.setText(_translate("runOrganizer", "Classification Progress"))
        self.label_30.setText(_translate("runOrganizer", "Est Time"))
        self.label_32.setText(_translate("runOrganizer", "0"))
from polo.widgets.run_tree import RunTree
