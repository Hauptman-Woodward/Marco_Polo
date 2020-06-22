import os
from datetime import datetime


from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QDateTime, QPoint, Qt
from PyQt5.QtCore import QItemSelectionModel
from PyQt5.QtGui import QBrush, QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QGridLayout
from polo import make_default_logger
from polo.crystallography.run import HWIRun, Run
from polo.designer.UI_run_importer import Ui_Dialog
from polo.utils.exceptions import EmptyRunNameError, ForbiddenImageTypeError
# from polo.threads.thread import LoadRunThread
from polo.utils.io_utils import (directory_validator, list_dir_abs,
                                 parse_hwi_dir_metadata, run_name_validator)
from polo.utils.unrar_utils import *
from polo.utils.dialog_utils import make_message_box

from polo import ALLOWED_IMAGE_COUNTS

from polo import tim  # the bartender

from polo.threads.thread import QuickThread
from PyQt5.QtWidgets import QApplication

# TODO: Downloading function and reflect files in the actual FTP server
# Probably want to look into threads for downloading so not being done on
# the GUI thread

# TODO clear the field if there is an error relating to that feild
logger = make_default_logger(__name__)

import_descriptors = [  # TODO Move this into a text file
        '''Use HWI image import for screening runs conducted at the 
        Hauptman-Woodward Medical Research Insitutue High-Throughput
        Crystallization Screening Center. Polo includes all current and past 
        crystallization cocktail menus for HWI screens and will automatically
        extract metadata from your imported files based on current HWI
        file naming conventions.''',
        '''Use raw image import for importing a directory of misc images into 
        Polo. Be aware that using inconsistent image sizes and types may cause
        unexpected behavior from Polo.''',
        '''Use Non-HWI image import settings for crystallization images taken
        at a high-throughput facility other than the one at HWI. Currently you
        cannot specify alternative metadata parsing methods or cocktail menus
        outside of HWI.'''
]


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
        self.can_unrar = test_for_working_unrar()

        # self.import_descriptors = read_import_descriptors()

        # Widget connections
        self.ui.listWidget.currentRowChanged.connect(
            self.display_selected_run_type)
        self.ui.pushButton.clicked.connect(self.handle_browse_request)
        self.ui.pushButton_6.clicked.connect(self.handle_browse_request)
        self.ui.pushButton_5.clicked.connect(self.handle_browse_request)
        self.ui.lineEdit.editingFinished.connect(self.make_hwi_run_suggestions)
        self.ui.pushButton_2.clicked.connect(self.create_new_run)
        self.ui.radioButton.toggled.connect(self.set_menu_options)
        self.ui.radioButton_2.toggled.connect(self.set_menu_options)
        self.ui.listWidget.selectionModel().setCurrentIndex(self.ui.listWidget.model().index(0, 0), QItemSelectionModel.Select)
        # self.ui.comboBox.currentIndexChanged.connect(
        #     self.validate_hwi_number_images_run)


        # Widget display setup
        self.set_menu_options()
        logger.info('Opened run importer dialog')
        self.cannot_unrar_message()
        self.exec_()
        

    @property
    def current_menu_type(self):
        '''Return the current screen type selection. 'm' is returned when
        membrane screens have been selected by the user and 's' is returned
        when soluble screens have been selected.

        :return: screen type
        :rtype: str
        '''
        if self.ui.radioButton.isChecked():
            return 'm'
        else:
            return 's'

    @property
    def soluble_menus(self):
        '''Ask the bartender to return all soluble screen cocktail menus

        :return: list of Menu objects
        :rtype: list
        '''
        return tim.get_menus_by_type('s')
        # return tim.get_menus_by_type('s')  # returns menu objects

    @property
    def membrane_menus(self):
        '''Ask the bartender to return all membrane screen cocktail menus

        :return: list of Menu objects
        :rtype: list
        '''
        return tim.get_menus_by_type('m')

    @property
    def current_dateEdit(self):
        '''Get the current dateEdit widget based on the current index of
        the stackedWidget. `current...` methods are used to determine which
        stackWidget page to pull information from.

        :return: [description]
        :rtype: [type]
        '''
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
    
    def cannot_unrar_message(self):
        if not self.can_unrar:
            message = '''Polo was unable to find a working unrar program for
            your operating system. Polo will only be able to import images
            from uncompressed directories. For for information on installing
            unrar for Polo please visit this link LINK HERE'''
            msg = make_message_box(message, parent=self)
            self.ui.comboBox_6.clear()
            self.ui.comboBox_6.addItem('From Directory')  # only allow imports from dir
            msg.exec_()


    def get_menu_options(self):
        '''Returns a list of Menus that are available for the user to pick from
        based on their screen type selection.

        :return: list of Menu objects
        :rtype: list
        '''
        # set options depending on the radiobox selected
        if self.ui.radioButton.isChecked():  # membrane selected
            menus = self.membrane_menus
        else:
            menus = self.soluble_menus
        return sorted(menus, key=lambda menu: menu.start_date, reverse=True)

    def set_menu_options(self):
        '''Set the menu selection comboBox items to the available menu options
        '''
        options = self.get_menu_options()  # menu instances
        self.ui.comboBox_3.clear()
        self.ui.comboBox_3.addItems([menu.path for menu in options])

    def get_menu_index_by_path(self, menu_path):
        '''Retrieve the index of a combobox item representing a Menu object
        from the menu object's path

        :param menu_path: File path of a menu object
        :type menu_path: str
        :return: Index of the menu path in the combobox
        :rtype: int
        '''
        return self.ui.comboBox_3.findText(menu_path)

    def set_current_menu(self, menu):
        menu_index = self.get_menu_index_by_path(menu.path)
        if menu_index:
            return self.ui.comboBox_3.setCurrentIndex(menu_index)

    def set_hwi_image_type(self, image_type):
        '''Suggests an image spectrum for HWI imports based on the
        inferred image spectrum. 

        :param image_type: Image spectrum keyword
        :type image_type: str
        '''
        if image_type == 'uvt':
            self.ui.comboBox_2.setCurrentIndex(1)
        elif image_type == 'jpg':
            self.ui.comboBox_2.setCurrentIndex(0)
        elif image_type == 'shg':
            self.ui.comboBox_2.setCurrentIndex(2)
        else:
            self.ui.comboBox_2.setCurrentIndex(3)

    def suggest_menu_by_date(self, image_date, menu_type=None):
        '''Given a specific date, suggest what menu should be used. If the
        menu type is not given then assume the menu type should come from
        the current user selection.

        :param image_date: Date to search for menu by
        :type image_date: Datetime
        :param menu_type: Soluble of membrane menu, defaults to None
        :type menu_type: str, optional
        :return: Menu object that was used during the given date
        :rtype: Menu
        '''
        if not menu_type:
            menu_type = self.current_menu_type

        return tim.get_menu_by_date(image_date, menu_type)

    def make_hwi_run_suggestions(self):
        '''Wrapper method that can be used to call all methods involved in
        displaying suggested settings for HWI Run image imports.

        :return: True if image directory conforms to HWI naming conventions, False otherwise
        :rtype: Bool
        '''
        dir_path = self.ui.lineEdit.text()
        if os.path.exists(dir_path):
            dir_data = parse_hwi_dir_metadata(dir_path)
            if isinstance(dir_data, ValueError):
                make_message_box('Selected directory does not conform to HWI naming\
                    conventions. Could not make suggestions.').exec_()
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
        self.ui.textBrowser.setPlainText(import_descriptors[i])

    def open_run_browser(self):
        '''
        Opens a QFileDialog that only allows for selecting directories.
        Returns the path of the directory the user selects. Will be none
        is no directory is selected.
        '''
        if self.can_unrar and self.ui.comboBox_6.currentText() == 'From Rar':
            mode = QtWidgets.QFileDialog.ExistingFile
            f = 'Rar archives (*.rar)'
        else:
            mode = QtWidgets.QFileDialog.DirectoryOnly
            f = ''

        browser = QtWidgets.QFileDialog(self, filter=f)
        browser.setFileMode(mode)
        
        browser.exec_()
        f = browser.selectedFiles()

        if f and len(f) > 0 and f[0]:  # avoid index errors
            return f[0]
        else:
            return ''
        
    def crack_open_a_rar_one(self, rar_path):
        if not isinstance(rar_path, Path):
            rar_path = Path(rar_path)
        parent_path = rar_path.parent
        return unrar_archive(rar_path, parent_path)
        
    def validate_import(self, import_path=None):

        if not isinstance(import_path, Path):
            import_path = Path(import_path)
        
        if import_path.suffix == '.rar':
            import_thread = QuickThread(self.crack_open_a_rar_one, rar_path=import_path)
            message = 'Unpacking rar archive'
        else:
            import_thread = QuickThread(lambda: import_path)
            message = ''
        
        def thread_done():
            self.setEnabled(True)
            if message:
                message.close()
            QApplication.restoreOverrideCursor()
            r = import_thread.result
            if isinstance(r, Path):
                validator_result = directory_validator(str(r))
                if validator_result:
                    self.current_dir_path_lineEdit.setText(str(r))
                    if self.ui.stackedWidget.currentIndex() == 0:
                    # additional actions if loading in an HWI directory
                        self.make_hwi_run_suggestions()
                        self.validate_run_name(text=self.ui.lineEdit_2.text())
                else:
                    make_message_box('Failed to import with error {}'.format(
                        validator_result
                    ))
            else:
                make_message_box('Failed to read {} with error {}'.format(
                    import_path ,r 
                )).exec_()

        QApplication.setOverrideCursor(Qt.WaitCursor)
        import_thread.finished.connect(thread_done)
        import_thread.start()
        self.setEnabled(False)
        if message:
            message = make_message_box(message)
            message.exec_()

    def handle_browse_request(self):
        path = self.open_run_browser()
        if path:
            self.validate_import(path)
        

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
    
    
    def handle_rar_file(self, rar_path):
        # do stuff for rar file and then set the path to the uncompressed
        # dirctory 
        pass

    
    def show_rar_popup(self):
        pass
    # add method that pops up when unrar file is imported and asks how the
    # import should go down

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

        if current_index == 0:
            cocktail_menu = tim.get_menu_by_path(
                self.ui.comboBox_3.currentText())
            new_run = HWIRun(
                image_dir=dir_name,
                run_name=run_name,
                cocktail_menu=cocktail_menu,
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


