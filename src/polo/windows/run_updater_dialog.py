import json
import os

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QBrush, QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QGridLayout
from polo.designer.UI_run_updater_dialog import Ui_runUpdater

from polo import LOG_PATH, tim, IMAGE_SPECS, make_default_logger

logger = make_default_logger(__name__)


class RunUpdaterDialog(QtWidgets.QDialog):
    '''Small dialog for updating basic information about a run after
    it has been imported. Includes updating the plate ID, the cocktail
    menu used and the image spectrum.

    :param run: Run to update
    :type run: Run or HWIRun
    :param run_names: Names of already loaded runs.
    :type run_names: list or set
    :param parent: Parent widget, defaults to None
    :type parent: QWidget, optional
    '''

    def __init__(self, run, run_names, parent=None):
        super(RunUpdaterDialog, self).__init__(parent)
        self.ui = Ui_runUpdater()
        self.ui.setupUi(self)
        self.run = run
        self.run_names = run_names  # all currently used run names
        self.ui.pushButton_2.clicked.connect(self.close)
        self._set_cocktail_menu()
        self._select_run_menu()
        self._set_run_date()
        self.ui.radioButton.toggled.connect(self._set_cocktail_menu)
        self.ui.pushButton.clicked.connect(self._update_run)
        self.ui.comboBox_2.addItems(IMAGE_SPECS)


    @property
    def current_menus(self):
        '''The `CocktailMenu` instances that are currently being displayed
        to the user via the cocktail menu comboBox widget.

        :return: List of `CocktailMenu` instances 
        :rtype: list
        '''
        return self._current_menus

    @current_menus.setter
    def current_menus(self, type_key):
        if type_key == 's' or type_key == 'm':  # soluble or membrane
            self._current_menus = tim.get_menus_by_type(type_key)
        else:
            return []

    @property
    def run(self):
        '''The run being updated.

        :return: The run being updated
        :rtype: Run or HWIRun
        '''
        return self._run

    @run.setter
    def run(self, new_run):
        self._run = new_run
        logger.info('Opened new run {}'.format(self._run))
    
    def _set_run_date(self):
        '''Set the `date` attribute of the `run` based on
        the value in the dateEdit widget.
        '''
        if self.run:
            self.ui.dateEdit.setDate(self.run.date)

    def _set_cocktail_menu(self):
        '''Private method that display cocktails in the cocktail comboBox based on
        the current menu type selection. Either displays
        soluble or membrane cocktail menus.
        '''
        self.ui.comboBox.clear()
        if self.ui.radioButton.isChecked():
            self.current_menus = 's'
        elif self.ui.radioButton_2.isChecked():
            self.current_menus = 'm'

        self.ui.comboBox.addItems(
            [os.path.basename(menu.path) for menu in sorted(
                self.current_menus, key=lambda m: m.start_date)])

    def _select_run_menu(self):
        '''Private method that sets the current index of the comboBox
        based on the current `cocktail_menu` attribute of the `Run` instance 
        referenced by the `run` attribute.
        '''
        run_menu = self.run.cocktail_menu
        menu_index = self.ui.comboBox.findText(os.path.basename(run_menu.path))
        if menu_index:
            self.ui.comboBox.setCurrentIndex(menu_index)

    def _update_run_cocktail_menu(self):
        '''Private method that updates the `cocktail_menu` attribute of the 
        `Run` instance referenced by the `run` attribute based on the current 
        cocktail comboBox selection.
        '''
        new_menu = tim.get_menu_by_basename(self.ui.comboBox.currentText())
        if new_menu and new_menu.path != self.run.cocktail_menu.path:
            self.run.cocktail_menu = new_menu
            for i, image in enumerate(self.run.images):
                image.cocktail = self.run.cocktail_menu.cocktails[str(image.well_number)]

    # NOTE: Currently working on doing this one. Updating run name is a much bigger
    # deal since it is used as the key for identifying a run

    # def update_run_name(self):
    #     new_name = self.ui.lineEdit.text()
    #     if new_name not in self.run_names and new_name != self.run.run_name:
    #         self.run.run_name = new_name

    def _update_spectrum(self):
        '''Private method that update the spectrum of the `run` attribute 
        and the images in that run based on the current selection of the 
        spectrum comboBox.
        '''
        new_spectrum = self.ui.comboBox_2.currentText()
        if new_spectrum != self.run.image_spectrum:
            self.run.image_spectrum = new_spectrum
            for image in self.run.images:
                image.spectrum = new_spectrum

    def _update_plate_id(self):
        '''Private method that updates the `plate_id` attribute of the 
        Run instance references by the `run` attribute based on the contents
        of the plate ID lineEdit widget.
        '''
        new_id = self.ui.lineEdit_2.text()
        if new_id != self.run.plate_id:
            self.run.plate_id = new_id
    
    def _update_run(self):
        '''Private wrapper method that calls all other `_update` methods
        and then closes the dialog.
        '''
        # self.update_run_name()
        self._update_run_cocktail_menu()
        self._update_spectrum()
        self._update_plate_id()
        self.close()
