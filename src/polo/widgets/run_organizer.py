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
from polo.utils.io_utils import RunDeserializer, RunLinker
from polo.utils.unrar_utils import test_for_working_unrar
from polo.windows.ftp_dialog import FTPDialog
from polo.windows.run_importer_dialog import RunImporter, RunImporterDialog

# run organizer should be the outer class and
# run tree should be the inner calss widget


class RunOrganizer(QtWidgets.QWidget):

    opening_run = pyqtSignal(list)
    classify_run = pyqtSignal(list)
    ftp_download_status = pyqtSignal(bool)

    def __init__(self, parent=None, loaded_runs={},
                 classified_runs={}, auto_link_runs=True):

        super(RunOrganizer, self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.auto_link_runs = auto_link_runs  # allow for turn off in settings
        self.current_run = None
        self.classified_runs = {}
        self.shown_unrar_message = False
        self.ftp_download_counter = [0, 0]  # x of y downloads complete
        self.ui.pushButton.clicked.connect(self.handle_classification_request)
        self.ui.runTree.itemDoubleClicked.connect(self.handle_opening_run)

    def handle_classification_request(self):
        selected_runname = self.ui.runTree.currentItem().text(0)
        if selected_runname in self.ui.runTree.loaded_runs:
            selected_run = self.ui.runTree.loaded_runs[selected_runname]
            self.open_classification_thread(selected_run)

    def handle_opening_run(self, *args):
        # get the selected item
        selected_runname = self.ui.runTree.currentItem().text(0)
        selected_run = None
        if selected_runname in self.ui.runTree.classified_runs:
            selected_run = self.ui.runTree.classified_runs[selected_runname]
        elif selected_runname in self.ui.runTree.loaded_runs:
            selected_run = self.ui.runTree.loaded_runs[selected_runname]
        else:
            make_message_box('It appears this run no longer exists').exec_()
        if selected_run:
            self.opening_run.emit([selected_run])

        # if selected_runname in self.ui.runTree.classified_runs:
        #     selected_run = self.ui.runTree.classified_runs[selected_runname]
        #     self.opening_run.emit([selected_run])
        # else:
        #     if selected_runname in self.ui.runTree.loaded_runs:
        #         selected_run = self.ui.runTree.loaded_runs[selected_runname]
        #         if selected_run.image_spectrum == IMAGE_SPECS[0]:  # visible
        #             # self.classify_run.emit([selected_run])
        #             self.open_classification_thread(selected_run)
        #         else:
        #             self.ui.runTree.add_classified_run(selected_run)
        #             self.opening_run.emit([selected_run])
        #     else:
        #         pass

    def open_classification_thread(self, run):
        self.ui.progressBar.setMaximum(len(run))
        self.ui.progressBar.setValue(1)  # reset the bar to 0
        self.classification_thread = ClassificationThread(run)
        self.classification_thread.change_value.connect(
            self.set_progress_value)
        self.classification_thread.estimated_time.connect(
            self.set_estimated_classification_time)

        def classification_cleanup():
            self.ui.runTree.setEnabled(True)
            self.ui.runTree.add_classified_run(run)

        self.classification_thread.finished.connect(classification_cleanup)
        self.ui.runTree.setEnabled(False)
        self.classification_thread.start()

    def set_progress_value(self, val):
        self.ui.progressBar.setValue(val)

    def set_estimated_classification_time(self, time, num_images_remain):
        time = time*num_images_remain
        if time >= 60:
            time_string = '{} mins'.format(round(time/60, 2))
        else:
            time_string = '{} secs'.format(round(time))
        self.ui.label_32.setText(time_string)

    def import_from_saved_run(self):

        xtal_dialog = RunImporter.make_xtal_file_dialog(parent=self)
        xtal_dialog.exec_()
        xtal_file = xtal_dialog.selectedFiles()
        if xtal_file:  # returned as a list
            xtal_file = xtal_file[0]
            if os.path.isfile(xtal_file):
                r = RunDeserializer(
                    xtal_file).xtal_to_run()
                self.ui.runTree.add_run_to_tree(r)
                self.ui.runTree.add_classified_run(r)

                # self.new_run_thread = RunDeserializer(
                #     xtal_file).xtal_to_run_on_thread()

                # def finished_import():
                #     result = self.new_run_thread.result
                #     if isinstance(result, (Run, HWIRun)):
                #         self.ui.runTree.add_run_to_tree(result)
                #         self.ui.runTree.add_classified_run(result)
                #     else:
                #         pass
                #     # shoe error message
                # self.new_run_thread.finished.connect(finished_import)
                # self.new_run_thread.start()

    def import_run_from_dialog(self):
        run_importer_dialog = RunImporterDialog(
            current_run_names=self.ui.runTree.current_run_names,
            parent=self)
        if (
            hasattr(run_importer_dialog, 'new_run')
            and isinstance(run_importer_dialog.new_run, (HWIRun, Run))
        ):
            self.ui.runTree.add_run_to_tree(run_importer_dialog.new_run)

    def import_run_from_ftp(self):
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

    def finished_ftp_download(self):
        self.ftp_download_status.emit(False)
        self.ftp_download_counter = [0, 0]  # reset the counter
        make_message_box(
            message='All FTP downloads completed!', parent=self
        ).exec_()

    def handle_ftp_download(self, file_path):
        if test_for_working_unrar():
            unpacker = RunImporter.unpack_rar_archive_thread(file_path)
            if unpacker:
                unpacker.finished.connect(lambda: self.add_run_from_directory(
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
            self.ui.runTree.add_run_to_tree(new_run)
        # message box failed to import?
