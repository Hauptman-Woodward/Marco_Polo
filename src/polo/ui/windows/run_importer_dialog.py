import os
from datetime import datetime


from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QDateTime, QPoint, Qt
from PyQt5.QtGui import QBrush, QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QGridLayout
from polo import make_default_logger
from polo.crystallography.run import HWIRun, Run
from polo.ui.designer.UI_run_importer import Ui_Dialog
from polo.utils.exceptions import EmptyRunNameError, ForbiddenImageTypeError
# from polo.threads.thread import LoadRunThread
from polo.utils.io_utils import (directory_validator, list_dir_abs,
                                 parse_cocktail_csv, parse_cocktail_metadata,
                                 parse_hwi_dir_metadata,
                                 read_import_descriptors, run_name_validator)

from polo import ALLOWED_IMAGE_COUNTS

from polo import tim  # the bartender

# TODO: Downloading function and reflect files in the actual FTP server
# Probably want to look into threads for downloading so not being done on
# the GUI thread

# TODO clear the field if there is an error relating to that feild
logger = make_default_logger(__name__)


class RunImporterDialog(QtWidgets.QDialog):
    '''
    Dialog that allows and controls how the user creates run objects from
    directories of images.
    '''

    def __init__(self, current_run_names):
        '''Create instance of RunImporterDialog. Used to import screening
        images from an uncompressed directory of images.

        :param current_run_names: Runnames that are already in use by the\
            current Polo session (Run names should be unique)
        :type current_run_names: list or set
        '''
        QtWidgets.QDialog.__init__(self)
        self.current_run_names = current_run_names
        # Data and UI setup
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.new_run = None

        # self.import_descriptors = read_import_descriptors()

        # Widget connections
        self.ui.listWidget.currentRowChanged.connect(
            self.display_selected_run_type)
        self.ui.pushButton.clicked.connect(self.set_image_directory)
        self.ui.pushButton_6.clicked.connect(self.set_image_directory)
        self.ui.pushButton_5.clicked.connect(self.set_image_directory)
        self.ui.lineEdit.editingFinished.connect(self.make_hwi_run_suggestions)
        self.ui.pushButton_2.clicked.connect(self.create_new_run)
        self.ui.radioButton.toggled.connect(self.set_menu_options)
        self.ui.radioButton_2.toggled.connect(self.set_menu_options)
        # self.ui.comboBox.currentIndexChanged.connect(
        #     self.validate_hwi_number_images_run)

        # Widget display setup
        self.set_menu_options()
        logger.info('Opened run importer dialog')
        self.exec_()

    @property
    def current_menu_type(self):
        if self.ui.radioButton.isChecked():
            return 'm'
        else:
            return 's'

    @property
    def soluble_menus(self):
        return tim.get_menus_by_type('s')
        # return tim.get_menus_by_type('s')  # returns menu objects

    @property
    def membrane_menus(self):
        return tim.get_menus_by_type('m')

    @property
    def current_dateEdit(self):
        current_index = self.ui.stackedWidget.currentIndex()
        if current_index == 0:
            return self.ui.dateEdit_2
        elif current_index == 1:
            return self.ui.dateEdit
        else:
            return self.ui.dateEdit_2

    @property
    def current_dir_path_lineEdit(self):
        current_index = self.ui.stackedWidget.currentIndex()
        if current_index == 0:
            return self.ui.lineEdit
        elif current_index == 1:
            return self.ui.lineEdit_5
        else:
            return self.ui.lineEdit_3

    @property
    def current_run_name_lineEdit(self):
        current_index = self.ui.stackedWidget.currentIndex()
        if current_index == 0:
            return self.ui.lineEdit_2
        elif current_index == 1:
            return self.ui.lineEdit_6
        else:
            return self.ui.lineEdit_4

    def get_menu_options(self):
        # set options depending on the radiobox selected
        if self.ui.radioButton.isChecked():  # membrane selected
            menus = self.membrane_menus
        else:
            menus = self.soluble_menus
        return sorted(menus, key=lambda menu: menu.start_date, reverse=True)

    def set_menu_options(self):
        options = self.get_menu_options()  # menu instances
        self.ui.comboBox_3.clear()
        self.ui.comboBox_3.addItems([menu.path for menu in options])

    def get_menu_index_by_path(self, menu_path):
        return self.ui.comboBox_3.findText(menu_path)

    def set_current_menu(self, menu):
        menu_index = self.get_menu_index_by_path(menu.path)
        if menu_index:
            return self.ui.comboBox_3.setCurrentIndex(menu_index)

    def set_hwi_image_type(self, image_type):
        if image_type == 'uvt':
            self.ui.comboBox_2.setCurrentIndex(1)
        elif image_type == 'jpg':
            self.ui.comboBox_2.setCurrentIndex(0)
        elif image_type == 'shg':
            self.ui.comboBox_2.setCurrentIndex(2)
        else:
            self.ui.comboBox_2.setCurrentIndex(3)

    def suggest_menu_by_date(self, image_date, menu_type=None):
        if not menu_type:
            menu_type = self.current_menu_type

        return tim.get_menu_by_date(image_date, menu_type)

    def make_hwi_run_suggestions(self):
        dir_path = self.ui.lineEdit.text()
        if os.path.exists(dir_path):
            dir_data = parse_hwi_dir_metadata(dir_path)
            if isinstance(dir_data, ValueError):
                self.show_error_message('Selected directory does not conform to HWI naming\
                    conventions. Could not make suggestions.')
                return False
            else:
                image_type, plate_id, date, run_name = dir_data
                self.ui.lineEdit_2.setText(run_name)
                self.set_hwi_image_type(image_type)
                self.set_menu_options()
                suggested_menu = self.suggest_menu_by_date(date)
                self.set_current_menu(suggested_menu)
                self.ui.dateEdit_2.setDate(date)
                return True

    def detect_missing_images(self, image_dir):
        # first check the number of images specified
        images = list_dir_abs(image_dir)
        if len(images) in ALLOWED_IMAGE_COUNTS:
            pass
            # make suggestion for number of images here
        else:
            pass
        # missing data, suggest using FTP to redownload images
        # or insert place holder images
        # also if suggestion is less than current number of images

    def set_image_directory(self):
        '''
        Opens a directory browser dialog and validates that directory
        as meeting the requirements for import. Then calls
        update_current_stack to update the lineEdit widget on the
        current page to reflect the selected directory. This is conditional
        on the selected directory being valid.
        '''
        dir_path = self.open_directory_browser()
        if dir_path:
            if self.validate_directory(dir_path):
                self.current_dir_path_lineEdit.setText(dir_path)
                if self.ui.stackedWidget.currentIndex() == 0:
                    # additional actions if loading in an HWI directory
                    self.make_hwi_run_suggestions()
                    self.validate_run_name(text=self.ui.lineEdit_2.text())

    def validate_hwi_number_images_run(self):
        '''
        Additional directory validation for HWI runs that is not required for
        non-HWI or raw image imports.
        '''
        hwi_image_dir = self.ui.lineEdit.text()
        if os.path.exists(hwi_image_dir):
            user_num_images = int(self.ui.comboBox.currentText())
            actual_image_count = len(list_dir_abs(hwi_image_dir, allowed=True))

            error, message = False, ''
            if actual_image_count > user_num_images:
                error = True
                message = '{} contains more than {} images. Increase number of images or \
                    import run as a non-HWI run.'.format(hwi_image_dir, user_num_images)
            elif actual_image_count < user_num_images:
                error = True
                message = '{} contains less than {} images. Run can still be imported as an\
                    HWI run but will be missing image data. You might want to redownload your\
                    images using the import from FTP function.'.format(hwi_image_dir, user_num_images)
            if error:
                self.show_error_message(message=message)
                return False
            else:
                return True

    def display_selected_run_type(self, i):
        '''
        Changes the Widget displayed in the stackWidget
        based on the given index i.

        param i: Int. Index of stackWidget to show to user.
        '''
        self.ui.stackedWidget.setCurrentIndex(i)

    def open_directory_browser(self):
        '''
        Opens a QFileDialog that only allows for selecting directories.
        Returns the path of the directory the user selects. Will be none
        is no directory is selected.
        '''
        browser = QtWidgets.QFileDialog(parent=self)
        browser.setFileMode(QtWidgets.QFileDialog.Directory)
        dirnames = ''
        if browser.exec():
            filenames = browser.selectedFiles()
            return filenames[0]

    def validate_directory(self, image_dir=None):
        '''
        Validates a given directory path and ensures that it meets
        the requirements to be imported without causing errors in
        other functions down the line. Shows error message corresponding to
        validation error if directory is not valid.

        In order for a directory to be valid it must exist, be a directory
        and contain at least one image of an allowed type.

        :param image_dir: String. Path to be validated.
        '''
        validator_result = directory_validator(image_dir)
        if validator_result == True:
            return True
        else:
            if validator_result == NotADirectoryError:
                message = '{} is not a directory. Could not complete import.'.format(
                    image_dir)
            elif validator_result == FileNotFoundError:
                message = '{} does not exist. Could not complete import.'.format(
                    image_dir)
            elif validator_result == ForbiddenImageTypeError:
                message = '{} does not contain any allowed image types'.format(
                    image_dir)
            self.show_error_message(message)

    def validate_run_name(self, text=None):
        '''
        Validates a given run name to ensure it can be used safely. Shows
        an error message to the user if the run name is not valid and clears
        the run name lineEdit widget.

        In order for a run name to be valid it must contain only UTF-8
        codable characters and not already be in use by another
        run object. This is because the run name is used as a key to refer
        to the run object in other functions.

        :param text: String. The run name to be validated.
        '''
        validator_result = run_name_validator(text, self.current_run_names)
        if validator_result == UnicodeError:
            self.show_error_message('Run name is not UTF-8 Compliant')
            self.current_run_name_lineEdit.setText('')
        elif validator_result == TypeError:
            self.show_error_message('Run name must not be empty.')
        elif not validator_result:  # result is false already exists
            self.show_error_message(
                message='Run name already exists, please pick a unique name.')
            self.current_run_name_lineEdit.setText('')
            # TODO option to overwrite the run of that same name
        else:
            self.current_run_name_lineEdit.setText(text)
            return True

    def show_error_message(self, message=':('):
        '''
        Helper method for showing a QErrorMessage dialog to the user.

        :param message: String. The message text to show to the user.
        '''
        err = QtWidgets.QErrorMessage(parent=self)
        err.showMessage(message)
        err.exec_()

    def create_new_run(self):
        '''
        Creates a new run based on the information contained in the widgets
        of the current stackedWidget index. If a run is able to be created successfully
        then the new_run attribute is set to point at the new run object.
        '''
        current_index = self.ui.stackedWidget.currentIndex()
        new_run = None
        run_name = self.current_run_name_lineEdit.text()
        dir_name = self.current_dir_path_lineEdit.text()
        date = self.current_dateEdit.dateTime().toPyDateTime()

        if self.validate_run_name(text=run_name) and self.validate_directory(dir_name):
            if current_index == 0:
                cocktail_dict = tim.get_menu_by_path(
                    self.ui.comboBox_3.currentText()).cocktails
                new_run = HWIRun(
                    image_dir=dir_name,
                    run_name=run_name,
                    cocktail_dict=cocktail_dict,
                    image_spectrum=self.ui.comboBox_2.currentText(),
                    date=date
                )
            else:
                image_spectrum = None  # TODO add spectrum selection for all runs
                if current_index == 2:
                    image_spectrum = self.ui.comboBox_4.currentText()

                new_run = Run(image_dir=dir_name, run_name=run_name,
                              image_spectrum=image_spectrum, date=date)
            if new_run != None:
                new_run.add_images_from_dir()
                self.new_run = new_run
                self.close()

# open a thread to create a new run and add a loading screen or at
# least change the cursor
