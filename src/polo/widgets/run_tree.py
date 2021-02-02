import ftplib
import os
from pathlib import Path, PurePosixPath
from datetime import datetime

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QAction, QApplication, QGridLayout
from polo.utils.dialog_utils import make_message_box
from polo import ICON_DICT, IMAGE_SPECS, SPEC_KEYS
from polo.utils.io_utils import RunDeserializer, RunLinker, MsoReader, make_default_logger
from polo.crystallography.run import HWIRun, Run
from polo.threads.thread import ClassificationThread
from polo.windows.run_updater_dialog import RunUpdaterDialog

logger = make_default_logger(__name__)


class RunTreeItem(QtWidgets.QTreeWidgetItem):


    def __init__(self, date, parent):
        self.date = date  # datetime
        super(RunTreeItem, self).__init__(parent)
    
    def __cmp__(self, other):
        if isinstance(self.date, datetime):
            if self.date < other.date:
                return -1
            elif self.date == other.date:
                return 0
            else:
                return 1
        else:
            return -1  # just assume less than
    

class RunTree(QtWidgets.QTreeWidget):
    '''Inherits the :class:`QTreeWidget` class and acts as the sample and
    run display. The User uses the RunTree to open and classify runs
    they load into Polo.

    :param parent: Parent widget, defaults to None
    :type parent: QWidget, optional
    :param auto_link: If True automatically link runs together, defaults to True
    :type auto_link: bool, optional
    '''

    opening_run = pyqtSignal()
    save_run_signal = pyqtSignal()
    remove_run_signal = pyqtSignal(list)
    dropped_links_signal = pyqtSignal(list)
    classify_sample_signal = pyqtSignal(list)

    def __init__(self, parent=None, auto_link=True):
        self.classified_status = {}
        self.loaded_runs = {}
        self.formated_name_to_name = {}
        self.samples = []
        self.auto_link = auto_link
        super(RunTree, self).__init__(parent)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setAcceptDrops(True)
        self.setSortingEnabled(True)
        logger.debug('Created {}'.format(self))

    @property
    def current_run_names(self):
        '''List of all currently loaded :class:`Run` names.

        :return: List of :class:Run` names
        :rtype: list
        '''
        return list(self.loaded_runs.keys())
    
    @property
    def selected_run(self):
        '''The: class:`Run` that is currently selected. If no :class:`Run` is
        selected returns False.

        :return: The currently selected run, if one exists, otherwise returns False
        :rtype: Run, HWIRun or False
        '''
        if self.currentItem() and self.currentItem().text(0) in self.formated_name_to_name:
            return self.loaded_runs[self.formated_name_to_name[self.currentItem().text(0)]]
        else:
            return False

    def _open_run_slot(self, event=None):
        '''Private method that emits the :attr:`opening_run` signal when called. This
        signal can be connected to other widgets to communicate that the user
        has selected a run and wants to open it for analysis.   

        :param event: QEvent, defaults to None
        :type event: QEvent, optional
        '''
        self.opening_run.emit()

    def _edit_data_slot(self, event=None):
        '''Private method used to update the data in a :class:`Run` after it has
        been modified by the user through the :class:`RunUpdater` dialog.

        :param event: QEvent, defaults to None
        :type event: QEvent, optional
        '''
        current_selection = self.selected_run
        if current_selection:
            updater = RunUpdaterDialog(
                run=current_selection, run_names=self.current_run_names)
            updater.exec_()
            # if updater.run.run_name != run_name:
            #     # need to change the run name in the viewer
            #     print(type(run))
            #     run_node = self._get_run_node(run)
            #     if run_node:
            #         run_node.setText(0, updater.run.run_name)
            self.loaded_runs[run_name] = updater.run
    
    def _display_name_setter(self, run):
        '''Private method that creates a display name for a run that also
        avoids collisions with existing display names. Currently the process
        of translating a display name to a :class:`Run` object involves first
        looking up the display name in the :attr:`formated_name_to_name`
        dictionary to get the run name and then looking up the run name in the
        :attr:`loaded_runs` dictionary to get the :class:`Run` object. This
        means that currently run names and display names need to be unique
        to avoid collisions.

        :param run: Run to create a display name for
        :type run: Run or HWIRun
        '''
        if run.formated_name in self.formated_name_to_name:  # collision
            def avoid_collision(formated_name, i):
                incremented_name = '{}-{}'.format(formated_name, i)
                if incremented_name in self.formated_name_to_name:
                    avoid_collision(formated_name, i+1)
                else:
                    return incremented_name
            return avoid_collision(run.formated_name, 0)
        else:
            return run.formated_name

    def _add_run_node(self, run, tree=None):
        '''Private method that adds a new run node.

        :param run: Run to add to the tree
        :type run: Run or HWIRun
        :param tree: `QTreeWidgetItem` to act as parent node, defaults to None.
                     If None uses the root as the parent node.
        :type tree: QTreeWidgetItem, optional
        :return: Node added to the tree
        :rtype: QTreeWidgetItem
        '''
        if not tree:
            tree = self

        if run.run_name in self.loaded_runs:
            # already got one mate
            return
        else:
            new_node = RunTreeItem(run.date, tree)
            formated_name = self._display_name_setter(run)
            new_node.setText(0, formated_name)
            new_node.setToolTip(0, run.get_tooltip())
        
            self.loaded_runs[run.run_name] = run
            self.formated_name_to_name[formated_name] = run.run_name
            logger.debug('Added new run: {}'.format(run))
            return new_node

    def _get_run_node(self, run):
        '''Private helper method that returns the :class:`QTreeWidgetItem`
        corresponding to a given :class:`Run`. Returns None if a node cannot be found.

        :param run: Run to search for
        :type run: Run or HWIRun
        :return: Given run's corresponding :class:`QTreeWidgetItem` if it exists
        :rtype: QTreeWidgetItem
        '''
        run_name = run.run_name
        # sample_name = run.sampleName
        parent_node = self.findItems(
            run.sampleName, Qt.MatchExactly, column=0).pop(0)

        for i in range(parent_node.childCount()):
            child_node = parent_node.child(i)
            if child_node.text(0) == run_name:
                return child_node

    def _add_classifications_from_mso_slot(self, event=None):
        '''Add classifications to an existing :class:`Run` from the contents of an
        MSO file. Intended to be connected to the `classify_from_mso`
        QAction that is defined in the :
        :meth:`~polo.widgets.run_tree.RunTree.contextMenuEvent`
        method.

        :param event: QEvent, defaults to None
        :type event: QEvent, optional
        '''
        if self.selected_run:
            mso_browser = QtWidgets.QFileDialog.getOpenFileName(
                self, 'MSO Hunter', filter='mso files (*.mso)')
            if mso_browser and len(mso_browser) > 0:
                mso_file = mso_browser[0]
                reader = MsoReader(mso_file)
                result = reader.classify_images_from_mso_file(
                    self.selected_run.images)
                if isinstance(result, list):
                    self.selected_run.images = result
                    message = 'Added MSO classifications from {}'.format(
                        mso_file
                    )
                else:
                    message = 'Failed to add MSO classifications from {}. Failed with error {}'.format(
                        mso_file, result
                    )
                make_message_box(parent=self, message=message).exec_()

    def _remove_run_slot(self, event=None):
        '''Slot to connect to contextMenu popup to remove the selected run.
        '''
        if self.currentItem():
            display_name = self.currentItem().text(0)
            self.remove_run(display_name)

    def remove_run(self, display_name):
        '''Private method to remove a :class:`Run` completely from the
         Polo interface.

        :param display_name: Display name being shown to the user to represent
                            the run to be removed.
        :type run_name: str
        '''
        try:
            condemned_run = self.loaded_runs[self.formated_name_to_name[display_name]]
            self.remove_run_from_view(display_name, condemned_run.sampleName)
            self.formated_name_to_name.pop(display_name)  # remove display name
            self.loaded_runs.pop(condemned_run.run_name)  # remove from loaded runs
            self.link_sample(condemned_run.sampleName)
            # relink all the runs in the sample

            # remove links to condemned run if an alt spectrum 
            for run in self.loaded_runs:
                if (self.loaded_runs[run].alt_spectrum
                    and self.loaded_runs[run].alt_spectrum.run_name == condemned_run.run_name
                    ):
                    self.loaded_runs[run].alt_spectrum = None
            self.remove_run_signal.emit([None])
            logger.debug('Removed run {}'.format(condemned_run))
        except Exception as e:
            logger.error('Caught {} at {}'.format(e, self.remove_run))
            make_message_box(parent=self,
            message='Could not remove run {}'.format(e)
            ).exec_()
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
            paths = []
            for url in event.mimeData().urls():
                paths.append(Path(str(url.toLocalFile())))
            self.dropped_links_signal.emit(paths)
            logger.info('Dropped {} file paths'.format(len(paths)))
        else:
            event.ignore()
                
    def remove_run_from_view(self, display_name, sample_name):
        '''Remove a :class:`Run` instance using its :attr:`run_name` attribute.
        Does not effect any other widgets. Calling this method only 
        removes the :class:`Run` instance from
        the display. If a :class:`Run` instance is removed from successfully
        it is returned.

        TODO UPDATE

        :param run_name: Name of run to remove
        :type run_name: str
        :return: Removed run
        :rtype: Run or HWIRun
        '''
        parent_node = self.findItems(sample_name, Qt.MatchExactly, column=0)
        if parent_node:
            parent_node = parent_node.pop()
            for i in range(parent_node.childCount()):  # find run node
                if parent_node.child(i) and parent_node.child(i).text(0) == display_name:
                    parent_node.removeChild(parent_node.child(i))
            if parent_node.childCount() == 0:
                # no runs left for this sample so remove it
                for i in range(self.invisibleRootItem().childCount()):
                    if (self.invisibleRootItem().child(i) 
                        and self.invisibleRootItem().child(i).text(0) == sample_name
                        ):
                        self.invisibleRootItem().removeChild(
                            self.invisibleRootItem().child(i))

    def add_classified_run(self, run):
        '''Marks a :class:`Run` instance as classified by adding it to the
        :attr:`classified_status` dictionary.

        :param run: Run to mark as classified
        :type run: Run or HWIRun
        '''
        if isinstance(run, str) and run in self.loaded_runs:
            self.classified_status[run] = True

    def add_sample(self, sample_name, *args):
        '''Adds a new sample to the tree. Samples are the
        highest level node in the `RunTree`.

        :param sample_name: Name of sample to add, acts as key so should 
                            be unique.
        :type sample_name: str
        '''
        parent_item = QtWidgets.QTreeWidgetItem(self)
        parent_item.setText(0, sample_name)
        self.samples.append(sample_name)
        for run in args:
            if isinstance(run, (Run, HWIRun)):
                self._add_run_node(run, parent_item)
        logger.debug('Added sample: {}'.format(sample_name))

    def link_sample(self, sample_name):
        '''Links all :class:`Run` instances in a given sample together by both date
        and spectrum using the :meth:`~polo.utils.io_utils.RunLinker.the_big_link`
        method.

        :param sample_name: Name of the sample who's runs should be linked
        :type sample_name: str
        '''
        # gather runs with this sample
        runs_in_sample = [run for run_name, run in self.loaded_runs.items()
                          if run.sampleName == sample_name]
        linked_runs = RunLinker.the_big_link(runs_in_sample)
        linked_runs_dict = {run.run_name: run for run in linked_runs}
        self.loaded_runs.update(linked_runs_dict)

    def add_run_to_tree(self, new_run):
        '''Add a new :class:`Run` instance to the tree. Uses the :class:`Run` instance's 
        :attr:`sampleName` attribute to determine what sample node 
        the :class:`Run` instance should be added
        to. If the sample name does not exist in the tree a new sample node is added.
        If the :class:`Run` instance lacks the :attr:`sampleName` attribute as is the case for 
        non-HWIRuns the :attr:`sampleName` attribute is set to "Non-HWI Runs". 
        If the :class:`Run` instance is an :class:`HWIRun` and lacks the 
        :attr:`sampleName` attribute :attr:`sampleName` is
        set to "Sampleless Runs".

        :param new_run: Run to add to the tree
        :type new_run: Run or HWIRun
        '''

        if new_run.run_name not in self.loaded_runs:
            if isinstance(new_run, HWIRun):
                if hasattr(new_run, 'sampleName'):
                    sample_node = self.findItems(
                        new_run.sampleName, Qt.MatchExactly, column=0)
                    if sample_node:
                        sample_node = sample_node.pop()  # returned as a list
                        self._add_run_node(new_run, sample_node)
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
                    self._add_run_node(new_run, orphan_runs)

            elif isinstance(new_run, Run):
                non_hwi_runs = self.findItems(
                    'Non-HWI Runs', Qt.MatchExactly, column=0)
                if non_hwi_runs:
                    non_hwi_runs = non_hwi_runs.pop()
                else:
                    non_hwi_runs = QtWidgets.QTreeWidgetItem(self)
                    non_hwi_runs.setText(0, 'Non-HWI Runs')

                new_run.sampleName = 'Non-HWI Runs'
                self._add_run_node(new_run, non_hwi_runs)
    
    def _classify_all_runs_slot(self, sample_name):
        '''Classify all the unclassified runs belonging to a the selected
        sample.
        '''
        runs_to_classify = [run for run_name, run in self.loaded_runs.items()
                            if (hasattr(run, 'sampleName') 
                                and run_name not in self.classified_status
                                and run.image_spectrum == IMAGE_SPECS[0]
                                )
                            ]
        self.classify_sample_signal.emit(runs_to_classify)
        

    def contextMenuEvent(self, event):
        '''Handle left click events by creating a popup context menu.

        :param event: QEvent
        :type event: QEvent
        '''
        current_run = self.selected_run
        self.menu = QtWidgets.QMenu(self)
        if current_run:
            # edit_data_action = QtWidgets.QAction('Edit Run Data', self)
            # edit_data_action.triggered.connect(lambda: self._edit_data_slot(event))

            remove_run_action = QtWidgets.QAction('Remove Run', self)
            remove_run_action.triggered.connect(
                lambda: self._remove_run_slot(event))

            open_run_action = QtWidgets.QAction('Open Run', self)
            open_run_action.triggered.connect(
                lambda: self._open_run_slot(event))

            classify_from_mso = QtWidgets.QAction(
                'Add MSO classifications', self)
            classify_from_mso.triggered.connect(
                lambda: self._add_classifications_from_mso_slot(event))

            self.menu.addAction(open_run_action)
            #self.menu.addAction(edit_data_action)
            self.menu.addAction(remove_run_action)
            self.menu.addSeparator()
            self.menu.addAction(classify_from_mso)
            
            self.menu.popup(QtGui.QCursor.pos())
        else:
            # check if left clicked on a sample
            if self.currentItem().text(0) in self.samples:
                classify_all_runs_action = QtWidgets.QAction('Classify All Runs', self)
                classify_all_runs_action.triggered.connect(
                    lambda: self._classify_all_runs_slot(self.currentItem().text(0))
                )
                self.menu.addAction(classify_all_runs_action)
                self.menu.popup(QtGui.QCursor.pos())


            
    

    
        

        

        
