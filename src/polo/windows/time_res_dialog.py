from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QBrush, QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QGridLayout

from polo.crystallography.run import HWIRun
from polo.designer.UI_time_resolved_dialog import Ui_Dialog

# TODO: Downloading function and reflect files in the actual FTP server
# Probably want to look into threads for downloading so not being done on
# the GUI thread

class TimeResDialog(QtWidgets.QDialog):

    def __init__(self, available_runs):
        QtWidgets.QDialog.__init__(self)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.available_runs = available_runs
        self.ui.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.ui.pushButton.clicked.connect(self.auto_detect_time_links)
        self.ui.pushButton_2.clicked.connect(self.close)
        
        self.display_runs()

        self.exec_()
    
    def get_HWI_runs(self):
        return [run for run in self.available_runs if type(self.available_runs[run]) == HWIRun]
    
    
    def display_runs(self):
        # filter by HWI type runs as of now
        if self.available_runs:
            self.ui.listWidget.addItems(self.get_HWI_runs())
        
    def auto_detect_time_links(self):
        selected_runs = [i.text() for i in self.ui.listWidget.selectedItems()]
        temp_runs = []
        for selected_run in selected_runs:
            temp_runs.append(self.available_runs[selected_run])
    
        temp_runs = sorted(temp_runs, key=lambda x: x.images[0].date)
        # sorted from earliest to latest
        for i in range(0, len(temp_runs)-1):
            temp_runs[i].link_to_next_date(temp_runs[i+1])
        
        
        for run in temp_runs:
            if run.run_name in self.available_runs:

                self.available_runs[run.run_name] = run

        self.close()
    
    def validate_user_selection(self):
        pass
    # when user attempts to link images sets manually
    # give warning if links do not cofirm to what would
    # have been generated from auto setting
    
    def sort_available_runs_by_date(self):
        pass 
