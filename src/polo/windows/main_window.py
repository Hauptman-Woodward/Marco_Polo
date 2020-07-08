import copy
import json
import logging
import os
import random
import sys
import time
import webbrowser
from pathlib import Path

from matplotlib.backends.backend_qt5agg import \
    NavigationToolbar2QT as NavigationToolbar
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QPixmapCache
from PyQt5.QtWidgets import QAction, QApplication, QGridLayout

from polo import *
from polo.crystallography.run import HWIRun, Run
from polo.designer.UI_main_window import Ui_MainWindow
from polo.plots.plots import MplCanvas, MplWidget, StaticCanvas
from polo.utils.io_utils import *
from polo.utils.math_utils import best_aspect_ratio, get_cell_image_dims
from polo.utils.dialog_utils import make_message_box
from polo.widgets.plate_viewer import plateViewer
from polo.widgets.slideshow_viewer import SlideshowViewer

from polo.windows.ftp_dialog import FTPDialog
from polo.windows.image_pop_dialog import ImagePopDialog
from polo.windows.log_dialog import LogDialog
from polo.windows.run_importer_dialog import RunImporterDialog
from polo.windows.run_updater_dialog import RunUpdaterDialog

from polo.windows.spectrum_dialog import SpectrumDialog
from polo.windows.time_res_dialog import TimeResDialog


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

        self.current_run = None  # name of current run
        self.cached_plate_scenes = {}
        self.runOrganizer.opening_run.connect(self.handle_opening_run)
        self.menuImport.triggered[QAction].connect(self.handle_image_import)

        #self.menuAdvanced_Tools.triggered[QAction].connect(
        #    self.handle_advanced_tools)
        # TODO make new run linker interface

        self.menuExport.triggered[QAction].connect(self.handle_export)
        self.menuHelp.triggered[QAction].connect(self.handle_help_menu)
        self.menuFile.triggered[QAction].connect(self.handle_file_menu)
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

    # def remove_run(self):
    #     # NOTE IN PROGRESS
    #     message = 'Are you sure you want to remove run {}.'.format(
    #         self.current_run.run_name)
    #     warning = self.make_message_box(
    #         message, icon=QtWidgets.QMessageBox.Warning,
    #         buttons=QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel
    #     )
    #     choice = warning.exec_()
    #     if choice == 1024:
    #         self.loaded_runs.pop(self.current_run.run_name)
    #         if self.current_run.run_name in self.classified_runs:
    #             self.classified_runs.pop(self.current_run.run_name)
    #     else:
    #         logging.info('Canceled remove run')

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
            self.runOrganizer.import_run_from_ftp()
        elif selection == self.actionFrom_Saved_Run_3:
            self.runOrganizer.import_from_saved_run()
        elif selection == self.actionFrom_Directory:
            self.runOrganizer.import_run_from_dialog()
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
            make_message_box(
                parent=self,
                message='Looks like you imported a non-HWI Run. For now optimization screening is disabled.'
                ).exec_()

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
        if isinstance(q, list) and len(q) > 0:
            if self.current_run:
                self.current_run.unload_all_pixmaps()
                QPixmapCache.clear()

            # only keep the pixmaps for the current run loaded
            # other pixmaps from other runs will be loaded if the user
            # switches between dates or spectrums though

            self.current_run = q.pop()
            if self.current_run.image_spectrum == IMAGE_SPECS[0]:  # is visible
                self.current_run.insert_into_alt_spec_chain()
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
                    self.writer = HtmlWriter(self.current_run)
                    QApplication.setOverrideCursor(Qt.WaitCursor)
                    self.setEnabled(False)
                    self.writer.write_complete_run(
                        export_path, encode_images=True)
                    self.setEnabled(True)
                    QApplication.restoreOverrideCursor()
                elif action == self.actionAs_CSV:
                    export_path = export_path.with_suffix('.csv')
                    csv_exporter = RunCsvWriter(self.current_run, export_path)
                    export_results = csv_exporter.write_csv()
                elif action == self.actionAs_MSO:
                    writer = MsoWriter(self.current_run, export_path)
                    writer.write_mso_file()

        else:
            logger.info('User attempted to export with no current run')
            make_message_box(
                parent=self,
                message='Please load a run first'
                ).exec_()

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
                make_message_box(
                    parent=self,
                    message='No suitable filepath was given.'
                    ).exec_()


    # General Utilities
    # =========================================================================    

    def get_widget_dims(self, widget):
        '''Returns the width and height as a tuple of a given widget.

        :param widget: QWidget
        :type widget: QWidget
        :return: width and height of the widget
        :rtype: tuple
        '''
        return widget.width(), widget.height()

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

    # Plot Window Methods
    # =========================================================================

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
            make_message_box(
                parent=self,
                message='Please load a run first.'
                ).exec_()

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


    # Inter Tab Controls and Other
    # =========================================================================

    def on_changed_tab(self, i):
        '''
        Handles GUI behavior when a user switches to one tab to another.

        :param i: Int. The index of the current tab, after user has changed tabs.
        '''
        i = int(i)  # make sure its actually an int
        if self.current_run:
            if i == 0:
                pass
                # self.new_slideshow_image_routine()
            elif i == 2:
                self.handle_plot_selection()  # refresh the current plot
            elif i == 5:  # run data editor
                self.current_run.annotations = self.plainTextEdit.toPlainText()
            elif i == 4:
                self.optimizeWidget.update()


    def show_error_message(self, message='Error :('):
        error_dlg = QtWidgets.QErrorMessage(self)
        error_dlg.showMessage(message)
        error_dlg.exec()

    # Depreciated Methods
    # =========================================================================