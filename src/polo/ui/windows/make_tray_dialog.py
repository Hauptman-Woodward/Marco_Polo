from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QBrush, QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QGridLayout
from UI.designer.Ui_make_tray import Ui_Dialog
from Utils.ftp_utils import logon, list_dir

import os


# TODO: Downloading function and reflect files in the actual FTP server
# Probably want to look into threads for downloading so not being done on
# the GUI thread

class makeTrayDialog(QtWidgets.QDialog):

    def __init__(self, hits):
        QtWidgets.QDialog.__init__(self)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.hits = hits  # images human classed as crystal
        self.selected_hit = None


        self.ui.listWidget.itemClicked.connect(self.update_selected_hit)

        self.exec_()
    
    def open_file_dialog(self):  # open dialog to write file
        file_dlg = QtWidgets.QFileDialog()
        filename = ''
        if file_dlg.exec():
            filename = file_dlg.selectedFiles()
            return filename[0]
        else:
            return False
    
    def write_csv(self, output_path):
        pass
    # write current screen as csv file
    
    def write_pdf(self, output_path):
        pass
    # write as pdf
        
    
    def update_selected_hit(self, q):
        
        self.selected_hit = self.hits[q.text()]
    
    def render_cocktail_details(self):
        pass
        # do this through adding a str method to cocktail
    
    def make_hit_dict(self, hits):
        return {os.path.basename(image.path): image for image in hits}
        
    
    def make_tray_from_hit(self):
        cocktail = self.selected_hit.cocktail
        x_var = self.ui.comboBox.currentText()
        y_var = self.ui.comboBox_2.currentText()
        
        x_var_base, x_units = cocktail[x_var]  # need to implement
        y_var_base, y_units = cocktail[x_var]  # also need implement
        
        # now need to convert the units
        # need a dictionary of molar masses to use for lookup to convert to
        # molarity
    
    def populate_dropdowns(self):
        cocktail = self.selected_hit.cocktail
        solutions = [solution.chemical_additive for solution in cocktail.solutions] + ['pH']
        self.ui.comboBox.addItems(solutions)
        self.ui.comboBox_2.addItems(solutions)
        
    
    