# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ethan/Documents/github/Marco_Polo/pyqt_designer/image_pop_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(763, 607)
        self.gridLayout_6 = QtWidgets.QGridLayout(Dialog)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.photoViewer = PhotoViewer(self.groupBox)
        self.photoViewer.setObjectName("photoViewer")
        self.gridLayout.addWidget(self.photoViewer, 0, 0, 1, 1)
        self.gridLayout_6.addWidget(self.groupBox, 0, 0, 4, 1)
        self.groupBox_4 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_4.setMaximumSize(QtCore.QSize(200, 200))
        self.groupBox_4.setObjectName("groupBox_4")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_4)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.textBrowser_2 = QtWidgets.QTextBrowser(self.groupBox_4)
        self.textBrowser_2.setObjectName("textBrowser_2")
        self.gridLayout_3.addWidget(self.textBrowser_2, 0, 0, 1, 1)
        self.gridLayout_6.addWidget(self.groupBox_4, 0, 1, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_2.setMaximumSize(QtCore.QSize(200, 200))
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.textBrowser = QtWidgets.QTextBrowser(self.groupBox_2)
        self.textBrowser.setObjectName("textBrowser")
        self.gridLayout_2.addWidget(self.textBrowser, 0, 0, 1, 1)
        self.gridLayout_6.addWidget(self.groupBox_2, 1, 1, 1, 1)
        self.groupBox_5 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_5.setObjectName("groupBox_5")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.groupBox_5)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.pushButton_6 = QtWidgets.QPushButton(self.groupBox_5)
        self.pushButton_6.setObjectName("pushButton_6")
        self.gridLayout_5.addWidget(self.pushButton_6, 0, 0, 1, 1)
        self.pushButton = QtWidgets.QPushButton(self.groupBox_5)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout_5.addWidget(self.pushButton, 0, 1, 1, 1)
        self.pushButton_7 = QtWidgets.QPushButton(self.groupBox_5)
        self.pushButton_7.setObjectName("pushButton_7")
        self.gridLayout_5.addWidget(self.pushButton_7, 1, 0, 1, 2)
        self.gridLayout_6.addWidget(self.groupBox_5, 2, 1, 1, 1)
        self.groupBox_3 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_3.setMaximumSize(QtCore.QSize(2000, 200))
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupBox_3)
        self.gridLayout_4.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.pushButton_2 = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton_2.setEnabled(True)
        self.pushButton_2.setMinimumSize(QtCore.QSize(60, 60))
        self.pushButton_2.setAutoDefault(False)
        self.pushButton_2.setDefault(False)
        self.pushButton_2.setFlat(False)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout_4.addWidget(self.pushButton_2, 0, 0, 1, 1)
        self.pushButton_5 = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton_5.setMinimumSize(QtCore.QSize(60, 60))
        self.pushButton_5.setObjectName("pushButton_5")
        self.gridLayout_4.addWidget(self.pushButton_5, 1, 0, 1, 1)
        self.pushButton_4 = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton_4.setMinimumSize(QtCore.QSize(60, 60))
        self.pushButton_4.setObjectName("pushButton_4")
        self.gridLayout_4.addWidget(self.pushButton_4, 1, 1, 1, 1)
        self.pushButton_3 = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton_3.setMinimumSize(QtCore.QSize(60, 60))
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridLayout_4.addWidget(self.pushButton_3, 0, 1, 1, 1)
        self.radioButton = QtWidgets.QRadioButton(self.groupBox_3)
        self.radioButton.setObjectName("radioButton")
        self.gridLayout_4.addWidget(self.radioButton, 2, 0, 1, 1)
        self.gridLayout_6.addWidget(self.groupBox_3, 3, 1, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Image Pop Out"))
        self.groupBox.setTitle(_translate("Dialog", "Image Name"))
        self.groupBox_4.setTitle(_translate("Dialog", "Image Details"))
        self.groupBox_2.setTitle(_translate("Dialog", "Cocktail Details"))
        self.groupBox_5.setTitle(_translate("Dialog", "Navigation"))
        self.pushButton_6.setText(_translate("Dialog", "Previous Date"))
        self.pushButton.setText(_translate("Dialog", "Next Date"))
        self.pushButton_7.setText(_translate("Dialog", "Swap Spectrum"))
        self.groupBox_3.setTitle(_translate("Dialog", "Human Classification"))
        self.pushButton_2.setToolTip(_translate("Dialog", "<html><head/><body><p>Classify current image as crystal.</p><p><br/></p></body></html>"))
        self.pushButton_2.setText(_translate("Dialog", "Crystal"))
        self.pushButton_2.setShortcut(_translate("Dialog", "A"))
        self.pushButton_5.setToolTip(_translate("Dialog", "<html><head/><body><p>Classify current image as clear.</p><p><br/></p></body></html>"))
        self.pushButton_5.setText(_translate("Dialog", "Clear"))
        self.pushButton_5.setShortcut(_translate("Dialog", "S"))
        self.pushButton_4.setToolTip(_translate("Dialog", "<html><head/><body><p>Classify current image as other.</p></body></html>"))
        self.pushButton_4.setText(_translate("Dialog", "Other"))
        self.pushButton_4.setShortcut(_translate("Dialog", "D"))
        self.pushButton_3.setToolTip(_translate("Dialog", "<html><head/><body><p>Classify current image as precipitate.</p></body></html>"))
        self.pushButton_3.setText(_translate("Dialog", "Precipitate"))
        self.pushButton_3.setShortcut(_translate("Dialog", "W"))
        self.radioButton.setText(_translate("Dialog", "Favorite?"))
from polo.widgets.slideshow_viewer import PhotoViewer
