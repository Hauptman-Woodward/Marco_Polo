import os
from datetime import datetime
from random import randint


from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QDateTime, QPoint, Qt
from PyQt5.QtCore import QItemSelectionModel
from PyQt5.QtGui import QBrush, QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QGridLayout
from polo import make_default_logger
from polo.crystallography.run import HWIRun, Run
from polo.designer.UI_multi_run_importer import Ui_multiImporter
# from polo.threads.thread import LoadRunThread
from polo.utils.io_utils import (
    list_dir_abs, run_name_validator, RunDeserializer)
from polo.utils.unrar_utils import *
from polo.utils.dialog_utils import make_message_box
from polo.utils.io_utils import XmlReader

from polo import ALLOWED_IMAGE_COUNTS, IMAGE_SPECS

from polo import bartender, IMAGE_SPECS, SPEC_KEYS  # the bartender

from polo.threads.thread import QuickThread
from PyQt5.QtWidgets import QApplication
from polo.utils.io_utils import *


class RunImporterDialog(QtWidgets.QDialog):
    '''RunImporterDialog instances are the user interface for importing
    runs from rar archives or directories stored on the local machine. 

    :param current_run_names: Runnames that are already in use by the
                                current Polo session (Run names should be unique)
    :type current_run_names: list or set
    '''

    def __init__(self, current_run_names, parent=None):
        super(RunImporterDialog, self).__init__(parent)
        self.current_run_names = current_run_names
        self.ui = Ui_multiImporter()
        self.ui.setupUi(self)
        self.import_candidates = {}
        self.can_unrar = test_for_working_unrar()
        if not self.can_unrar:
            self.pushButton_4.setEnabled(False)
        self._last_selection = None

        self.ui.lineEdit.editingFinished.connect(self._verify_run_name)
        self.ui.pushButton_4.clicked.connect(lambda: self._import_files(rar=True))
        self.ui.pushButton_5.clicked.connect(lambda: self._import_files(rar=False))
        self.ui.listWidget.currentItemChanged.connect(
            self._handle_candidate_change)
        self.ui.radioButton.toggled.connect(self._display_cocktail_files)
        self.ui.pushButton.clicked.connect(self._close_dialog)
        self.ui.pushButton_2.clicked.connect(self._remove_run)
        #self.ui.pushButton_3.clicked.connect(self._restore_defaults)
        self._display_cocktail_files()

    @property
    def all_run_names(self):
        '''All run names of all current :class:ImportCandidate
        instances.

        :return: Set of all run names
        :rtype: set
        '''
        return set(
            [can_path.__dict__['run_name'] for can_path in self.import_candidates.values()
             if 'run_name' in can_path.__dict__] + self.current_run_names
        )

    @property
    def selected_candidate(self):
        '''The currently selected :class:`ImportCandidate` if one exists, otherwise
        returns None.

        :return: Currently selected candidate
        :rtype: ImportCandidate
        '''
        return self._selected_candidate

    @selected_candidate.setter
    def selected_candidate(self, new_candidate_str):
        if new_candidate_str in self.import_candidates:
            self._selected_candidate = self.import_candidates[new_candidate_str]
        else:
            self._selected_candidate = None

    @property
    def selection_dict(self):
        '''Returns a dictionary who's keys are :class:`Run` attributes and values
        are the values of :class:`RunImporterDialog` widgets that correspond to
        these attributes.

        Example of the dictionary returned below.

        .. code-block:: python
        
            {
                'cocktail_menu': Menu,
                'date': datetime,
                'run_name': str,
                'image_spectrum': str
            }

        :return: dict
        :rtype: dict
        '''
        return {
            'cocktail_menu': bartender.get_menu_by_basename(self.ui.comboBox_3.currentText()),
            'date': self.ui.dateEdit_2.dateTime().toPyDateTime(),
            'run_name': self.ui.textEdit.text(),
            'image_spectrum': self.ui.comboBox_2.currentText()
        }  # need to hardy this up to prevent errors
    
    def _could_not_import_message(self, prefix, paths):
        '''Private method that creates a message box popup for when imports fail.

        :param prefix: First part of the error message. Something
                       like "Could not import the following files:"
        :type prefix: str
        :param paths: List of filepaths that could not be imported
        :type paths: list
        :return: QMessageBox
        :rtype: QMessageBox
        ''' 
        message = [prefix] + [str(p) for p in paths]
        return make_message_box(
            message='\n'.join(message),
            parent=self
        )
    
    def _import_files(self, rar=True):
        '''
        :param rar: If True opens the filebrowser for rar archives and filters
                    out all other import types, defaults to True
        :type rar: bool, optional
        '''
        file_paths = self._open_browser(rar=rar)
        if file_paths:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            file_path = file_paths.pop()
            importer = RunImporter(file_path)
            self.import_thread = importer.create_import_thread()
            
            def finished_import_thread(file_path):
                result = self.import_thread.result
                if isinstance(result, (str, Path)) and Path(result).is_dir():
                    for run_type in RUN_TYPES:
                        try:
                            result = run_type.init_from_directory(result)
                            result.add_images_from_dir()
                            break
                        except Exception as e:
                            continue
                
                if isinstance(result, Run):
                    self.import_candidates[file_path] = result
                
                self.import_thread = None
                while not self.import_thread and file_paths:
                    file_path = file_paths.pop()
                    importer = RunImporter(file_path)
                    self.import_thread = importer.create_import_thread()
                
                if self.import_thread:
                    self.import_thread.finished.connect(
                        lambda: finished_import_thread(file_path))
                    self.import_thread.start()
                else:
                    self._display_candidate_paths()
                    QApplication.restoreOverrideCursor()
            
            if self.import_thread:
                self.import_thread.finished.connect(
                    lambda: finished_import_thread(file_path))
                self.import_thread.start()
            else:
                make_message_box(
                    parent=self,
                    message='Could not import {}'.format(file_path)
                ).exec_()
                QApplication.restoreOverrideCursor()
    
    def _close_dialog(self):
        # Closes the dialog and updates the last select run
        current_item = self.ui.listWidget.currentItem()
        if current_item:
            current_item_path = current_item.text()
            self._update_candidate_run_data(current_item_path)
            self.close()
    
    def _open_browser(self, rar=True):
        '''Private method that opens a :class:`QFileBrowser` instance that allows the 
        user to select files for import. 
        The allowed filetype is set using the `rar` flag.

        :param rar: If True, allow user to only import Rar archive files 
                            defaults to True. If False
                            only allows the user to import directories.
        :type rar: bool, optional
        :return: List of files the user has selected for import 
        :rtype: list
        '''
        if rar:
            mode = QtWidgets.QFileDialog.ExistingFiles
            file_filter = 'Rar archives (*.rar)'
        else:
            mode = QtWidgets.QFileDialog.DirectoryOnly
            file_filter = ''

        browser = QtWidgets.QFileDialog(self, filter=file_filter)
        browser.setFileMode(mode)
        browser.exec_()
        return browser.selectedFiles()

    def _handle_candidate_change(self):
        '''TODO: Needs rewrite for clarity 
        
        Private method that calls 
        :meth:`~polo.windows.run_importer.RunImporterDialog._update_selected_candidate`
        and then  :meth:`~polo.windows.run_importer.RunImporterDialog._populate_fields`. 
        This updates the data of the previously selected 
        :class:`ImportCandidate` if it has been changed and then
        updates data display widgets with the information from the currently selected
        :class:`ImportCandidate` instance.
        '''
        current_item = self.ui.listWidget.currentItem()
        if current_item:
            current_item_text = current_item.text()
            if self._last_selection:
                self._update_candidate_run_data(self._last_selection)
            self._populate_fields(self.import_candidates[current_item_text])
            self._last_selection = current_item_text

    def _verify_run_name(self):
        '''Private method to verify a run name. If run name fails verification
        clears the runname :class:`QLineEdit` widget and shows an error message to the user.
        '''
        run_name, error, message = self.ui.lineEdit.text(), False, ''
        if run_name in self.all_run_names:
            if ('run_name' in self.selected_candidate.__dict__  # run name has actually changed
                and self.selected_candidate.__dict__['run_name'] != run_name):
                error, message = True, '{} all ready in use.'.format(run_name)
        if run_name == '':
            error, message = True, 'Run name must not be empty'
        if error:
            make_message_box(
                message=message, parent=self
            ).exec_()
            self.ui.lineEdit.clear()

    def _remove_run(self):
        '''Removes a run as an import candidate and refreshes the 
        :class:`QlistWidget` to reflect the removal.
        '''
        try:
            current_item = self.ui.listWidget.currentItem()
            if current_item:
                file_path = current_item.text()
                if file_path in self.import_candidates:
                    self.import_candidates.pop(file_path)
                    self._display_candidate_paths()
            else:
                make_message_box(
                    parent=self, message='Please select a run first'
                ).exec_()
        except Exception as e:
            logger.error('Caught {} at {}'.format(e, self._restore_defaults))
            make_message_box(
                parent=self, message='Could not remove import. {}'.format(e)
                ).exec_()

    def _display_candidate_paths(self):
        '''rewrite import candidate class is no longer used
        '''
        self.ui.listWidget.clear()
        self.ui.listWidget.addItems(
            sorted(list(self.import_candidates.keys())))
        self.ui.listWidget.repaint()  # catalina os patch

    def _populate_fields(self, import_candidate):
        '''TODO: Needs a rewrite 
        '''
        try:
            if isinstance(import_candidate, HWIRun):
                self._enable_hwi_import_tools()
            else:
                self._disable_hwi_import_tools()

            for key, value in import_candidate.__dict__.items():
                if value:  # only proceed is actually have value to use
                    if key == 'cocktail_menu':
                        self._set_cocktail_menu(import_candidate)
                    elif key == 'image_spectrum':
                        self._set_image_spectrum(value)
                        pass
                    elif key == 'run_name':
                        self.ui.lineEdit.setText(str(value))
                    elif key == 'date':
                        self.ui.dateEdit_2.setDate(value)
        except Exception as e:
            logger.error('Caught {} at {}'.format(e, self._populate_fields))
            make_message_box(
                parent=self,
                message='Failed to refresh fields {}'.format(e)
            ).exec_()

    def _set_cocktail_menu(self, import_candidate):
        '''Private method that sets the cocktail :class:`QComboBox` based on the
        :class:`~polo.utils.io_utils.Menu` instance referenced by the 
        :attr:`selected_candidate`attribute. This method is used to convey to
        the user which
        :class:`~polo.utils.io_utils.Menu` has been selected for a given
        :class:`ImportCandidate`.
        '''
        if ('cocktail_menu' in import_candidate.__dict__
                and isinstance(import_candidate.__dict__['cocktail_menu'], Menu)
            ):
            menu = import_candidate.__dict__['cocktail_menu']
            self._display_cocktail_files(menu_type=menu.type_)
            menu_name = os.path.basename(menu.path)
            menu_index = self.ui.comboBox_3.findText(menu_name)
            if menu_index >= 0:
                self.ui.comboBox_3.setCurrentIndex(menu_index)

    def _set_cocktail_menu_type_radiobuttons(self, type_):
        '''Private method that sets the :class:`~polo.utils.io_utils.Menu` 
        type :class:`QRadioButtons`
        given a :class:`~polo.utils.io_utils.Menu` type key.

        :param type_: Menu type key. If `type_` == 's' then soluble
                      menu radioButton state is set to True. If 'type_` == 'm' then
                      membrane radiobutton state is set to True
        :type type_: str
        '''
        if type_ == 'm':
            self.ui.radioButton.setChecked(True)
        elif type_ == 's':
            self.ui.radioButton_2.setChecked(True)

    def _enable_hwi_import_tools(self):
        '''Private method to enable widgets that should only be used
        for :class:`HWIRun` imports. 
        '''
        items = (self.ui.gridLayout.itemAt(i)
                 for i in range(self.ui.gridLayout.count()))
        for i in items:
            widget = i.widget()
            if hasattr(widget, 'setEnabled'):
                widget.setEnabled(True)

    def _disable_hwi_import_tools(self):
        '''Private method to disable widgets that should only be used for
        :class:`HWIRun` imports.
        '''
        self.ui.comboBox_3.setEnabled(False)
        self.ui.radioButton.setEnabled(False)
        self.ui.radioButton_2.setEnabled(False)

    def _set_image_spectrum(self, spectrum):
        '''Private method that sets the image spectrum comboBox
        based on the `spectrum` argument. Should be used to display
        the inferred spectrum of an import candidate to the user when
        that candidate is selected. 

        :param spectrum: Spectrum key
        :type spectrum: str
        '''
        i = self.ui.comboBox_2.findText(spectrum)
        if i >= 0:
            self.ui.comboBox_2.setCurrentIndex(i)

    def _display_cocktail_files(self, menu_type=None):
        '''Private method that displays the available cocktail files to the
        user via the :class:`~polo.utils.io_utils.Menu` :class:`QComboBox` widget.

        :param menu_type: Key for which kind of cocktail screens to display, defaults to None. 
                          "m" for membrane screens and "s" for soluble screens.
        :type menu_type: str, optional
        '''
        self.ui.comboBox_3.clear()
        if menu_type == 's' or menu_type == 'm':
            self._set_cocktail_menu_type_radiobuttons(menu_type)
        if self.ui.radioButton_2.isChecked():  # soluble screens
            menus = bartender.get_menus_by_type('s')
        elif self.ui.radioButton.isChecked():  # membrane screens
            menus = bartender.get_menus_by_type('m')

        menus = [os.path.basename(menu.path) for menu in sorted(
            menus, key=lambda m: m.start_date)]

        self.ui.comboBox_3.addItems(menus)

    def _update_candidate_run_data(self, import_candidate_path):
        '''Rewrite
        '''
        import_candidate = self.import_candidates[import_candidate_path]
        selection_dict = {
            'run_name': self.ui.lineEdit.text(),
            'image_spectrum': self.ui.comboBox_2.currentText(),
            'date': self.ui.dateEdit_2.dateTime().toPyDateTime()
        }
        if isinstance(import_candidate, HWIRun):
            selection_dict['cocktail_menu'] = bartender.get_menu_by_basename(
                self.ui.comboBox_3.currentText()
            )
        self.import_candidates[import_candidate_path].__dict__.update(selection_dict)
        

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
            paths = []
            for url in event.mimeData().urls():
                path = Path(str(url.toLocalFile()))
        else:
            event.ignore()
