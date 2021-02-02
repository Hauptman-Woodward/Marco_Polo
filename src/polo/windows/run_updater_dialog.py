import json
import os

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QAction, QGridLayout
from polo.designer.UI_run_updater_dialog import Ui_runUpdater
from polo.utils.dialog_utils import make_message_box
from polo.utils.io_utils import RunLinker

from polo import LOG_PATH, bartender, IMAGE_SPECS, make_default_logger

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
    updated_run_signal = pyqtSignal(list)

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
        '''The :class:`polo.utils.io_utils.Menu` instances that are currently being displayed
        to the user via the :class:`~polo.utils.io_utils.Menu` ::class:`QComboBox` widget.

        :return: List of :class:`polo.utils.io_utils.Menu` instances 
        :rtype: list
        '''
        return self._current_menus

    @current_menus.setter
    def current_menus(self, type_key):
        if type_key == 's' or type_key == 'm':  # soluble or membrane
            self._current_menus = bartender.get_menus_by_type(type_key)
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
        logger.debug('Opened new run {}'.format(self._run))
    
    def _set_run_date(self):
        '''Set the :attr:`date` attribute of the :class:`Run` referenced
        by the :attr:`run` attribute from 
        the value in the :class:`QDateEdit` widget.
        '''
        if self.run:
            self.ui.dateEdit.setDate(self.run.date)

    def _set_cocktail_menu(self):
        '''Private method that display cocktails in the 
        :class:`~polo.utils.io_utils.Menu` :class:`QComboBox` based on
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
        '''Private method that sets the current index of the  :class:`QComboBox`
        based on the current :attr:`cocktail_menu` attribute of the :class:`Run`
        instance  referenced by the :attr:`run` attribute.
        '''
        run_menu = self.run.cocktail_menu
        menu_index = self.ui.comboBox.findText(os.path.basename(run_menu.path))
        if menu_index:
            self.ui.comboBox.setCurrentIndex(menu_index)

    def _update_run_cocktail_menu(self):
        '''Private method that updates the `cocktail_menu` attribute of the 
        `Run` instance referenced by the :attr:`run` attribute based on the current 
        :class:`~polo.utils.io_utils.Menu` :class:`QComboBox` selection.
        '''
        new_menu = bartender.get_menu_by_basename(self.ui.comboBox.currentText())
        if new_menu and new_menu.path != self.run.cocktail_menu.path:
            self.run.cocktail_menu = new_menu
            for i, image in enumerate(self.run.images):
                image.cocktail = self.run.cocktail_menu.cocktails[image.well_number]

    # NOTE: Currently working on doing this one. Updating run name is a much bigger
    # deal since it is used as the key for identifying a run

    # def update_run_name(self):
    #     new_name = self.ui.lineEdit.text()
    #     if new_name not in self.run_names and new_name != self.run.run_name:
    #         self.run.run_name = new_name

    def _update_spectrum(self):
        '''Private method that update the spectrum of the :attr:`run` attribute 
        and the images in that run based on the current selection of the 
        spectrum  :class:`QComboBox`.
        '''
        new_spectrum = self.ui.comboBox_2.currentText()
        if new_spectrum != self.run.image_spectrum:
            self.run.image_spectrum = new_spectrum
            for image in self.run.images:
                image.spectrum = new_spectrum
            all_linked_runs = self.run.get_linked_date_runs() + self.run.get_linked_alt_runs()
            RunLinker.the_big_link(all_linked_runs)
    
    def _update_date(self):
        # TODO make this work. Currently need to work out issues caused with
        # run linking when dates are changed. Since dates are used in the sample
        # display need to remove the node corresponding to the run that has
        # been updated and then reinsert and relink.

        new_date = self.ui.dateEdit.dateTime().toPyDateTime()

        # could add this functionality to setters for date instead of
        # handeling here

        if new_date != self.run.date:
            self.run.date = new_date
            for image in self.run.images:
                image.date = new_date
            linked_runs = self.run.get_linked_date_runs()
            if len(linked_runs) > 1:
                for run in linked_runs:
                    for image in run.images:
                        image.next_image = None
                        image.previous_image = None
                    run.next_run = None
                    run.previous_run = None
        

    def _update_plate_id(self):
        '''Private method that updates the `plate_id` attribute of the 
        Run instance references by the :attr:`run` attribute based on the contents
        of the plate ID :class:`QLineEdit` widget.
        '''
        new_id = self.ui.lineEdit_2.text()
        if new_id != self.run.plate_id:
            self.run.plate_id = new_id
    
    def _update_run(self):
        '''Private wrapper method that calls all other `_update` methods
        and then closes the dialog.
        '''
        # self.update_run_name()
        try:
            self._update_run_cocktail_menu()
            self._update_spectrum()
            self._update_plate_id()
            self._update_date()
            self.updated_run_signal.emit([self.run])
        except Exception as e:
            logger.error('Caught {} calling {}'.format(e, self._update_run))
            make_message_box(
                parent=self,
                message='Could not update run {}'.format(e)
            ).exec_()
        self.close()
