import ftplib
import os
from pathlib import Path, PurePosixPath

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QAction, QApplication, QGridLayout
from polo.utils.dialog_utils import make_message_box
from polo import ICON_DICT, IMAGE_SPECS, SPEC_KEYS
from polo.utils.io_utils import RunDeserializer, RunLinker, MsoReader
from polo.crystallography.run import HWIRun, Run
from polo.windows.run_updater_dialog import RunUpdaterDialog

class RunTree(QtWidgets.QTreeWidget):

    opening_run = pyqtSignal()
    save_run_signal = pyqtSignal()
    remove_run_signal = pyqtSignal(list)

    def __init__(self, parent=None, auto_link=True):
        self.classified_status = {}
        self.loaded_runs = {}
        self.samples = []
        self.auto_link = auto_link
        super(RunTree, self).__init__(parent)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
    
    @property
    def current_run_names(self):
        return list(self.loaded_runs.keys())
    
    @property
    def selected_run(self):
        if self.currentItem() and self.currentItem().text(0) in self.loaded_runs:
            return self.loaded_runs[self.currentItem().text(0)]
        else:
            return False

    def remove_run_from_view(self, run_name):
        # remove the current selected run if one is selected
        # only removes it from the view does not do any backend removal
        condemned_run = self.loaded_runs[run_name]
        condemned_run_parent = self.findItems(condemned_run.sampleName, Qt.MatchExactly, column=0)
        if condemned_run_parent:
            condemned_run_parent = condemned_run_parent.pop()
            # got through all children of parent
            for i in range(condemned_run_parent.childCount()):
                if condemned_run_parent.child(i).text(0) == run_name:
                    condemned_run_parent.removeChild(condemned_run_parent.child(i))
                    break
            # check if any remaining children
            if condemned_run_parent.childCount() == 0:
                self.invisibleRootItem().removeChild(condemned_run_parent)
            
            return condemned_run
    
    def add_classified_run(self, run):
        if isinstance(run, str) and run in self.loaded_runs:
            self.classified_status[run] = True
            
    def add_sample(self, sample_name, *args):
        parent_item = QtWidgets.QTreeWidgetItem(self)
        parent_item.setText(0, sample_name)
        self.samples.append(sample_name)
        for run in args:
            if isinstance(run, (Run, HWIRun)):
                self.add_run_node(run, parent_item)

    def add_run_node(self, run, tree=None):
        if not tree:
            tree = self
        new_node = QtWidgets.QTreeWidgetItem(tree)
        new_node.setText(0, run.run_name)
        new_node.setToolTip(0, run.get_tooltip())
        if run.run_name in self.loaded_runs:
            self.handle_dup_run_import()
        else:
            self.loaded_runs[run.run_name] = run
        return new_node
    
    def link_sample(self, sample_name):
        # gather runs with this sample
        runs_in_sample = [run for run_name, run in self.loaded_runs.items()
                        if run.sampleName == sample_name]
        linked_runs = RunLinker.the_big_link(runs_in_sample)
        linked_runs_dict = {run.run_name: run for run in linked_runs}
        self.loaded_runs.update(linked_runs_dict)


    def add_run_to_tree(self, new_run):
        if new_run.run_name not in self.loaded_runs:
            if isinstance(new_run, HWIRun):
                if hasattr(new_run, 'sampleName'):
                    sample_node = self.findItems(
                        new_run.sampleName, Qt.MatchExactly, column=0)
                    if sample_node:
                        sample_node = sample_node.pop()  # returned as a list
                        self.add_run_node(new_run, sample_node)
                    else:
                        self.add_sample(new_run.sampleName, new_run)
                else:
                    orphan_runs = self.findItems(
                        'Sampleless Runs', Qt.MatchExactly, column=0)
                    if orphan_runs:
                        orphan_runs = orphan_runs.pop()
                    else:
                        orphan_runs = QtWidgets.QTreeWidgetItem(self)
                        orphan_runs.setText(0, 'Sampleless Runs')
                    new_run.sampleName = 'Sampleless Runs'
                    self.add_run_node(new_run, orphan_runs)

            elif isinstance(new_run, Run):
                non_hwi_runs = self.findItems(
                    'Non-HWI Runs', Qt.MatchExactly, column=0)
                if non_hwi_runs:
                    non_hwi_runs = non_hwi_runs.pop()
                else:
                    non_hwi_runs = QtWidgets.QTreeWidgetItem(self)
                    non_hwi_runs.setText(0, 'Non-HWI Runs')
                    new_run.sampleName = 'Non-HWI Runs'
                self.add_run_node(new_run, non_hwi_runs)
    
    def _remove_run(self, run_name):
        # get all runs in the sample and just relink everything together
        run = self.remove_run_from_view(run_name)
        if run_name in self.loaded_runs: self.loaded_runs.pop(run_name)
        if run_name in self.classified_status: self.classified_status.pop(run_name)

        self.link_sample(run.sampleName)

        for run in self.loaded_runs:
            if (self.loaded_runs[run].alt_spectrum
                and self.loaded_runs[run].alt_spectrum.run_name == run_name
                ):
                self.loaded_runs[run].alt_spectrum = None
        self.remove_run_signal.emit([run])
        # BUG: run unlinking not working for non visible images
        # the images within a run are unlinked but not the actual run objects
        # the above is a temp fix
    
    def contextMenuEvent(self, event):
        if self.currentItem() and self.currentItem().text(0) in self.loaded_runs:
            self.menu = QtWidgets.QMenu(self)

            # edit_data_action = QtWidgets.QAction('Edit Run Data', self)
            # edit_data_action.triggered.connect(lambda: self._edit_data_slot(event))

            remove_run_action = QtWidgets.QAction('Remove Run', self)
            remove_run_action.triggered.connect(lambda: self._remove_run_slot(event))

            open_run_action = QtWidgets.QAction('Open Run', self)
            open_run_action.triggered.connect(lambda: self._open_run_slot(event))

            classify_from_mso = QtWidgets.QAction('Add MSO classifications', self)
            classify_from_mso.triggered.connect(lambda: self._add_classifications_from_mso_slot(event))


            self.menu.addAction(open_run_action)
            #self.menu.addAction(edit_data_action)
            self.menu.addAction(remove_run_action)
            self.menu.addSeparator()
            self.menu.addAction(classify_from_mso)
            

            self.menu.popup(QtGui.QCursor.pos())
    
    def _open_run_slot(self, event=None):
        self.opening_run.emit()
    
    def _edit_data_slot(self, event=None):
        current_selection = self.currentItem()
        if current_selection:
            run_name = current_selection.text(0)
            run = self.loaded_runs[run_name]
            updater = RunUpdaterDialog(run=run, run_names=self.current_run_names)
            updater.exec_()
            # if updater.run.run_name != run_name:
            #     # need to change the run name in the viewer
            #     print(type(run))
            #     run_node = self._get_run_node(run)
            #     if run_node:
            #         run_node.setText(0, updater.run.run_name)
            self.loaded_runs[run_name] = updater.run
    
    def _add_classifications_from_mso_slot(self, event=None):
        if self.selected_run:
            mso_browser = QtWidgets.QFileDialog.getOpenFileName(
                self, 'MSO Hunter', filter='mso files (*.mso)')
            if mso_browser and len(mso_browser) > 0:
                mso_file = mso_browser[0]
                reader = MsoReader(mso_file)
                result = reader.classify_images_from_mso_file(
                    self.selected_run.images)
                if result == True:
                    message = 'Added MSO classifications from {}'.fromat(
                        mso_file
                    )
                else:
                    message = 'Failed to add MSO classifications from {}. Failed with error {}'.format(
                        mso_file, result
                    )
                make_message_box(parent=self, message=message).exec_()
    
    def _get_run_node(self, run):
        run_name = run.run_name
        sample_name = run.sampleName
        parent_node = self.findItems(
                            run.sampleName, Qt.MatchExactly, column=0).pop(0)
        
        for i in range(parent_node.childCount()):
            child_node = parent_node.child(i)
            if child_node.text(0) == run_name:
                return child_node

    # open edit run data dialog window

    def _remove_run_slot(self, event=None):
        current_selection = self.currentItem()
        if current_selection:
            run_name = current_selection.text(0)
            self._remove_run(run_name)

    
        

        

        