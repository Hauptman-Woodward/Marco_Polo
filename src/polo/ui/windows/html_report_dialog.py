import os

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QBrush, QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QGridLayout

from polo.ui.designer.Ui_HTMLReportDialog import Ui_HTMLReportDialog
from polo.utils.ftp_utils import list_dir, logon
from polo.utils.io_utils import make_dict_from_run_via_json

# TODO: Downloading function and reflect files in the actual FTP server
# Probably want to look into threads for downloading so not being done on
# the GUI thread

class htmlReportDialog(QtWidgets.QDialog):

#TODO: work the html generation into this dialog from IOUtils
# also need to add attributes to run to allow for storing run annotations
# and need a way to get the current date easily for run

    def __init__(self, run):
        QtWidgets.QDialog.__init__(self)
        self.ui = Ui_HTMLReportDialog()
        self.ui.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.run = run
        self.ui.pushButton.clicked.connect(self.close)
        self.ui.pushButton_2.clicked.connect(self.generate_report)

        self.exec_()
    
    def generate_report(self):
        images = make_dict_from_run_via_json(self.run)['images']
        output_path = QtWidgets.QFileDialog.getSaveFileName()
        if output_path:
            if '.html' not in os.path.basename(output_path).lower():
                output_path += '.html'
                if self.ui.radioButton.isChecked():
                    sort_by = 'human_class'
                elif self.ui.radioButton_2.isChecked():
                    sort_by = 'machine_class'
                elif self.ui.radioButton_3.isChecked():
                    sort_by = 'well_number'
                elif self.ui.radioButton_4.isChecked():
                    sort_by = 'cocktail_number'
            
    def sort_image_dict_by_class(self, image_list, classifier='human_class'):
        # converts json generated list of image dicts to a list that
        # is sorted by the classifiction. Set the classifier using the
        # classifier variable. Should be an attribute of image that contains
        # a classification
        image_bins = {}
        for image in image_list:
            c = str(image[classifier])
            if c not in image_bins:
                image_bins[c] = [image]
            else:
                image_bins[c].append(image)
        
        return [image_bins[b] for b in sorted(image_bins)]

    def sort_image_dict_by_well_number(self, image_list):
        # validation to make sure will have well number needed before
        # this call
        return sorted(image_list, key=lambda x: int(x['well_number']))

    def sort_image_dict_by_cocktail_number(self, image_list):
        # validation for cocktail numbers needed before call
        pass
        
    
    def parse_inclusion_options(self):
        inclusion_list = []
        if self.ui.checkBox_6.isChecked():
            inclusion_list.append('plate_annotations')
        if self.ui.checkBox_7.isChecked():
            inclusion_list.append('image_annotations')
        if self.ui.checkBox_5.isChecked():
            inclusion_list.append('plate_summary_stats')
        if self.ui.checkBox_4.isChecked():
            inclusion_list.append('plate_heatmaps')
        
        return inclusion_list

    def parse_sort_options(self):
        sort_by = ''
        if self.ui.radioButton.isChecked():
            sort_by = 'human_class'
        elif self.ui.radioButton_2.isChecked():
            sort_by = 'machine_class'
        elif self.ui.radioButton_3.isChecked():
            sort_by = 'well_number'
        elif self.ui.radioButton_4.isChecked():
            sort_by = 'cocktail_number'
        
        return sort_by
