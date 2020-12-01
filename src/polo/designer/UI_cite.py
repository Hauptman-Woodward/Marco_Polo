# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ethan/Documents/github/HWI/Marco_Polo/pyqt_designer/cite.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_CitePolo(object):
    def setupUi(self, CitePolo):
        CitePolo.setObjectName("CitePolo")
        CitePolo.resize(605, 367)
        self.gridLayout = QtWidgets.QGridLayout(CitePolo)
        self.gridLayout.setObjectName("gridLayout")
        self.PoloCite = QtWidgets.QTextBrowser(CitePolo)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.PoloCite.setFont(font)
        self.PoloCite.setAcceptDrops(False)
        self.PoloCite.setObjectName("PoloCite")
        self.gridLayout.addWidget(self.PoloCite, 0, 0, 1, 2)
        self.pushButton = QtWidgets.QPushButton(CitePolo)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 1, 0, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(CitePolo)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 1, 1, 1, 1)

        self.retranslateUi(CitePolo)
        QtCore.QMetaObject.connectSlotsByName(CitePolo)

    def retranslateUi(self, CitePolo):
        _translate = QtCore.QCoreApplication.translate
        CitePolo.setWindowTitle(_translate("CitePolo", "Thank you for using Polo"))
        self.PoloCite.setHtml(_translate("CitePolo", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:600; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">If you found Polo helpful, please cite</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">().</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">and</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">()</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Use the buttons below to open each article in your browser.</p></body></html>"))
        self.pushButton.setText(_translate("CitePolo", "Take me to the Polo article"))
        self.pushButton_2.setText(_translate("CitePolo", "Take me to the MARCO article"))
