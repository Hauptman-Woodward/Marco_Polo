from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QBrush, QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QGridLayout
import os
from polo import ICON_DICT
import ftplib
from pathlib import PurePosixPath
from PyQt5.QtWidgets import QApplication

from polo.crystallography.run import Run, HWIRun
from polo.utils.io_utils import RunLinker
from polo.utils.dialog_utils import make_message_box
from polo.windows.ftp_dialog import FTPDialog


class RunOrganizer(QtWidgets.QTreeWidget):

    def __init__(self, parent=None, loaded_runs={},
                classified_runs={}, auto_link_runs=True):

        super(RunOrganizer, self).__init__(parent)
        self.auto_link_runs = auto_link_runs  # allow for turn off in settings
        self.loaded_runs = loaded_runs
        self.current_run = None
        self.added_runs_counter = 0
        self.itemDoubleClicked.connect(self.handle_opening_run)
    

    def handle_opening_run(item, self):

        # get currently selected item see if in classified runs and then
        # decide what to do from here


        run_name = item.text(0)
        self.current_run = self.loaded_runs[run_name]
        if self.current_run in classified_runs:
            return self.current_run
        else:
            # do some classification here
            pass
        # need a method in main window that if it gets back a run from this
        # call then sets everything up with that run 
        

    def handle_dup_run_import(self):
        pass
    

    # how could connect ftp download directly into add from run
    # in some way

    def import_from_ftp(self):
        ftp_browser = FTPDialog()
        if ftp_browser.ftp and ftp_browser.download_files and ftp_browser.save_dir:
            self.ftp_download_thread = FTPDownloadThread(
                dialog.ftp, dialog.download_files, dialog.save_dir
            )
    
    def finished_ftp_download(self):
        pass
        

            # might make sense to create a run importer class
            # that is seperate from the dialog so can be used here as well





    
    def import_saved_run(self):
        pass
    # should add it directly to the classified runs
    # possible add some option that would allow for reclassifiction of runs

    def import_new_run(self):
        pass
    
    
    def add_sample(self, sample_name, *args):
        parent_item = QtWidgets.QTreeWidgetItem(self)
        parent_item.setText(0, sample_name)
        for run in args:
            if isinstance(run, (Run, HWIRun)):
                self.add_run_node(run, parent_item)
    
    def add_run_node(self, run, tree=None):
        if not tree: tree = self
        new_node = QtWidgets.QTreeWidgetItem(tree)
        new_node.setText(0, run.run_name)
        new_node.setToolTip(0, run.get_tooltip())
        self.added_runs_counter += 1  # could be used to insure unique
        if run.run_name in self.loaded_runs:
            self.handle_dup_run_import()
        else:
            self.loaded_runs[run.run_name] = run
        return new_node
    
    def link_to_sample(self, new_run):
        sample_node = self.findItems(new_run.sampleName, Qt.MatchExactly, column=0)
        if sample_node:
            sample_node = sample_node.pop()

        # probalby would make more sense to move loaded runs here
        # instead of haveing in the main window
    
    def classify_all_loaded_runs(self):
        pass

    def classify_run(self):
        pass


    def add_run_to_tree(self, new_run):
        if isinstance(new_run, HWIRun):
            if hasattr(new_run, 'sampleName'):
                sample_node = self.findItems(new_run.sampleName, Qt.MatchExactly, column=0)
                if sample_node:
                    sample_node = sample_node.pop()  # returned as a list
                    self.add_run_node(sample_node, new_run)
                else:
                    self.add_sample(new_run.sampleName, new_run)
            else:
                orphan_runs = self.findItems('Sampleless Runs', Qt.MatchExactly, column=0)
                if orphan_runs:
                    orphan_runs = orphan_runs.pop()
                else:
                    orphan_runs = QtWidgets.QTreeWidgetItem(self)
                    orphan_runs.setText(0, 'Sampleless Runs')
                new_run.sampleName = 'Sampleless Runs'
                self.add_run_node(orphan_runs, new_run)

        elif isinstance(new_run, Run):
            non_hwi_runs = self.findItems('Non-HWI Runs', Qt.MatchExactly, column=0)
            if non_hwi_runs:
                    non_hwi_runs = non_hwi_runs.pop()
            else:
                non_hwi_runs = QtWidgets.QTreeWidgetItem(self)
                non_hwi_runs.setText(0, 'Non-HWI Runs')
                new_run.sampleName = 'Non-HWI Runs'
            self.add_run_node(non_hwi_runs, new_run)


    def remove_sample(self, sample_name):
        pass

    def remove_run(self, smaple_name, run_name):
        pass