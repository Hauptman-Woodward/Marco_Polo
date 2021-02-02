# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ethan/Documents/github/HWI/Marco_Polo/pyqt_designer/run_organizer.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(630, 575)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.runTree = RunTree(Form)
        self.runTree.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.runTree.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.runTree.setWordWrap(True)
        self.runTree.setObjectName("runTree")
        self.gridLayout.addWidget(self.runTree, 0, 0, 1, 2)
        self.label_30 = QtWidgets.QLabel(Form)
        self.label_30.setObjectName("label_30")
        self.gridLayout.addWidget(self.label_30, 4, 0, 1, 1)
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 1, 0, 1, 2)
        self.label_31 = QtWidgets.QLabel(Form)
        self.label_31.setObjectName("label_31")
        self.gridLayout.addWidget(self.label_31, 2, 0, 1, 2)
        self.progressBar = QtWidgets.QProgressBar(Form)
        self.progressBar.setToolTip("")
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout.addWidget(self.progressBar, 3, 0, 1, 2)
        self.label_32 = QtWidgets.QLabel(Form)
        self.label_32.setObjectName("label_32")
        self.gridLayout.addWidget(self.label_32, 4, 1, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.runTree.setToolTip(_translate("Form", "<html><head/><body><p><span style=\" background-color:transparent;\">Runs that have been loaded into Polo will be displayed here. Individual runs will appear under their respective sample. Runs of the same sample will be automatically associated, or &quot;linked&quot;, by date or spectrum to allow you to swap between spectrum or navigate between dates.</span></p><p><span style=\" background-color:transparent;\">To open a run </span><span style=\" font-weight:600; background-color:transparent;\">doubleclick </span><span style=\" background-color:transparent;\">it.</span></p><p><span style=\" background-color:transparent;\">To remove a run </span><span style=\" font-weight:600; background-color:transparent;\">left-click</span><span style=\" background-color:transparent;\"> and select </span><span style=\" font-weight:600; background-color:transparent;\">remove run</span><span style=\" background-color:transparent;\">.</span></p><p><span style=\" background-color:transparent;\">You can also add runs by draging and dropping image folders, rar archives or xtal files into the sample browser.</span></p><p><span style=\" background-color:transparent;\">To run the MARCO model on a run </span><span style=\" font-weight:600; background-color:transparent;\">click</span><span style=\" background-color:transparent;\"> the run and the hit the </span><span style=\" font-weight:600; background-color:transparent;\">Classify Selected Run</span><span style=\" background-color:transparent;\"> button below.</span></p></body></html>"))
        self.runTree.headerItem().setText(0, _translate("Form", "Samples"))
        self.label_30.setText(_translate("Form", "Est Time"))
        self.pushButton.setToolTip(_translate("Form", "<html><head/><body><p>Run the MARCO model on the currently selected run. </p><p>MARCO has been trained on visible (brightfield) images and its classifications are therefore not valid for images taken with other photographic technologies.</p><p><br/></p></body></html>"))
        self.pushButton.setText(_translate("Form", "Classify Selected Run"))
        self.label_31.setText(_translate("Form", "Classification Progress"))
        self.label_32.setText(_translate("Form", "0"))
from polo.widgets.run_tree import RunTree
