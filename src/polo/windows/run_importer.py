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

from polo import tim, IMAGE_SPECS, SPEC_KEYS  # the bartender

from polo.threads.thread import QuickThread
from PyQt5.QtWidgets import QApplication
from polo.utils.io_utils import *


class ImportCandidate():

    def __init__(self, path):
        self.data = {}
        self.path = Path(path)
        self.import_type = None
        self.is_verified = False

    @property
    def is_rar(self):
        if self.path.suffix == '.rar':
            return True
        else:
            return False

    @property
    def cocktail_menu(self):
        if isinstance(self.import_type, HWIRun) and 'date' in self.data:
            return tim.get_menu_by_date(self.data['date'])
        else:
            return None

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, new_path):
        self._path = new_path
        self.data['run_name'] = os.path.basename(str(new_path))
        # set basename of the directory as the default run name

    def unrar(self):
        if self.is_rar:
            unrar_result = unrar_archive(
                self.path, target_dir=self.path.parent)
            if isinstance(unrar_result, Path):
                self.path = unrar_result
                return self.path
        return False

    def read_xmldata(self, dir_path):
        # read xml data from HWI uncompressed rar files
        reader = XmlReader(dir_path)
        platedata = reader.find_and_read_platedata(dir_path)
        if isinstance(platedata, dict) and platedata:
            return platedata
        else:
            return {}  # empty dict so always safe to pass to update method

    def verify_path(self):
        str_path = str(self.path)
        if os.path.exists(str_path):
            if self.is_rar and os.path.isfile(str_path):
                self.is_verified = True
            else:
                if RunImporter.directory_validator(str_path) is True:
                    self.is_verified = True
        return self.is_verified

    def assign_run_type(self):
        if self.is_verified:  # should be a directory now
            hwi_data = RunImporter.parse_hwi_dir_metadata(self.path)
            if isinstance(hwi_data, dict):
                self.data.update(hwi_data)
                self.import_type = HWIRun
                self.set_cocktail_menu()
            else:
                self.import_type = Run
            return self.import_type

    def set_cocktail_menu(self):
        if 'date' in self.data and isinstance(self.data['date'], datetime):
            self.data['cocktail_menu'] = tim.get_menu_by_date(
                self.data['date'], type_='s')

    def __hash__(self):
        return hash(self.path)

    def __str__(self):
        return str(self.path)


