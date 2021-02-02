# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ethan/Documents/github/HWI/Marco_Polo/pyqt_designer/settings.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(528, 548)
        self.listWidget = QtWidgets.QListWidget(Dialog)
        self.listWidget.setGeometry(QtCore.QRect(20, 10, 141, 511))
        self.listWidget.setObjectName("listWidget")
        item = QtWidgets.QListWidgetItem()
        self.listWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listWidget.addItem(item)
        self.stackedWidget = QtWidgets.QStackedWidget(Dialog)
        self.stackedWidget.setGeometry(QtCore.QRect(180, 20, 291, 451))
        self.stackedWidget.setObjectName("stackedWidget")
        self.ftp_settings = QtWidgets.QWidget()
        self.ftp_settings.setObjectName("ftp_settings")
        self.stackedWidget.addWidget(self.ftp_settings)
        self.slideshow_settings = QtWidgets.QWidget()
        self.slideshow_settings.setObjectName("slideshow_settings")
        self.label = QtWidgets.QLabel(self.slideshow_settings)
        self.label.setGeometry(QtCore.QRect(10, 10, 67, 17))
        self.label.setObjectName("label")
        self.stackedWidget.addWidget(self.slideshow_settings)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        __sortingEnabled = self.listWidget.isSortingEnabled()
        self.listWidget.setSortingEnabled(False)
        item = self.listWidget.item(0)
        item.setText(_translate("Dialog", "FTP"))
        item = self.listWidget.item(1)
        item.setText(_translate("Dialog", "Slideshow"))
        item = self.listWidget.item(2)
        item.setText(_translate("Dialog", "Run Linking"))
        item = self.listWidget.item(3)
        item.setText(_translate("Dialog", "Preformance"))
        self.listWidget.setSortingEnabled(__sortingEnabled)
        self.label.setText(_translate("Dialog", "TextLabel"))
