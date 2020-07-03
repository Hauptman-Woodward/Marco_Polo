import ftplib
import os
from pathlib import Path, PurePosixPath

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QAction, QApplication, QGridLayout

from polo import ICON_DICT, IMAGE_SPECS, SPEC_KEYS
from polo.utils.io_utils import RunDeserializer, RunLinker
from polo.crystallography.run import HWIRun, Run

class RunTree(QtWidgets.QTreeWidget):

    def __init__(self, parent=None, auto_link=True):
        print(type(parent))
        self.classified_runs = {}
        self.loaded_runs = {}
        self.auto_link = auto_link
        super(RunTree, self).__init__(parent)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

    @property
    def current_run_names(self):
        return list(self.loaded_runs.keys()) + list(self.classified_runs.keys())

    @property
    def all_runs(self):
        d = {}
        d.update(self.loaded_runs)
        d.update(self.classified_runs)

        return d

    def add_classified_run(self, run):
        if isinstance(run, str) and run in self.loaded_runs:
            self.classified_runs[run] = self.loaded_runs.pop(run)
        elif isinstance(run, (Run, HWIRun)) and run.run_name in self.loaded_runs:
            self.classified_runs[run.run_name] = self.loaded_runs.pop(
                run.run_name)

    def add_sample(self, sample_name, *args):
        parent_item = QtWidgets.QTreeWidgetItem(self)
        parent_item.setText(0, sample_name)
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
            self.link_in_new_run(run)
        return new_node

    def link_in_new_run(self, new_run):
        if self.auto_link and new_run.sampleName:
            sample_node = self.findItems(
                new_run.sampleName, Qt.MatchExactly, column=0)
            if sample_node:
                sample_node = sample_node.pop()
                all_runs = self.all_runs
                sample_runs = [all_runs[sample_node.child(i).text(0)] for i in range(
                    0, sample_node.childCount()) if sample_node.child(i).text(0) in all_runs]
                # LIST COMP AT ALL COSTS!
                linker = RunLinker(sample_runs)
                linked_runs = linker.the_big_link()

    def add_run_to_tree(self, new_run):
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