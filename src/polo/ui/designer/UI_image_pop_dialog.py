# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ethan/Documents/github/Polo_Builder/pyqt_designer/image_pop_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(596, 638)
        self.gridLayout_3 = QtWidgets.QGridLayout(Dialog)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.photoViewer = PhotoViewer(self.groupBox)
        self.photoViewer.setObjectName("photoViewer")
        self.gridLayout.addWidget(self.photoViewer, 0, 0, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox, 0, 0, 1, 2)
        self.groupBox_2 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_2.setMaximumSize(QtCore.QSize(200, 200))
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.textBrowser = QtWidgets.QTextBrowser(self.groupBox_2)
        self.textBrowser.setObjectName("textBrowser")
        self.gridLayout_2.addWidget(self.textBrowser, 0, 0, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox_2, 1, 0, 1, 1)
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
        self.pushButton_3 = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton_3.setMinimumSize(QtCore.QSize(60, 60))
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridLayout_4.addWidget(self.pushButton_3, 0, 1, 1, 1)
        self.pushButton_4 = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton_4.setMinimumSize(QtCore.QSize(60, 60))
        self.pushButton_4.setObjectName("pushButton_4")
        self.gridLayout_4.addWidget(self.pushButton_4, 1, 1, 1, 1)
        self.pushButton_5 = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton_5.setMinimumSize(QtCore.QSize(60, 60))
        self.pushButton_5.setObjectName("pushButton_5")
        self.gridLayout_4.addWidget(self.pushButton_5, 1, 0, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox_3, 1, 1, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Image Pop Out"))
        self.groupBox.setTitle(_translate("Dialog", "Image Name"))
        self.groupBox_2.setTitle(_translate("Dialog", "Cocktail Details"))
        self.groupBox_3.setTitle(_translate("Dialog", "Human Classification"))
        self.pushButton_2.setToolTip(_translate("Dialog", "<html><head/><body><p>Classify current image as crystal.</p><p><br/></p></body></html>"))
        self.pushButton_2.setText(_translate("Dialog", "Crystal"))
        self.pushButton_2.setShortcut(_translate("Dialog", "A"))
        self.pushButton_3.setToolTip(_translate("Dialog", "<html><head/><body><p>Classify current image as precipitate.</p></body></html>"))
        self.pushButton_3.setText(_translate("Dialog", "Precipitate"))
        self.pushButton_3.setShortcut(_translate("Dialog", "W"))
        self.pushButton_4.setToolTip(_translate("Dialog", "<html><head/><body><p>Classify current image as other.</p></body></html>"))
        self.pushButton_4.setText(_translate("Dialog", "Other"))
        self.pushButton_4.setShortcut(_translate("Dialog", "D"))
        self.pushButton_5.setToolTip(_translate("Dialog", "<html><head/><body><p>Classify current image as clear.</p><p><br/></p></body></html>"))
        self.pushButton_5.setText(_translate("Dialog", "Clear"))
        self.pushButton_5.setShortcut(_translate("Dialog", "S"))
from polo.ui.widgets.slideshow_viewer import PhotoViewer
