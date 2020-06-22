import json
import os

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QBrush, QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QGridLayout
from polo.designer.UI_run_updater_dialog import Ui_runUpdater

from polo import LOG_PATH, tim


class RunUpdaterDialog(QtWidgets.QDialog):
    '''Small dialog for displaying the contents of the Polo log file
    '''

    def __init__(self, run, run_names, parent=None):
        super(RunUpdaterDialog, self).__init__(parent)
        self.ui = Ui_runUpdater()
        self.ui.setupUi(self)
        self.run = run
        self.run_names = run_names  # all currently used run names
        self.ui.pushButton_2.clicked.connect(self.close)
        self.set_cocktail_menu()
        self.select_run_menu()

        self.exec_()

    @property
    def current_menus(self):
        return self.__current_menus

    @current_menus.setter
    def current_menus(self, type_key):
        if type_key == 's' or type_key == 'm':  # soluble or membrane
            self.__current_menus = tim.get_menus_by_type(type_key)
        else:
            return []

    @property
    def run(self):
        return self.__run

    @run.setter
    def run(self, new_run):
        self.__run = new_run
        self.ui.lineEdit.setText(new_run.run_name)

    def set_cocktail_menu(self):
        if self.ui.radioButton.isChecked():
            self.current_menus = 's'
        elif self.ui.radioButton_2.isChecked():
            self.current_menus = 'm'
        self.ui.comboBox.addItems([menu.path for menu in self.current_menus])

    def select_run_menu(self):
        run_menu = self.run.cocktail_menu
        print(list(self.run.cocktail_menu.keys()))
        menu_index = self.ui.comboBox.findText(run_menu.path)
        if menu_index:
            self.ui.comboBox.setCurrentIndex(menu_index)

    def update_run_cocktail_menu(self):
        new_menu = tim.get_menu_by_path(self.ui.comboBox.setCurrentText())
        run.cocktail_menu = new_menu
        for i, image in enumerate(self.run.images):
            image.cocktail = self.run.cocktail_menu.cocktails[i]
            # update the cocktails for each image
            # should only do this for HWI runs

    def update_run_name(self):
        new_name = self.ui.lineEdit.text()
        if new_name not in self.run_names and new_name != self.run.run_name:
            self.run.run_name = new_name

    def update_spectrum(self):
        new_spectrum = self.ui.comboBox_2.currentText()
        if new_spectrum != self.run.image_spectrum:
            self.run.image_spectrum = new_spectrum
            for image in self.run.images:
                image.spectrum = new_spectrum

    def update_plate_id(self):
        new_id = self.ui.lineEdit_2.text()
        if new_id != self.run.plate_id:
            self.run.plate_id = new_id
