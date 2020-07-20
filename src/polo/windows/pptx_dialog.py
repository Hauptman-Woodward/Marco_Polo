
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
from polo.designer.UI_pptx_designer import Ui_PptxDialog
from polo.utils.io_utils import *
from polo.utils.dialog_utils import *
from polo import IMAGE_CLASSIFICATIONS
from polo.widgets.run_tree import RunTree


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

        boxes = [self.ui.checkBox, self.ui.checkBox_2,
                 self.ui.checkBox_3, self.ui.checkBox_4]
        for box, clss in zip(boxes, IMAGE_CLASSIFICATIONS):
            box.setText(clss)
        return dict(zip(IMAGE_CLASSIFICATIONS, boxes))

    def _validate_typed_path(self):
        path = self.ui.lineEdit_3.text()
        if RunSerializer.path_validator(parent=True):
            return True
        else:
            make_message_box(parent=self,
                             message='{} is not a valid path'.format(path)).exec_()
            self.ui.lineEdit_3.clear()

    @property
    def human(self):
        return self.ui.radioButton.isChecked()

    @property
    def marco(self):
        return self.ui.radioButton_2.isChecked()

    @property
    def title(self):
        return self.ui.lineEdit.text()

    @property
    def subtitle(self):
        return self.ui.lineEdit_2.text()
    
    @property
    def all_dates(self):
        return self.ui.checkBox_9.isChecked()
    
    @property
    def all_specs(self):
        return self.ui.checkBox_8.isChecked()

    def setup_run_tree(self):
        self.ui.runTreeWidget.auto_link = False
        for run_name, run in self.runs.items():
            self.ui.runTreeWidget.add_run_to_tree(run)

    def _browse_and_update_line_edit(self):
        file_path = self._get_save_path()
        if file_path:
            self.ui.lineEdit_3.setText(file_path)

    def set_default_titles(self):
        pass
    # need to access the currently selected item and determine if it is a
    # sample or not and act on that

    def _get_save_path(self):
        file_name = QtWidgets.QFileDialog.getSaveFileName(
            self, 'Presentation Path')
        if file_name and len(file_name) >= 1:
            return file_name[0]
        else:
            return ''

    def _parse_image_classifications(self):
        # return image classifications whose checkboxes are checked
        return set([clss for clss, box in self._image_class_checkboxes.items()
                                       if box.isChecked()])

    def _write_presentation(self, run=None):
        self.setEnabled(False)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        if not self.ui.lineEdit_3.text():
            file_path = _get_save_path
        else:
            file_path = self.ui.lineEdit_3.text()

        writer = PptxWriter(file_path,
                            image_types=self._parse_image_classifications(),
                            marco=self.marco, human=self.human)
        if not isinstance(run, (Run, HWIRun)):
            if self.ui.runTreeWidget.selected_run:
                run = self.ui.runTreeWidget.selected_run
            else:
                make_message_box('Please select a run').exec_()
                return

        write_result = writer.make_single_run_presentation(
            run=run,
            title=self.title,
            subtitle=self.subtitle,
            all_specs=self.all_specs,
            all_dates=self.all_dates
            )

        if write_result == True:
            message = 'Wrote presentation to {}'.format(file_path)
        else:
            message = 'Error writing presentation {}'.format(write_result)

        make_message_box(parent=self, message=message).exec_()
        self.setEnabled(True)
        QApplication.restoreOverrideCursor()
        return write_result

    def check_for_warnings(self):
        pass
