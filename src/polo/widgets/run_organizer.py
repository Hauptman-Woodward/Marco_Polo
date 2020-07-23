import ftplib
import os
from pathlib import Path, PurePosixPath

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QAction, QApplication, QGridLayout

from polo import ICON_DICT, IMAGE_SPECS, SPEC_KEYS
from polo.crystallography.run import HWIRun, Run
from polo.designer.UI_run_organizer import Ui_Form
from polo.threads.thread import *
from polo.utils.dialog_utils import make_message_box
from polo.utils.io_utils import *
from polo.utils.unrar_utils import test_for_working_unrar
from polo.windows.ftp_dialog import FTPDialog
from polo.windows.run_importer import RunImporterDialog

# run organizer should be the outer class and
# run tree should be the inner calss widget


class RunOrganizer(QtWidgets.QWidget):
    '''Widget for organizing and importing runs into Polo.

    :param parent: Parent widget, defaults to None
    :type parent: QWidget, optional
    :param auto_link_runs: If True runs are automatically
                            linked as they are loaded in, defaults to True
    :type auto_link_runs: bool, optional
    '''

    opening_run = pyqtSignal(list)
    classify_run = pyqtSignal(list)
    ftp_download_status = pyqtSignal(bool)

    def __init__(self, parent=None, auto_link_runs=True):

        super(RunOrganizer, self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.auto_link_runs = auto_link_runs  # allow for turn off in settings
        self.current_run = None
        self.shown_unrar_message = False
        self.ftp_download_counter = [0, 0]  # x of y downloads complete
        self._has_been_opened = set([])
        self.ui.pushButton.clicked.connect(self._handle_classification_request)
        self.ui.runTree.itemDoubleClicked.connect(self._handle_opening_run)
        self.ui.runTree.opening_run.connect(self._handle_opening_run)
        self.ui.runTree.remove_run_signal.connect(self._clear_current_run)

        logger.info('Created {}'.format(self))

    def __iter__(self):
        return (run for run_name, run in self.ui.runTree.loaded_runs.items())


    def _clear_current_run(self, run_list):
        '''Clear out the current run from other widgets by emiting a
        `opening_run` signal with a list that does not contain
        a Run or HWIRun object.

        :param run_list: List of runs
        :type run_list: list
        '''
        if run_list:
            self.opening_run.emit([None])

    def _handle_classification_request(self):
        '''Private method to open a classification thread of the currently selected run.
        Calls  :meth:`~polo.widgets.run_organizer.RunOrganizer._open_classification_thread` to
        start the classification thread.
        '''
        selected_runname = self.ui.runTree.currentItem().text(0)
        if selected_runname in self.ui.runTree.loaded_runs:
            selected_run = self.ui.runTree.loaded_runs[selected_runname]
            self._open_classification_thread(selected_run)

    def _handle_opening_run(self, *args):
        '''Private method that signal to other widgets that the current run should be opened
        for analysis and viewing by emiting the `opening_run` signal containing
        the selected run.
        '''
        # get the selected item
        selected_run_name = self.ui.runTree.currentItem().text(0)
        if selected_run_name in self.ui.runTree.loaded_runs:
            selected_run = self.ui.runTree.loaded_runs[selected_run_name]
            if (selected_run.run_name not in self._has_been_opened
                and not hasattr(selected_run, 'save_file_path')):
                backup = self._check_for_existing_backup(selected_run)
                if backup and os.path.isfile(str(backup)):
                    choice = make_message_box(
                        parent=self,
                        message='Found backed up classifications for this run.\
                            Would you like to use them?',
                        buttons=QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
                        ).exec_()
                    if choice == QtWidgets.QMessageBox.Yes:
                        reader = MsoReader(backup)
                        classified_images = reader.classify_images_from_mso_file(
                            images=selected_run.images
                        )
                        if isinstance(classified_images, list):
                            selected_run.images = classified_images
                            message = 'Loaded classifications from backup.'
                        else:
                            message='Failed to load classifications.'
                        make_message_box(
                            parent=self, message=message
                        ).exec_()
            self.opening_run.emit([selected_run])
            self._has_been_opened.add(selected_run.run_name)

    def _open_classification_thread(self, run):
        '''Private method to create and run a classification thread which will run
        the MARCO model on all images in the run passed to `run` argument.

        :param run: Run or HWIRun instance to run MARCO on
        :type run: Run or HWIRun
        '''
        self.ui.progressBar.setMaximum(len(run))
        self.ui.progressBar.setValue(1)  # reset the bar to 0
        self.classification_thread = ClassificationThread(run)
        self.classification_thread.change_value.connect(
            self._set_progress_value)
        self.classification_thread.estimated_time.connect(
            self._set_estimated_classification_time)

        def classification_cleanup():
            self.ui.runTree.setEnabled(True)
            self.ui.runTree.add_classified_run(run)
            logger.info('Closed classification thread: {}'.format(
                self.classification_thread
            ))

        self.classification_thread.finished.connect(classification_cleanup)
        self.ui.runTree.setEnabled(False)
        self.classification_thread.start()
        logger.info('Opened classification thread: {}'.format(
            self.classification_thread))

    def _set_progress_value(self, val):
        '''Private helper method to increment the classification
        progress bar.

        :param val: Value to set progress bar to
        :type val: int
        '''
        self.ui.progressBar.setValue(val)

    def _set_estimated_classification_time(self, time, num_images_remain):
        '''Display the estimated classification time to the user. Time remaining
        is calculated by multiplying the time it took to classify a representative
        image by the number of images that remain to be classified.

        :param time: Time to classify latest image
        :type time: int
        :param num_images_remain: Number of images that still require classification
        :type num_images_remain: int
        '''
        time = time*num_images_remain
        if time >= 60:
            time_string = '{} mins'.format(round(time/60, 2))
        else:
            time_string = '{} secs'.format(round(time))
        self.ui.label_32.setText(time_string)

    def _add_runs_to_tree(self, runs):
        '''Private method to add a set of runs to the runTree.

        :param runs: List of runs to add to the runTree
        :type runs: list
        '''
        sample_names = set([])
        for run in runs:
            self.ui.runTree.add_run_to_tree(run)
            sample_names.add(
                self.ui.runTree.loaded_runs[run.run_name].sampleName)
            # pulling run from runTree ensures it has a sample name if it
            # was added to the tree
        # link the runs together by sample
        for sample in sample_names:
            self.ui.runTree.link_sample(sample)

    def _add_run_from_directory(self, dir_path):
        '''Private method to add a run to the runTree from a directory path.

        :param dir_path: Path to directory to import
        :type dir_path: str or Path
        :return: Run or HWIRun created from directory if successful
        :rtype: Run or HWIRun
        '''
        # use run importer class to make the run
        new_run = RunImporter.import_run_from_directory(str(dir_path))
        if isinstance(new_run, (Run, HWIRun)):
            self._add_runs_to_tree([new_run])
            logger.info('Added run {} from directory'.format(new_run))
        return new_run
        # message box failed to import?
    
    
    def _check_for_existing_backup(self, run):
        '''Check the directory specified by the `BACKUP_DIR` constant for
        a backup mso file that matches the run passed through the `run`
        argument. Run's are matched to mso backups by their run name so it
        the user has renamed their run after the backup is saved it will not
        be found.

        See :meth:`~polo.widgets.run_organizer.RunOrganizer.backup_classifications`
        for details on how the mso files are written.

        :param run: Run to search for mso backup with
        :type run: HWIRun
        :return: Path to mso backup if one exists that matches the `run`, else
                return None
        :rtype: str or None
        '''
        backups = list_dir_abs(str(BACKUP_DIR))
        if backups:
            for each_backup in backups:
                if run.run_name in Path(each_backup).name:
                    return each_backup
        return None

    def _remove_run(self, run=None):
        '''Private method to completely remove a run from Polo.

        :param run: Run to remove from current session, defaults to None
        :type run: Run or HWIRun, optional
        '''
        if not run:
            run_name = self.ui.runTree.currentItem()
        if run_name:
            run_name = run_name.text(0)
            condemned_run = self.ui.runTree.remove_run_from_view(run_name)
            if isinstance(condemned_run, (Run, HWIRun)):
                # need to cut any links that had this run in it
                next_run, prev_run = None, None
                if condemned_run.next_run:
                    next_run = condemned_run.next_run
                if condemned_run.previous_run:
                    prev_run = condemned_run.previous_run
                
                if next_run and prev_run:  # cut condemned run out
                    next_run.previous_run = None
                    prev_run.next_run = None
                    prev_run.link_to_next_date(next_run)
                
                elif next_run:  # condemned run was first in the list
                    next_run.previous_run = None
                    for image in next_run.images:
                        image.previous_image = None
                elif prev_run:  # condemned was last in the list
                    prev_run.next_run = None
                    for image in prev_run.images:
                        image.next_image = None
                
                # need to go around the horn since no backwards pointer
                if condemned_run.alt_spectrum:
                    start = condemned_run.alt_spectrum
                    linked_spectrums = []
                    while start and start.run_name != condemned_run.run_name:
                        linked_spectrums.append(start)
                        start = start.alt_spectrum
                    linked_spectrums[-1].alt_spectrum = None
                    if len(linked_spectrums) > 1:
                        linked_spectrums[0].link_to_alt_spectrum(linked_spectrums[-1])

    def backup_classifications_on_thread(self, run):
        '''Does the exact same thing as 
        :meth:`~polo.widgets.run_organizer.RunOrganizer.backup_classifications` 
        except excutes the job on a `QuickThread` instance to avoid slow
        computers complaining about the GUI being frozen. This has been
        especially prevelant on Windows machines.

        :param run: Run to save as mso file
        :type run: HWIRun
        '''

        write_path = BACKUP_DIR.joinpath(run.run_name)

        def finished_backup():
            if self.backup_thread.result == False:
                make_message_box(
                    parent=self,
                    message='Failed to backup {} human classifications to mso file.'.format(run.run_name)
                    ).exec_()

        writer = MsoWriter(run, write_path)
        self.backup_thread = QuickThread(self.backup_classifications)
        self.backup_thread.finished.connect(finished_backup)
    
    def backup_classifications(self, run):
        '''Write the human classifications of the images in the `run` argument
        to an mso file and store it in the directory specified by the
        `BACKUP_DIR` constant. Does not store MARCO classifications because
        these can be much more easily recreated than human classifications.
        Additionally, when a run is loaded back in and a backup mso exists
        for it Polo assumes the classifications in that mso file are human
        classifications.

        Currently only HWIRuns can be written as mso files because of mso's
        integration with cocktail data and well assignments. Need a different
        format for non-HWI runs that would map filenames to classifications
        and ignore cocktail data / well assignments.

        :param run: Run to backup human classifications
        :type run: HWIRun
        '''

        write_path = BACKUP_DIR.joinpath(run.run_name)
        writer = MsoWriter(run, write_path)
        writer.write_mso_file(use_marco_classifications=False)


        
    def import_saved_runs(self, xtal_files=[]):
        '''Import runs saved to xtal files.

        :param xtal_files: List of xtal files to import runs from, defaults to []
        :type xtal_files: list, optional
        '''
        if not xtal_files:
            xtal_dialog = RunImporter.make_xtal_file_dialog(parent=self)
            xtal_dialog.exec_()
            xtal_files = xtal_dialog.selectedFiles()
        if xtal_files:  # returned as a list
            runs_to_add = []
            for xtal in xtal_files:
                QApplication.setOverrideCursor(Qt.WaitCursor)
                if os.path.isfile(xtal):
                    deserializer = RunDeserializer(xtal)
                    new_run = deserializer.xtal_to_run()
                    if isinstance(new_run, (HWIRun, Run)):
                        runs_to_add.append(new_run)
                    else:
                        QApplication.restoreOverrideCursor()
                        make_message_box(
                            parent=self,
                            message='Could not load run from {}. {}'.format(
                                xtal, new_run)
                        ).exec_()
            self._add_runs_to_tree(runs_to_add)
            logger.info('Added {} runs from saved files'.format(runs_to_add))
        QApplication.restoreOverrideCursor()

    def import_run_from_dialog(self):
        '''Import a run from a file dialog.
        '''
        run_importer_dialog = RunImporterDialog(
            current_run_names=self.ui.runTree.current_run_names,
            parent=self)
        run_importer_dialog.exec_()
        self._add_runs_to_tree(run_importer_dialog.imported_runs.values())
        logger.info('Added {} runs from file dialog'.format(
            run_importer_dialog.imported_runs.values()
        ))
        # for run_name, run in run_importer_dialog.imported_runs.items():
        #     self._add_run_to_tree(run)

    def import_run_from_ftp(self):
        '''Import runs from an FTP server. If an FTP download thread is not already
        running creates an FTPDialog instances and opens it to the user. FTP functions
        are then taken over by the FTPDialog until it is closed.
        '''
        if not test_for_working_unrar() and not self.shown_unrar_message:
            msg = make_message_box(
                message='No working unrar installation found. If you download files via FTP you will have to unrar and import them manually',
                parent=self)
            self.shown_unrar_message = True
            msg.exec_()

        if hasattr(self, 'ftp_download_thread') and self.ftp_download_thread.isRunning():
            msg = make_message_box(
                message='FTP download already in progress. {} of {} files downloaded.'.format(
                    self.ftp_download_counter[0], self.ftp_download_counter[1]
                ),
                parent=self
            )
            msg.exec_()
            return

        ftp_browser = FTPDialog(parent=self)
        ftp_browser.exec_()
        if ftp_browser.ftp and ftp_browser.download_files and ftp_browser.save_dir:
            self.ftp_download_thread = FTPDownloadThread(
                ftp_browser.ftp, ftp_browser.download_files, ftp_browser.save_dir
            )
            self.ftp_download_thread.download_path.connect(
                self.handle_ftp_download)
            self.ftp_download_thread.finished.connect(
                self.finished_ftp_download
            )
            self.ftp_download_status.emit(True)
            self.ftp_download_counter[1] = len(ftp_browser.download_files)
            self.ftp_download_thread.start()
            logger.info('Started FTP download thread {}'.format(
                self.ftp_download_thread
            ))

    def finished_ftp_download(self):
        self.ftp_download_status.emit(False)
        self.ftp_download_counter = [0, 0]  # reset the counter
        logger.info('Finished FTP download thread {}'.format(
            self.ftp_download_thread
        ))
        make_message_box(
            message='All FTP downloads completed!', parent=self
        ).exec_()

    def handle_ftp_download(self, file_path):
        if test_for_working_unrar():
            unpacker = RunImporter.unpack_rar_archive_thread(file_path)
            if unpacker:
                unpacker.finished.connect(lambda: self._add_run_from_directory(
                    str(Path(file_path).with_suffix(''))  # remove rar suffix
                ))
                unpacker.start()
        else:
            pass

        # connect the downloaded file to classification thread if it
        # is in the visible spectrum and another run is not already
        # going can create a kind of que for classification here

        self.ftp_download_counter[0] += 1
        # do something to tell the user that they need to unpack their files
        # message box failed to import?

    def add_run_from_directory(self, dir_path):
        # use run importer class to make the run
        new_run = RunImporter.import_run_from_directory(str(dir_path))
        if isinstance(new_run, (Run, HWIRun)):
            self._add_runs_to_tree([new_run])
        return new_run
        # message box failed to import?
   
    def remove_run(self, run=None):
        if not run:
            run_name = self.ui.runTree.currentItem()
        if run_name:
            run_name = run_name.text(0)
            condemned_run = self.ui.runTree.remove_run_from_view(run_name)
            if isinstance(condemned_run, (Run, HWIRun)):
                # need to cut any links that had this run in it
                next_run, prev_run = None, None
                if condemned_run.next_run:
                    next_run = condemned_run.next_run
                if condemned_run.previous_run:
                    prev_run = condemned_run.previous_run
                
                if next_run and prev_run:  # cut condemned run out
                    next_run.previous_run = None
                    prev_run.next_run = None
                    prev_run.link_to_next_date(next_run)
                
                elif next_run:  # condemned run was first in the list
                    next_run.previous_run = None
                    for image in next_run.images:
                        image.previous_image = None
                elif prev_run:  # condemned was last in the list
                    prev_run.next_run = None
                    for image in prev_run.images:
                        image.next_image = None
                
                # need to go around the horn since no backwards pointer
                if condemned_run.alt_spectrum:
                    start = condemned_run.alt_spectrum
                    linked_spectrums = []
                    while start and start.run_name != condemned_run.run_name:
                        linked_spectrums.append(start)
                        start = start.alt_spectrum
                    linked_spectrums[-1].alt_spectrum = None
                    if len(linked_spectrums) > 1:
                        linked_spectrums[0].link_to_alt_spectrum(linked_spectrums[-1])



                    


