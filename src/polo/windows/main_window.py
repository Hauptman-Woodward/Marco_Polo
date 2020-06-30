import copy
import json
import logging
import os
import random
import sys
import time
import webbrowser
from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QBitmap, QBrush, QColor, QIcon, QPainter, QPixmap
from PyQt5.QtWidgets import QAction, QApplication, QGridLayout

import matplotlib
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from polo import *
from polo.crystallography.cocktail import SignedValue
from polo.crystallography.image import Image
from polo.crystallography.run import HWIRun, Run
from polo.designer.UI_main_window import Ui_MainWindow
from polo.plots.plots import MplCanvas, MplWidget, StaticCanvas
from polo.threads.thread import (ClassificationThread, FTPDownloadThread,
                                 SaveThread)
from polo.utils.io_utils import *
from polo.utils.math_utils import best_aspect_ratio, get_cell_image_dims
from polo.widgets.plate_viewer import graphicsWell, plateViewer
from polo.widgets.slideshow_viewer import SlideshowViewer
# from polo.windows.exporter_dialog import exporterDialog
from polo.windows.ftp_dialog import FTPDialog
from polo.windows.image_pop_dialog import ImagePopDialog
from polo.windows.log_dialog import LogDialog
from polo.windows.run_importer_dialog import RunImporterDialog
# from polo.windows.secure_dave_dailog import SecureSaveDialog
from polo.windows.spectrum_dialog import SpectrumDialog
from polo.windows.time_res_dialog import TimeResDialog
from polo.windows.run_updater_dialog import RunUpdaterDialog

matplotlib.use('Qt5Agg')

