
from PyQt5 import QtWidgets
from polo.designer.UI_pptx_designer import Ui_Dialog
from polo.utils.io_utils import *


class PptxDesignerDialog(QtWidgets.QDialog):


    def __init__(self, runs, parent=None):
        super(PptxDesignerDialog, self).__init__(parent)
        self.runs = runs
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setup_run_tree()
        self.image_type_checkboxes = [

        ]

    @property
    def image_types(self):
        pass

    def setup_run_tree(self):
        self.ui.runTreeWidget.auto_link = False
        for run_name, run in self.runs.items():
            self.ui.runTreeWidget.add_run_to_tree(run)
    

    def set_default_titles(self):
        pass
    # need to access the currently selected item and determine if it is a
    # sample or not and act on that

    def get_save_path(self):
        file_name = QtWidgets.QFileDialog.getSaveFileName(self, 'Presentation Path')
        if file_name: return file_name.pop(0)
    
    # need to verify the parent directory

    def write_presentation(self):
        pass

    def check_for_warnings(self):
        pass
    # warning that writing presentation may take a long time

    


    

    
        
    


