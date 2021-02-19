
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
from polo.designer.UI_pptx_designer import Ui_PptxDialog
from polo.utils.io_utils import *
from polo.utils.dialog_utils import *
from polo import IMAGE_CLASSIFICATIONS, DEFAULT_IMAGE_PATH, make_default_logger
from polo.widgets.run_tree import RunTree
from pathlib import Path

logger = make_default_logger(__name__)

class PptxDesignerDialog(QtWidgets.QDialog):

    def __init__(self, runs, parent=None):
        super(PptxDesignerDialog, self).__init__(parent)
        self.runs = runs
        self.ui = Ui_PptxDialog()
        self.ui.setupUi(self)
        self.setup_run_tree()
        self._image_class_checkboxes = self._set_up_image_classification_checkboxes()

        self.ui.lineEdit_3.editingFinished.connect(self._validate_typed_path)
        self.ui.pushButton_2.clicked.connect(self._write_presentation)
        self.ui.pushButton.clicked.connect(self._browse_and_update_line_edit)

    def _set_up_image_classification_checkboxes(self):
        '''Private method that sets up the labels for the image classifications
        :class:`QCheckBox` instances. Should be called in the `__init__` function before
        displaying the dialog to the user.

        :return: Dictionary of image classifications which map to the :class:`QCheckBox` 
                 that corresponds to that image classification
        :rtype: dict
        ''' 

        boxes = [self.ui.checkBox, self.ui.checkBox_2,
                 self.ui.checkBox_3, self.ui.checkBox_4]
        for box, clss in zip(boxes, IMAGE_CLASSIFICATIONS):
            box.setText(clss)
        return dict(zip(IMAGE_CLASSIFICATIONS, boxes))

    def _validate_typed_path(self):
        '''Private method that validates that a filepath in the filepath
        :class:`QLineEdit` widget is actually a valid path that a pptx file could be
        saved there.

        :return: True if the path is valid, otherwise returns None and shows
                 a message box to the user.
        :rtype: True or None
        ''' 
        path = self.ui.lineEdit_3.text()
        if RunSerializer().path_validator(path, parent=True):
            return True
        else:
            make_message_box(parent=self,
                             message='{} is not a valid path'.format(path)).exec_()
            self.ui.lineEdit_3.clear()

    @property
    def human(self):
        '''State of the human classifier :class:`QCheckBox`.

        :return: State of the :class:`QCheckBox`
        :rtype: bool
        '''
        return self.ui.radioButton.isChecked()

    @property
    def marco(self):
        '''State of the MARCO classifier :class:`QCheckBox`. 

        :return: State of the :class:`QCheckBox`
        :rtype: bool
        '''
        return self.ui.radioButton_2.isChecked()
    
    @property
    def favorite(self):
        '''State of the favorite button. Returns boolean based on check status.

        Returns:
            bool: State of the favorite button
        '''
        return self.ui.checkBox_5.isChecked()

    @property
    def title(self):
        '''Title the user has entered for the presentation via the title
        :class:`QLineEdit` widget. If no string has been entered will return the empty
        string.

        :return: The presentation title
        :rtype: str
        '''
        return self.ui.lineEdit.text()

    @property
    def subtitle(self):
        '''Subtitle the user has entered for the presentation via the subtitle
        :class:`QLineEdit` widget. If no string has been entered will return the empty
        string.

        :return: The presentation subtitle
        :rtype: str
        '''
        return self.ui.lineEdit_2.text()
    
    @property
    def all_dates(self):
        '''The state of the "Include all Dates" :class:`QCheckBox`. If it is checked this
        indicates that a time resolved slide should be included in the
        presentation.

        :return: State of the :class:`QCheckBox`
        :rtype: bool
        '''
        return self.ui.checkBox_9.isChecked()
    
    @property
    def all_specs(self):
        '''The state of the "Include all Spectrums" :class:`QCheckBox`. If it is checked this
        indicates that a multi-spectrum slide should be included in the
        presentation.

        :return: State of the :class:`QCheckBox`
        :rtype: bool
        '''
        return self.ui.checkBox_8.isChecked()

    def setup_run_tree(self):
        self.ui.runTreeWidget.auto_link = False
        for run_name, run in self.runs.items():
            self.ui.runTreeWidget.add_run_to_tree(run)

    def _browse_and_update_line_edit(self):
        '''Private method that calls 
        :meth:`~polo.windows.pptx_dialog.PptxDialog._get_save_path`
        to open a file browser. If the user selects a save path using the file
        browser then displays this path in the filepath :class:`QLineEdit` widget.
        '''
        file_path = self._get_save_path()
        if file_path:
            self.ui.lineEdit_3.setText(file_path)

    def set_default_titles(self):
        pass
    # need to access the currently selected item and determine if it is a
    # sample or not and act on that

    def _get_save_path(self):
        '''Private method that opens a file browser and returns the selected
        save filepath.

        :return: Filepath if one is specified by the user, empty string otherwise
        :rtype: str
        '''
        file_name = QtWidgets.QFileDialog.getSaveFileName(
            self, 'Presentation Path')
        if file_name and len(file_name) >= 1:
            return file_name[0]
        else:
            return ''

    def _parse_image_classifications(self):
        '''Private method to get all currently selected image classifications
        by reading the state of all image classification 
        :class:`QCheckBox` instances. 

        :return: Set of all selected image classifications
        :rtype: set
        '''
        # return image classifications whose checkboxes are checked
        return set([clss for clss, box in self._image_class_checkboxes.items()
                                       if box.isChecked()])
    
    def _parse_manual_image_entry(self, num_wells):
        '''Private method to return the image (well) numbers if they have been
        manually specified by the user.
        '''
        text = self.ui.plainTextEdit.toPlainText()
        if text:  # only parse if user has entered text
            text = text.split(',')
            for i, _ in enumerate(text):
                text[i] = text[i].strip().replace(',', '')  # strip and remove extra commas
                try:
                    text[i] = int(text[i]) - 1  # convert to base 0
                    assert num_wells > text[i] and text[i] >= 0
                except Exception as e:
                    if isinstance(e, AssertionError):
                        message = 'Make sure not to enter well numbers greater than the total number of wells in the run ({})'.format(num_wells)
                    else:
                        message = 'Could not parse text entered. Please make sure to separate well numbers using commas and do not enter non-well-number values.'
                    make_message_box(message).exec_()
                    return e
        return text
    
    def _get_images_from_manual_entry(self, run):
        indices = self._parse_manual_image_entry(len(run.images))
        if isinstance(indices, Exception):
            return indices 
        if indices:
            return [run.images[i] for i in indices]
    
    def _get_images_from_auto_entry(self, run):
        return run.image_filter_query(
            self._parse_image_classifications(),
            self.human,
            self.marco,
            self.favorite
        )
        
    
    def _write_presentation(self, run=None):
        '''Private method that actually does the work of generating a
        presentation from a :class:`Run` or :class:`HWIRun` instance.

        :param run: Run to create a presentation from, defaults to None
        :type run: Run or HWIRun, optional
        :return: Path to the pptx presentation is write is successful, 
                 Exception otherwise.
        :rtype: str or Exception
        ''' 
        try:
            if not issubclass(type(run), Run):
                if self.ui.runTreeWidget.selected_run:
                    run = self.ui.runTreeWidget.selected_run
                else:
                    make_message_box('Please select a run').exec_()
                    QApplication.restoreOverrideCursor()
                    return

            # user has not entered an export path
            if not self.ui.lineEdit_3.text():
                make_message_box(
                    'Please set a path to export presentation to.').exec_()
                QApplication.restoreOverrideCursor()
                return
            else:
                file_path = str(Path(self.ui.lineEdit_3.text()))
            
            images = self._get_images_from_manual_entry(run)

            if isinstance(images, Exception):  # user attempted to enter manual
                # exception indicates user did something incorrectly or we
                # just failed to parse. None type would indicate user did
                # not use manual entry
                make_message_box(
                    'Could not read manual values, using auto.').exec_()
                images = self._get_images_from_auto_entry(run)
            
            if not images:
                images = self._get_images_from_auto_entry(run)
                
            if len(images) == 1 and images[0].path != DEFAULT_IMAGE_PATH or not images:  
                # check to make sure not empty image default
                make_message_box(
                    'No images in this run fit your selection criteria.').exec_()
                QApplication.restoreOverrideCursor()
                return
            
            writer = PptxWriter(file_path)

            self.setEnabled(False)  # disable dialog while writing
            QApplication.setOverrideCursor(Qt.WaitCursor)

            write_result = writer.make_presentation(
                run=run,
                images=images,
                title=self.title,
                subtitle=self.subtitle,
                all_specs=self.all_specs,
                all_dates=self.all_dates,
            )

            if write_result == True:
                message = 'Wrote presentation to {}'.format(file_path)
            else:
                message = 'Error writing presentation {}'.format(write_result)

            self.setEnabled(True)
            QApplication.restoreOverrideCursor()
            make_message_box(parent=self, message=message).exec_()
            return write_result
        except Exception as e:
            logger.error('Caught {} at {}'.format(e, self._write_presentation))
            make_message_box(
                parent=self,
                message='Failed to write presentation {}'.format(e)
            ).exec_()


    def check_for_warnings(self):
        pass