logger = make_default_logger(__name__)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    BAR_COLORS = [Qt.darkBlue, Qt.darkRed, Qt.darkGreen, Qt.darkGray]
    # cocktails sorted from earliest to latest (most recent last)
    CRYSTAL_ICON = str(ICON_DICT['crystal'])

    def __init__(self):
        '''
        Initialize main window object. polo is drawn from QT designer generated
        file in the designer folder. All button logic is also set up here.
        '''
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)

        self.loaded_runs = {}  # list of runs
        self.settings = {}  # stores the current settings as dict
        self.classified_runs = {}
        self.current_run = None  # name of current run
        self.cached_plate_scenes = {}
        self.ftp_connection = None
        self.ftp_download_thread = None

        self.menuImport.triggered[QAction].connect(self.handle_image_import)
        self.menuAdvanced_Tools.triggered[QAction].connect(
            self.handle_advanced_tools)
        self.menuExport.triggered[QAction].connect(self.handle_export)
        self.menuHelp.triggered[QAction].connect(self.handle_help_menu)
        self.menuFile.triggered[QAction].connect(self.handle_file_menu)
        self.runOrganizer.itemDoubleClicked.connect(self.handle_opening_run)
        # self.pushButton_7.clicked.connect(self.update_table_view)
        # self.pushButton_8.clicked.connect(self.uncheck_all_filters)
        self.run_interface.currentChanged.connect(self.on_changed_tab)
        self.menuBeta_Testers.triggered[QAction].connect(
            lambda: webbrowser.open(BETA))

       # plot view method connections

        self.plot_viewer_layout = QtWidgets.QVBoxLayout(self.groupBox_4)
        self.matplotlib_widget = StaticCanvas(parent=self.groupBox_4)
        self.plot_viewer_layout.addWidget(self.matplotlib_widget)
        self.toolbar = NavigationToolbar(
            canvas=self.matplotlib_widget, parent=self.groupBox_4)
        self.plot_viewer_layout.addWidget(self.toolbar)

        self.listWidget_3.currentTextChanged.connect(
            self.handle_plot_selection)

        self.set_tab_icons()

        logger.info('Created mainWindow object')

    # ICON setup
    # ========================================================================

    def set_tab_icons(self):
        '''Assigns icons to each of the main run interface tabs
        '''
        self.run_interface.setTabIcon(0, QIcon(str(ICON_DICT['camera'])))
        self.run_interface.setTabIcon(1, QIcon(str(ICON_DICT['plate'])))
        self.run_interface.setTabIcon(2, QIcon(str(ICON_DICT['table'])))
        self.run_interface.setTabIcon(3, QIcon(str(ICON_DICT['graph'])))
        self.run_interface.setTabIcon(4, QIcon(str(ICON_DICT['target'])))

    # Run IO
    # =========================================================================

    # remove the current run add dialog that asks if they are sure they want to
    # drop the run

    def remove_run(self):
        # NOTE IN PROGRESS
        message = 'Are you sure you want to remove run {}.'.format(
            self.current_run.run_name)
        warning = self.make_message_box(
            message, icon=QtWidgets.QMessageBox.Warning,
            buttons=QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel
        )
        choice = warning.exec_()
        if choice == 1024:
            self.loaded_runs.pop(self.current_run.run_name)
            if self.current_run.run_name in self.classified_runs:
                self.classified_runs.pop(self.current_run.run_name)
        else:
            logging.info('Canceled remove run')

    def add_loaded_run(self, run):
        '''
        Add a run object to the loaded_runs attribute and add the run name to
        the available runs listWidget so the user may select this run for
        viewing. After this function call the run will be recoverable using
        its run name as a key in the loaded_runs dictionary.

        :param run: Run Object. New run to make available to the user.
        '''
        self.loaded_runs[run.run_name] = run
        item = QtWidgets.QListWidgetItem(self.listWidget)
        item.setText(run.run_name)
        # self.listWidget.addItem(item)
        logging.info('Loaded run named {}'.format(run.run_name))

    def open_run_import_dialog(self):
        '''
        Creates an instance of the RunImporterDialog class and displays
        that dialog. After the instance is closed by the user checks to see
        if a new run has been created and stored in the new_run attribute of
        the RunImporterDialog instance. If one is present makes it available
        to the user by passing contents of new_run to add_loaded_run.
        '''
        importer_dialog = RunImporterDialog(
            current_run_names=list(self.loaded_runs.keys()))
        if importer_dialog.new_run != None:
            self.add_loaded_run(importer_dialog.new_run)
            logging.info('Added run successfully')
        else:
            logging.info('Attempted to open empty run at {}'.format(
                self.open_run_import_dialog))

    def handle_image_import(self, selection):
        '''
        Handles when the user attempts to import images into Polo. Effectively
        a wrapper around other methods that call provide the functionality to
        each option in the import menu.

        :param selection: QAction. QAction from user menu selection.
        '''
        selection_text = selection.text()
        if selection == self.actionFrom_FTP:
            # check if an ftp download thread is already running
            if self.ftp_download_thread:
                self.make_message_box(
                    message='FTP Download already in progress!',
                    buttons=QtWidgets.QMessageBox.Ok
                ).exec_

            else:
                self.open_ftp_dialog()
        elif selection == self.actionFrom_Saved_Run_3:
            self.handle_opening_saved_run()
        elif selection == self.actionFrom_Directory:
            self.open_run_import_dialog()
        elif selection == self.actionCocktails:
            pass
        else:
            logger.info('Import request matched no QActions at {}'.format(
                self.handle_image_import))
        # TODO allow users to add cocktail files

    def tab_limiter(self):
        if not isinstance(self.current_run, HWIRun):
            # need to disable stuff that requires cocktails
            self.tab_10.setEnabled(False)
            self.make_message_box(
                'Looks like you imported a non-HWI Run. For now optimization screening is disabled.',
                buttons=QtWidgets.QMessageBox.Ok).exec_()

    def handle_opening_run(self, q):
        '''
        Handles whenever a loaded run from the loaded runs list is
        doubleclicked. First sets the selected run to the current_run. If the
        run has not been classified and therefore does not exist in the
        classified_runs dictionary it is classified via the
        open_classification_thread method. If the run has been classified previously
        then it is displayed. Additionally checks the run type to determine what
        plotting methods should be available and enables the navigation by date
        push Buttons if the run has either a next or previous run
        connected to it.

        :param q: QListItem. Run selection from listWidget made by user.
        '''
        run_name = q.text(0)
        if run_name in self.classified_runs:
            self.current_run = self.loaded_runs[run_name]
            # self.update_run_data_tab()
            self.slideshowInspector.run = self.current_run
            self.tableInspector.run = self.current_run
            self.tableInspector.update_table_view()
            self.optimizeWidget.run = self.current_run
            self.plateInspector.run = self.current_run
            self.tab_limiter()  # set allowed tabs by run type
            self.plot_limiter()  # set allowed polo.plots
            # enable nav by time if has linked runs
            logger.info('Loaded new run named {}'.format(
                self.current_run.run_name))
        elif run_name in self.loaded_runs:
            run = self.loaded_runs[run_name]
            if run.image_spectrum == 'Visible':
                # TODO only classify runs in the visible spectrum
                self.open_classification_thread(run_name=run_name)
            else:
                self.classified_runs[run_name] = run

    def handle_export(self, action):
        '''
        Handles when user wants to export the current run. Creates an instance
        of exporterDialog class and displays that dialog to the user.
        '''
        if self.current_run:
            export_path = QtWidgets.QFileDialog.getSaveFileName(
                self, 'Save Run')[0]
            if export_path:
                export_path, export_results = Path(export_path), None
                if action == self.actionAs_HTML:
                    writer = HtmlWriter(self.current_run)
                    writer.write_complete_run_on_thread(export_path, encode_images=True)
                elif action == self.actionAs_CSV:
                    export_path = export_path.with_suffix('.csv')
                    csv_exporter = RunCsvWriter(self.current_run, export_path)
                    export_results = csv_exporter.write_csv()
                
                if export_results == True:
                    status_message = self.make_message_box(
                        message='Current run exported to {}'.format(export_path)
                    )
                else:
                    status_message = self.make_message_box(
                        message='Export to {} failed with error {}'.format(
                            export_path, export_results
                        )
                    )
                # status_message.exec_()
        else:
            logger.info('User attempted to export with no current run')
            self.make_message_box(message='Please load a run first').exec_()

    def handle_file_menu(self, selection):
        '''
        Method that handles all selection possiblities under
        the file menu. Calls the appropriate methods based on the
        value of selection arguement.

        :param selection: QAction. QAction returned by user selecting an item\
            from the file menu.
        '''
        save_path = None
        if self.current_run:
            current_run_saver = XtalWriter(self.current_run, self)
            if selection == self.actionSave_Run:
                sp = self.current_run.save_file_path
                if sp and os.path.exists(sp):  # save run path already exist
                    save_path = sp
            elif selection == self.actionSave_Run_As or save_path == None:
                save_path = self.save_file_dialog()

            if save_path:  # double check wonky stuff happening in save dialog
                current_run_saver.write_xtal_file_on_thread(save_path)
            else:
                self.make_message_box(
                    message='No suitable filepath was given.',
                    buttons=QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel
                )

    def handle_opening_saved_run(self):
        file_dlg = QtWidgets.QFileDialog(parent=self)
        file_dlg.setNameFilter('xtal or xtals (*.xtal *.xtals)')
        file_dlg.exec()
        xtal_file_path = file_dlg.selectedFiles()

        if xtal_file_path:
            xtal_file_path = file_dlg.selectedFiles()[0]
            if os.path.isfile(xtal_file_path):
                run_loader = RunDeserializer(xtal_file_path, self)
                run = run_loader.xtal_to_run_on_thread()

            # if not isinstance(run, (Run, HWIRun)):
            #     error_box = self.make_message_box(
            #         message='Save file could not be read :(',
            #         icon=QtWidgets.QMessageBox.Warning,
            #         buttons=QtWidgets.QMessageBox.Ok
            #     )
            #     error_box.exec()
            # else:
            #     self.loaded_runs[run.run_name] = run
            #     for image in run.images:
            #         if image.machine_class:
            #             self.classified_runs[run.run_name] = run
            #             break
            #     self.listWidget.addItem(run.run_name)
            #     self.loaded_runs[run.run_name].save_file_path = xtal_file_path

    # General Utilities
    # =========================================================================

    def add_loaded_run(self, run):
        if not isinstance(run, (Run, HWIRun)):
            error_box = self.make_message_box(
                message='Could not load run :(',
                icon=QtWidgets.QMessageBox.Warning,
                buttons=QtWidgets.QMessageBox.Ok
            )
            error_box.exec()
        else:
            self.loaded_runs[run.run_name] = run
            for image in run.images:
                if image.machine_class:
                    self.classified_runs[run.run_name] = run
                    break
            self.runOrganizer.add_run(run)
    

    def get_widget_dims(self, widget):
        return widget.width(), widget.height()

    def filter_parser(self, marco_widget=None, human_widget=None,
                      crystal_widget=None, clear_widget=None,
                      precipitate_widget=None, other_widget=None):
        image_types, human, marco = set([]), False, False
        if marco_widget:
            if marco_widget.isChecked():
                marco = True
        if human_widget:
            if human_widget.isChecked():
                human = True
        if crystal_widget:
            if crystal_widget.isChecked():
                image_types.add('Crystals')
        if clear_widget:
            if clear_widget.isChecked():
                image_types.add('Clear')
        if precipitate_widget:
            if precipitate_widget.isChecked():
                image_types.add('Precipitate')
        if other_widget:
            if other_widget.isChecked():
                image_types.add('Other')

        if not image_types and not human and not marco:
            marco, human = True, True
            image_types = set(
                ['Crystals', 'Precipitate', 'Clear', 'Other'])

        return image_types, human, marco

    def set_run_linking(self, disabled=True):
        # temp disable run linking while classifcation thread is
        # open to prevent semi linked runs
        self.menuAdvanced_Tools.setDisabled(disabled)
        logger.info('Set run linked tools enabled to {}'.format(disabled))

    def make_message_box(self, message, icon=QtWidgets.QMessageBox.Information,
                         buttons=QtWidgets.QMessageBox.Ok,
                         connected_function=None):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(icon)
        msg.setText(message)
        msg.setStandardButtons(buttons)
        if connected_function:
            msg.buttonClicked.connect(connected_function)

        logger.info('Made message box with message "{}"'.format(message))
        return msg

    def layout_widget_lister(self, layout):
        return (layout.itemAt(i) for i in range(layout.count()))
    

    def handle_help_menu(self, action):
        if action == self.actionQuickstart_Guide:
            webbrowser.open(QUICKSTART)
        elif action == self.actionDocumentation:
            webbrowser.open(DOCS)
        elif action == self.actionFAQ:
            webbrowser.open(FAQS)
        elif action == self.actionUser_Guide:
            webbrowser.open(USER_GUIDE)
        elif action == self.actionAbout:
            webbrowser.open(ABOUT)

    # Table View Methods
    # ==========================================================================

    # def parse_table_filters(self):
    #     image_types, human, marco = self.filter_parser(
    #         marco_widget=self.checkBox_11,
    #         human_widget=self.checkBox_12,
    #         crystal_widget=self.checkBox_7,
    #         clear_widget=self.checkBox_8,
    #         precipitate_widget=self.checkBox_9,
    #         other_widget=self.checkBox_10
    #     )
    #     # add hook ups for cocktail filters here
    #     # add sort by hook ups here
    #     return image_types, human, marco

    # def uncheck_all_filters(self):
    #     check_widgets = self.layout_widget_lister(self.gridLayout_3)
    #     for widget in check_widgets:
    #         if type(widget) == QtWidgets.QCheckBox:
    #             widget.setChecked(False)

    # def update_table_view(self):
    #     image_types, human, marco = self.parse_table_filters()
    #     self.tableViewer.set_current_data(image_types, human, marco)
    #     self.tableViewer.populate_table()

    # Plot Window Methods
    # ==========================================================================

      # clears the current plot and draws an empty figure in theory

    def handle_plot_selection(self):
        if self.current_run:
            current_item = self.listWidget_3.currentItem()
            if current_item:
                current_text = current_item.text()
                if current_text == 'Plate Heatmaps':
                    self.matplotlib_widget.plot_plate_heatmaps(
                        self.current_run)
                elif current_text == 'MARCO Accuracy':
                    self.matplotlib_widget.plot_meta_stats(self.current_run)
                elif current_text == 'Classification Counts':
                    self.matplotlib_widget.plot_bars(self.current_run)
                elif current_text == 'Classification Progress':
                    self.matplotlib_widget.plot_classification_progress(
                        self.current_run)
                elif current_text == 'Cocktail':
                    self.matplotlib_widget.plot_additive_map(self.current_run)

    # allow or disallow access to ploting methods based on run object type
    def plot_limiter(self):
        self.listWidget_3.clear()
        self.listWidget_3.addItems(self.current_run.AllOWED_PLOTS)

    def get_current_plot_selections(self):
        return {
            'type': self.comboBox.currentText(),
            'x_axis': self.comboBox_2.currentText(),
            'y_axis': self.comboBox_3.currentText()
        }

    def get_current_plot_labels(self):
        return {
            'title': self.lineEdit_2.text(),
            'x_lab': self.lineEdit_3.text(),
            'y_lab': self.lineEdit_4.text()

        }

    def apply_plot_selection_logic(self):
        BAR_X_VARS = ['Human Classification', 'MARCO Classicication',
                      '']
        BAR_Y_VARS = ['Number Images']
        VIOLIN_X_VARS = ['Human Classification', 'MARCO Classification']
        VIOLIN_Y_VARS = ['Cocktail pH', 'Number Images']

        # method for enableing and disabling selections based on other selections
        if self.comboBox.currentText() == 'Plate Heatmaps':
            self.comboBox_2.clear()
            self.comboBox_3.clear()
        elif self.comboBox.currentText() == 'Bar':
            self.clear_and_set_variable_boxes(BAR_X_VARS, BAR_Y_VARS)
        elif self.comboBox.currentText() == 'Violin':
            self.clear_and_set_variable_boxes(VIOLIN_X_VARS, VIOLIN_Y_VARS)

        self.set_default_plot_labels()

    def set_default_plot_labels(self):
        # set title
        x_var = self.comboBox_2.currentText()
        y_var = self.comboBox_3.currentText()

        self.lineEdit_2.setText('{} vs. {}'.format(
            x_var, y_var
        ))
        self.lineEdit_3.setText(x_var)
        self.lineEdit_4.setText(y_var)

    def clear_and_set_variable_boxes(self, x_vars, y_vars):
        '''
        Helper function for apply_plot_selection_logic that clears the
        two variable combo boxes and sets new values to the values
        contained in the x_vars and y_vars lists.
        '''
        self.comboBox_2.clear()
        self.comboBox_3.clear()
        self.comboBox_2.addItems(x_vars)
        self.comboBox_3.addItems(y_vars)

    # Dialog Windows (Open and Handle Methods)
    # =========================================================================

    def open_run_updater_dialog(self):
        if self.current_run:
            run_updater = RunUpdaterDialog(self.current_run,
            list(self.loaded_runs.keys()), self)
        else:
            self.make_message_box('Please load a run first.').exec_()

    def open_ftp_dialog(self):
        dialog = FTPDialog(self.ftp_connection)
        if dialog.ftp and dialog.download_files and dialog.save_dir:
            self.ftp_download_thread = FTPDownloadThread(
                dialog.ftp, dialog.download_files, dialog.save_dir
            )
            self.ftp_download_thread.finished.connect(
                self.finished_ftp_download)
            self.ftp_download_thread.start()
        QApplication.restoreOverrideCursor()

    def finished_ftp_download(self):
        m = self.make_message_box('Your FTP download has completed! Please decompress the downloaded files before attempting to import into Polo',
                                  buttons=QtWidgets.QMessageBox.Ok)
        m.exec_()
        self.ftp_download_thread = None  # reset the download thread so
        # FTP browser can be opened again

    def open_spectra_dialog(self):
        spec_dialog = SpectrumDialog(loaded_runs=self.loaded_runs)
        self.load_runs = spec_dialog.loaded_runs
        if self.current_run and self.current_run.alt_spectrum:
            self.plateInspector.set_alt_spectrum_buttons(allow=True)
            self.slideshowInspector.set_alt_spectrum_buttons()
            # enable alt spectrum selections

    def open_time_link_dialog(self):
        time_dialog = TimeResDialog(available_runs=self.loaded_runs)
        self.loaded_runs = time_dialog.available_runs
        if self.current_run:  # run is open
            self.current_run = self.loaded_runs[self.current_run.run_name]

    def save_file_dialog(self):
        file_name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Run')
        return file_name[0]

    def open_settings_dialog(self):
        settings = settingsDialog()

    def handle_advanced_tools(self, selection):
        if selection == self.actionTime_Resolved:
            self.open_time_link_dialog()
        elif selection == self.actionView_Log_2:
            self.open_log_dialog()
        elif selection == self.actionAdd_Image_Type:
            self.open_spectra_dialog()
        elif selection == self.actionEdit_Current_Run_Data:
            self.open_run_updater_dialog()

    def open_file_dialog(self, dialog_type='Dir'):
        file_dlg = QtWidgets.QFileDialog()
        if dialog_type == 'Dir':
            file_dlg.setFileMode(QtWidgets.QFileDialog.Directory)
        filenames = ''
        if file_dlg.exec():
            filenames = file_dlg.selectedFiles()
            return filenames[0]
        else:
            return False

    def open_log_dialog(self):
        log_dialog = LogDialog()

    def open_secure_save_dialog(self, file_path, mode):
        ss = SecureSaveDialog(file_path, decrypt=mode)

    # Run Metadata Methods
    # ==========================================================================

    # Journal Entry Methods
    # --------------------------------------------------------------------------

    # def update_run_data_tab(self):
    #     if self.current_run:
    #         entry_strings = []

    #         if self.current_run.journal == None:
    #             self.current_run.journal = {}  # last ditch catch of empty journal

    #         for entry_date, contents in self.current_run.journal.items():
    #             title, words = contents
    #             entry_strings.append('{} - {}'.format(title, entry_date))
    #         entry_strings = sorted(entry_strings)
    #         self.listWidget_2.clear()
    #         self.listWidget_2.addItems(entry_strings)

    #         if not self.lineEdit_2.text():
    #             self.set_default_journal_entry()

    # def set_default_journal_entry(self):
    #     if self.current_run:
    #         self.lineEdit_2.setText('Entry Number: {}'.format(
    #             len(self.current_run.journal)))

    # def add_journal_entry(self):
    #     '''
    #     Adds a journal entry based on the content in the current working
    #     space
    #     '''
    #     if self.current_run:
    #         title, contents = (
    #             self.lineEdit_2.text(),
    #             self.plainTextEdit.toPlainText())
    #         if title:
    #             if contents:
    #                 self.current_run.add_journal_entry(
    #                     contents=contents, title=title)
    #                 self.update_run_data_tab()
    #                 self.plainTextEdit.clear()
    #                 self.lineEdit_2.clear()
    #         else:
    #             text, _ = QtWidgets.QInputDialog.getText(
    #                 self, '', 'Enter a Title for Entry:'
    #             )
    #             self.lineEdit_2.setText(text)

    # def delete_journal_entry(self):
    #     '''
    #     Deletes the currently selected journal entry.
    #     '''
    #     if self.current_run:
    #         current_item_text = self.listWidget_2.currentItem().text()
    #         message = 'Are you sure you want to delete entry {}?'.format(
    #             current_item_text
    #         )
    #         warning = self.make_message_box(
    #             message, icon=QtWidgets.QMessageBox.Warning,
    #             buttons=QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel
    #         )
    #         choice = warning.exec_()
    #         if choice == 1024:
    #             self.listWidget_2.takeItem(self.listWidget_2.currentRow())
    #             entry_key = current_item_text.split(' - ')[-1]
    #             if entry_key in self.current_run.journal:
    #                 self.current_run.journal.pop(entry_key)

    # def show_journal_entry(self, entry):
    #     if self.current_run:
    #         entry_key = entry.text().split(' - ')[-1]
    #         title, contents = self.current_run.journal[entry_key]
    #         self.plainTextEdit.setPlainText(contents)
    #         self.lineEdit_2.setText(title)

    # def clear_journal_workspace(self):
    #     self.lineEdit_2.clear()
    #     self.plainTextEdit.clear()

    # Run Data Tab
    # =========================================================================

    def update_classification_progress(self):
        # BUG THIS METHOD DOES NOT ACTUALLY WORK
        if self.current_run:
            progress = self.current_run.get_images_by_classification()
            total_images = len(self.current_run)
            for key in progress:
                if key == 'Crystals':
                    self.progressBar_2.setValue(
                        round(len(progress[key]) / total_images))
                elif key == 'Clear':
                    self.progressBar_3.setValue(
                        round(len(progress[key]) / total_images))
                elif key == 'Precipitate':
                    self.progressBar_4.setValue(
                        round(len(progress[key]) / total_images))
                elif key == 'Other':
                    self.progressBar_5.setValue(
                        round(len(progress[key]) / total_images))

    # Inter Tab Controls and Other
    # ==========================================================================

    def on_changed_tab(self, i):
        '''
        Handles GUI behavior when a user switches to one tab to another.

        :param i: Int. The index of the current tab, after user has changed tabs.
        '''
        i = int(i)  # make sure its actually an int
        if self.current_run:
            if self.current_run.run_name in self.loaded_runs:
                if i == 0:
                    pass
                    # self.new_slideshow_image_routine()
                elif i == 2:
                    self.handle_plot_selection()  # refresh the current plot
                elif i == 5:  # run data editor
                    self.current_run.annotations = self.plainTextEdit.toPlainText()
                elif i == 4:
                    self.optimizeWidget.update()
                    # self.populate_hit_combo()
                    # need better way of updating

    # Threading
    # ==========================================================================

    def open_classification_thread(self, run_name):
        '''
        Updates the mainwindow progress bar based on number of images in the
        current_run and opens a new ClassificationThread which then works to
        classify all images in the current_run. Progress bar is then connected
        to the ClassificationThread method change_value which updates the bar
        status as images are classified. Finally, adds the current run to the
        classified runs dictionary.

        :param run_name: Unique run name to open classification thread on
        :type run_name: str
        '''
        def clean_marco_thread():
            self.classified_runs[run_name] = self.loaded_runs[run_name]
            #self.listWidget.setEnabled(True)
            self.set_run_linking(disabled=False)

        #self.listWidget.setEnabled(False)  # disable loading runs
        # while a thread is open

        # self.progressBar.setMaximum(len(self.current_run))
        self.set_run_linking(disabled=True)  # disable to prevent partial links
        self.progressBar.setMaximum(len(self.loaded_runs[run_name]))
        self.progressBar.setValue(1)  # reset the bar to 0
        self.thread = ClassificationThread(self.loaded_runs[run_name])
        self.thread.change_value.connect(self.set_progress_value)
        self.thread.estimated_time.connect(
            self.set_estimated_classification_time)
        self.thread.finished.connect(clean_marco_thread)
        self.thread.start()
        logger.info('Started classification thread for {}'.format(
            self.loaded_runs[run_name]
        ))

    def set_progress_value(self, val):
        '''
        Helper function to change progres bar value when thread is working.
        '''
        self.progressBar.setValue(val)

    def set_estimated_classification_time(self, time, num_images_remain):
        time = time*num_images_remain
        if time >= 60:
            time_string = '{} mins'.format(round(time/60, 2))
        else:
            time_string = '{} secs'.format(round(time))
        self.label_32.setText(time_string)

    def show_error_message(self, message='Error :('):
        error_dlg = QtWidgets.QErrorMessage(self)
        error_dlg.showMessage(message)
        error_dlg.exec()

    # Depreciated Methods
    # ==========================================================================

    def render_bar_graph(self, image=None, bar_spacing=8, x_offset=80):
        '''
        Renders a bar graph of prediction confidencse into the mainwindow
        based on the prediction dict of a given image.
        '''
        if not image:
            image = self.current_run.get_current_image()

        self.marco_bars.canvas.fig.clear()
        #self.marco_bars = MplWidget(self.graphicsView_2, 1, 1, 100)
        self.marco_bars.single_image_confidence(image)
        self.marco_bars.canvas.draw()  # need to fix this up
        # Summary Stats Methods
    # ==========================================================================

    def render_summary_stats(self, run=None):
        self.summary_polo.plots.canvas.fig.clear()
        if not run:  # allow passing of other run outside of current
            run = self.current_run
        self.summary_polo.plots.meta_stats(self.current_run)
        self.summary_polo.plots.canvas.draw()