class RunImporterDialog(QtWidgets.QDialog):
    '''
    Dialog that allows and controls how the user creates run objects from
    directories of images.
    '''
    HWI_INDEX, NON_HWI_INDEX, RAW_INDEX = 0, 1, 2

    # data_to_widgets = {
    #     'cocktail_menu': self.ui.comboBox_3,
    #     'date': self.ui.dateEdit_2,
    #     'image_spectrum': self.ui.comboBox_2,
    #     'run_name': self.ui.lineEdit
    # }

    def __init__(self, current_run_names, parent=None):
        '''Create instance of RunImporterDialog. Used to import screening
        images from an uncompressed directory of images.

        :param current_run_names: Runnames that are already in use by the\
            current Polo session (Run names should be unique)
        :type current_run_names: list or set
        '''
        super(RunImporterDialog, self).__init__(parent)
        self.current_run_names = current_run_names
        self.ui = Ui_multiImporter()
        self.ui.setupUi(self)
        self.import_candidates = {}
        self.imported_runs = {}
        self.can_unrar = test_for_working_unrar()
        if not self.can_unrar:
            self.pushButton_4.setEnabled(False)
        self.selected_candidate = None
        self.ui.lineEdit.editingFinished.connect(self._verify_run_name)
        self.ui.pushButton_4.clicked.connect(lambda: self._import_files(rar=True))
        self.ui.pushButton_5.clicked.connect(lambda: self._import_files(rar=False))
        self.ui.listWidget.currentItemChanged.connect(
            self._handle_candidate_change)
        self.ui.radioButton.toggled.connect(self._display_cocktail_files)
        self.ui.pushButton.clicked.connect(self._import_runs)
        self.ui.pushButton_2.clicked.connect(self._remove_run)
        self._display_cocktail_files()

    @property
    def all_run_names(self):
        return set(
            [can_path.data['run_name'] for can_path in self.import_candidates.values()
             if 'run_name' in can_path.data] + self.current_run_names
        )

    @property
    def selected_candidate(self):
        return self._selected_candidate

    @selected_candidate.setter
    def selected_candidate(self, new_candidate_str):
        if new_candidate_str in self.import_candidates:
            self._selected_candidate = self.import_candidates[new_candidate_str]
        else:
            self._selected_candidate = None

    @property
    def selection_dict(self):
        return {
            'cocktail_menu': tim.get_menu_by_basename(self.ui.comboBox_3.currentText()),
            'date': self.ui.dateEdit_2.dateTime().toPyDateTime(),
            'run_name': self.ui.textEdit.text(),
            'image_spectrum': self.ui.comboBox_2.currentText()
        }  # need to hardy this up to prevent errors
    
    def _could_not_import_message(self, prefix, paths):
        message = [prefix] + [str(p) for p in paths]
        return make_message_box(
            message='\n'.join(message),
            parent=self
        )

    def _import_files(self, rar=True):
        file_paths = self._open_browser(rar=rar)
        if file_paths:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            import_candidates = [ImportCandidate(p) for p in file_paths]
            import_candidates, drop_outs = self._test_candidate_paths(
                import_candidates)
            if drop_outs:
                self._could_not_import_message(
                    'Could not import the following paths:',
                    drop_outs
                ).exec_()

            if rar:
                self.import_thread = QuickThread(
                    self._unrar_candidate_paths, candidate_paths=import_candidates)
            else:
                self.import_thread = QuickThread(
                    lambda: import_candidates  # dummy thread
                )
            
            def _finish_file_import():
                self.setEnabled(True)
                if isinstance(self.import_thread.result, tuple):
                    import_candidates, failed_unrars = self.import_thread.result
                    if failed_unrars:
                        make_message_box(
                            message='\n'.join(
                                ['The following imports failed:\n'] + failed_unrars),
                            parent=self
                        ).exec_()
                else:
                    import_candidates = self.import_thread.result
                
                if import_candidates:
                    [imp_can.assign_run_type() for imp_can in import_candidates]
                    self._add_import_candidates(import_candidates)
                    self._display_candidate_paths()
                QApplication.restoreOverrideCursor()
            
            self.import_thread.finished.connect(_finish_file_import)
            self.setEnabled(False)
            self.import_thread.start()


    def _open_browser(self, rar=True):
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

    def _update_selected_candidate(self):
        new_candidate = self.ui.listWidget.currentItem()
        if new_candidate:
            new_candidate = new_candidate.text()
            if self.selected_candidate:
                self._update_candidate_run_data()
                # update with the current data in the display
            self.selected_candidate = new_candidate
            self._populate_fields(self.selected_candidate)

    def _handle_candidate_change(self):
        # connect to when index changed of list widget
        self._update_selected_candidate()
        self._populate_fields(self.selected_candidate)

    def _unrar_candidate_paths(self, candidate_paths):
        unrared_paths, failed_unrar = [], []
        if self.can_unrar:
            for path in candidate_paths:
                if path.is_rar:                     
                    result = path.unrar()
                    if result:
                        path.path = result
                        unrared_paths.append(path)
                    else:
                        failed_unrar.append(str(path))
        return unrared_paths, failed_unrar

    def _verify_run_name(self):
        run_name, error, message = self.ui.lineEdit.text(), False, ''
        if run_name in self.all_run_names:
            if 'run_name' in self.selected_candidate.data and self.selected_candidate.data['run_name'] != run_name:
                error, message = True, '{} all ready in use.'.format(run_name)
        if run_name == '':
            error, message = True, 'Run name must not be empty'
        if error:
            make_message_box(
                message=message, parent=self
            ).exec_()
            self.ui.lineEdit.clear()

    def _restore_defaults(self):
        self.selected_candidate.assign_run_type()  # reread the metadata
        self._populate_fields()

    def _remove_run(self):
        key = str(self.selected_candidate.path)
        if key in self.import_candidates:
            self.import_candidates.pop(key)
        self._display_candidate_paths()

    def _test_candidate_paths(self, file_paths):
        # should be directories at this point get paths should return canidate
        # paths
        verified_paths, bad_paths = [], []
        for path in file_paths:
            path.verify_path()
            if path.is_verified:
                verified_paths.append(path)
                continue
            bad_paths.append(path)

        return verified_paths, bad_paths
    
    def _add_import_candidates(self, new_candidates):
        self.import_candidates.update(
            {str(can.path): can for can in new_candidates}
        )

    def _display_candidate_paths(self):
        self.ui.listWidget.clear()
        self.ui.listWidget.addItems(
            sorted(list(self.import_candidates.keys())))

    def _show_import_error_message(self, unimported_paths):
        make_message_box(
            message='Could not import the following items:'
        ).exec_()

    def open_file_browser(self, rar=False, dir=False):
        pass

    def make_run(self, import_candidate):
        if isinstance(import_candidate.import_type, HWIRun):
            pass

    def _populate_fields(self, import_candidate):
        if issubclass(import_candidate.import_type, Run):
            self._enable_hwi_import_tools()
        else:
            self._disable_hwi_import_tools()

        for key, value in import_candidate.data.items():
            if key == 'cocktail_menu':
                self._set_cocktail_menu()
            elif key == 'image_spectrum':
                self._set_image_spectrum(value)
                pass
            elif key == 'run_name':
                self.ui.lineEdit.setText(str(value))
            elif key == 'date':
                self.ui.dateEdit_2.setDate(value)

    def _set_cocktail_menu(self):
        if ('cocktail_menu' in self.selected_candidate.data
                and isinstance(self.selected_candidate.data['cocktail_menu'], Menu)
                ):
            menu = self.selected_candidate.data['cocktail_menu']
            self._display_cocktail_files(menu_type=menu.type_)
            menu_name = os.path.basename(menu.path)
            menu_index = self.ui.comboBox_3.findText(menu_name)
            if menu_index >= 0:
                self.ui.comboBox_3.setCurrentIndex(menu_index)

    def _set_cocktail_menu_type_radiobuttons(self, type_):
        if type_ == 'm':
            self.ui.radioButton.setChecked(True)
        elif type_ == 's':
            self.ui.radioButton_2.setChecked(True)

    def _enable_hwi_import_tools(self):
        items = (self.ui.gridLayout.itemAt(i)
                 for i in range(self.ui.gridLayout.count()))
        for i in items:
            widget = i.widget()
            if hasattr(widget, 'setEnabled'):
                widget.setEnabled(True)

    def _set_image_spectrum(self, spectrum):
        i = self.ui.comboBox_2.findText(spectrum)
        if i >= 0:
            self.ui.comboBox_2.setCurrentIndex(i)

    def _import_runs(self):
        self.setEnabled(False)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        for run_name, candidate in self.import_candidates.items():
            new_run = self._import_run(candidate)
            if isinstance(new_run, (HWIRun, Run)):
                self.imported_runs[run_name] = new_run
        QApplication.restoreOverrideCursor()
        self.close()

    def _import_run(self, import_candidate):
        new_run = None
        import_type = import_candidate.import_type
        if issubclass(import_type, HWIRun):
            new_run = RunImporter.import_hwi_run(str(import_candidate.path),
                                                 **import_candidate.data)
        elif issubclass(import_type, Run):
            new_run = RunImporter.import_general_run(str(import_candidate.path),
                                                     **import_candidate.data)

        return new_run

    def _disable_hwi_import_tools(self):
        self.ui.comboBox_3.setEnabled(False)
        self.ui.radioButton.setEnabled(False)
        self.ui.radioButton_2.setEnabled(False)

    def _display_cocktail_files(self, menu_type=None):
        self.ui.comboBox_3.clear()
        if menu_type == 's' or menu_type == 'm':
            self._set_cocktail_menu_type_radiobuttons(menu_type)
            # self._display_cocktail_files()
        if self.ui.radioButton_2.isChecked():  # soluble screens
            menus = tim.get_menus_by_type('s')
        elif self.ui.radioButton.isChecked():
            menus = tim.get_menus_by_type('m')

        menus = [os.path.basename(menu.path) for menu in sorted(
            menus, key=lambda m: m.start_date)]

        self.ui.comboBox_3.addItems(menus)

    def _update_candidate_run_data(self):
        if self.selected_candidate:
            selection_dict = {
                'run_name': self.ui.lineEdit.text(),
                'image_spectrum': self.ui.comboBox_2.currentText(),
                'date': self.ui.dateEdit_2.dateTime().toPyDateTime()
            }
            if issubclass(self.selected_candidate.import_type, HWIRun):
                selection_dict['cocktail_menu'] = tim.get_menu_by_basename(
                    self.ui.comboBox_3.currentText()
                )
            self.selected_candidate.data.update(selection_dict)
