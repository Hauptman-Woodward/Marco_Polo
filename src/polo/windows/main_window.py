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
from PyQt5.QtWidgets import QAction, QGridLayout, QApplication

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
from polo.windows.run_updater_dialog import RunUpdaterDialog
from polo.windows.pptx_dialog import PptxDesignerDialog

from polo.windows.spectrum_dialog import SpectrumDialog
from polo.windows.time_res_dialog import TimeResDialog


logger = make_default_logger(__name__)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    '''QMainWindow that ultimately is the parent of all other
    included widgets.
    '''
    BAR_COLORS = [Qt.darkBlue, Qt.darkRed, Qt.darkGreen, Qt.darkGray]
    # cocktails sorted from earliest to latest (most recent last)
    CRYSTAL_ICON = str(ICON_DICT['crystal'])

    def __init__(self):

        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)
        self.current_run = None
        self.runOrganizer.opening_run.connect(self._handle_opening_run)

        # menu connections 
        self.menuImport.triggered[QAction].connect(self._handle_image_import)
        self.menuExport.triggered[QAction].connect(self._handle_export)
        self.menuHelp.triggered[QAction].connect(self._handle_help_menu)
        self.menuFile.triggered[QAction].connect(self._handle_file_menu)
        self.menuBeta_Testers.triggered[QAction].connect(
            lambda: webbrowser.open(BETA))
        self.menuTools.triggered[QAction].connect(self._handle_tool_menu)

        # change tab updates control
        self.run_interface.currentChanged.connect(self._on_changed_tab)

        # plot viewer connections 
        self.plot_viewer_layout = QtWidgets.QVBoxLayout(self.groupBox_4)
        self.matplotlib_widget = StaticCanvas(parent=self.groupBox_4)
        self.plot_viewer_layout.addWidget(self.matplotlib_widget)
        self.toolbar = NavigationToolbar(
            canvas=self.matplotlib_widget, parent=self.groupBox_4)
        self.plot_viewer_layout.addWidget(self.toolbar)
        self.listWidget_3.currentTextChanged.connect(
            self._handle_plot_selection)
        

        self._set_tab_icons()

        logger.info('Created {}'.format(self))
    
    @staticmethod
    def get_widget_dims(self, widget):
        '''Returns the width and height of a :class:`QWidget`
        as a tuple.

        :param widget: QWidget
        :type widget: QWidget
        :return: width and height of the widget
        :rtype: tuple
        '''
        return widget.width(), widget.height()

    @staticmethod
    def layout_widget_lister(self, layout):
        '''List all widgets in a given layout.

        :param layout: QLayout that contains widgets    
        :type layout: QLayout
        :return: Tuple of widgets in the given layout
        :rtype: tuple
        '''
        return (layout.itemAt(i) for i in range(layout.count()))
    
    @staticmethod
    def delete_all_backups():
        '''Deletes all backup mso files.

        :raises e: Any exceptions thrown by the function call
        :return: True, if backups are deleted
        :rtype: bool
        '''
        try:
            backup_files = list_dir_abs(str(BACKUP_DIR))
            if backup_files:
                for each_file in backup_files:
                    os.remove(str(each_file))
            return True
        except Exception as e:
            logger.error('Caught {} while calling {}'.format(
                            e, MainWindow.delete_all_backups))
            raise e
    
    def closeEvent(self, event):
        '''Handle main window close events. Writes mso backup files of
        all loaded runs that have human classifications so they can be
        restored later.

        :param event: QEvent
        :type event: QEvent
        '''
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.setEnabled(False)
        try:
            for run in self.runOrganizer:
                if run:
                    for image in run.images:
                        if image.human_class:
                            self.runOrganizer.backup_classifications(run)
                            break
                    # only backup files for runs with human classifications
        except Exception as e:
            logger.error('Caught {} while calling {}'.format(
                            e, self.closeEvent))
            QApplication.restoreOverrideCursor()
            make_message_box(
                parent=self,
                message='Failed to backup all runs {}'.format(e)).exec_()
        self.setEnabled(True)
        QApplication.restoreOverrideCursor()
        event.accept()
    
    def _check_current_run_for_missing_images(self):
        if isinstance(self.current_run, HWIRun):
            num_images = len([1 for i in self.current_run.images if not i.is_placeholder])
            message = ''
            if num_images > 1536:
                message = [
                    'There are {} more images in the selected run than'.format(num_images - 1536),
                    'the max plate size of 1536. Well assignments may not be',
                    'accurate! Please re-download this run or remove the',
                    'the extra images.' 
                ]
            elif num_images < 1536 and num_images != 96:
                message=[
                    'It looks like this run may be missing images.',
                    'HWI runs usually have 1536 images or sometimes 96 images',
                    'but this run has {} images.'.format(num_images),
                    'It is recommended to redownload this run before you do',
                    'any further image processing or classification'
                ]
            if message:
                make_message_box(
                    parent=self,
                    message=' '.join(message)
                ).exec_()

    def _set_tab_icons(self):
        '''Private method that assigns icons to each of the main run 
        interface tabs. Should be called in the `__init__` method before
        the main window is shown to the user.
        '''
        self.run_interface.setTabIcon(0, QIcon(str(ICON_DICT['camera'])))
        self.run_interface.setTabIcon(1, QIcon(str(ICON_DICT['plate'])))
        self.run_interface.setTabIcon(2, QIcon(str(ICON_DICT['table'])))
        self.run_interface.setTabIcon(3, QIcon(str(ICON_DICT['graph'])))
        self.run_interface.setTabIcon(4, QIcon(str(ICON_DICT['target'])))

    def _tab_limiter(self):
        '''Private method that limits the interfaces that a user is allowed
        to interact with based on the type of :class:`Run` they have loaded and
        selected. Currently, :class:`Run` functionality is limited due to the fact
        cocktails cannot be mapped to images.
        '''
        if self.current_run and not isinstance(self.current_run, HWIRun):
            # need to disable stuff that requires cocktails
            self.tab_10.setEnabled(False)  # optimize tab
            self.tab_2.setEnabled(False)  # plate view tab
            make_message_box(
                parent=self,
                message='Looks like you imported a non-HWI Run. For now optimization screening and plate view is disabled.'
                ).exec_()
        else:
            self.tab_10.setEnabled(True)
            self.tab_2.setEnabled(True)

    def _handle_opening_run(self, new_run):
        '''Private method that handles opening a run. For the most part,
        this means setting the :attr:`run` attribute of other widgets to the
        `new_run` argument. The setter methods of these widgets should then handle
        updating their interfaces to reflect the new run being
        opened. Also calls :meth:`~polo.windows.main_window.MainWindow._tab_limiter`
        and :meth:`~polo.windows.main_window.MainWindow._plot_limiter` to set 
        allowed functions for the user based on the type of run they open.

        Additionally, if this is not the first run to be opened, before
        the `new_run` is set as the :attr:`current_run` the pixmaps of the 
        :attr:`current_run` are unloaded to free up memory.

        :param q: List containing the run to be opened. Likely originating from
                  the :class:`RunOrganizer` widget.
        :type q: list
        '''
        try:
            if isinstance(new_run, list) and len(new_run) > 0:
                if self.current_run:
                    self.current_run.unload_all_pixmaps()
                    QPixmapCache.clear()
                
                    for image in self.current_run.images:
                        if image.human_class:
                            self.runOrganizer.backup_classifications_on_thread(
                                self.current_run)
                            break

                self.current_run = new_run.pop()
                self._check_current_run_for_missing_images()
                if (hasattr(self.current_run, 'insert_into_alt_spec_chain')
                    and self.current_run.image_spectrum == IMAGE_SPECS[0]
                    ):
                    self.current_run.insert_into_alt_spec_chain()
                self.slideshowInspector.run = self.current_run
                self.tableInspector.run = self.current_run
                self.tableInspector.update_table_view()
                self.optimizeWidget.run = self.current_run
                self.plateInspector.run = self.current_run
                self._tab_limiter()  # set allowed tabs by run type
                self._plot_limiter()  # set allowed polo.plots
                
                logger.info('Opened run: {}'.format(self.current_run))
        except Exception as e:
            logger.error('Caught {} calling {}'.format(e, self._handle_opening_run))
            make_message_box(parent=self,
                            message='Could not open current run. Failed {}'.format(e)
                            ).exec_()
            # enable nav by time if has linked runs
    
    # Menu handling methods
    # ======================================================================


    def _handle_tool_menu(self, selection):
        '''Private method that handles selection of 
        all options available to the user in 
        the `Tools` section of the main window menu.

        :param selection: User's menu selection
        :type selection: QAction
        '''
        try:
            if selection == self.actionView_Log_2:
                log_dialog = LogDialog(parent=self)
                log_dialog.exec_()
            elif selection == self.actionEdit_Current_Run_Data:
                if self.current_run:
                    updater_dialog = RunUpdaterDialog(
                        self.current_run,
                        self.runOrganizer.ui.runTree.current_run_names)
                    updater_dialog.exec_()
                else:
                    make_message_box(
                        parent=self,
                        message='Please load a run first.').exec_()
            elif selection == self.actionDelete_Classification_Backups:
                self._handle_delete_backups()
        except Exception as e:
            logger.error('Caught {} at {}'.format(e, self._handle_tool_menu))
            make_message_box(
                parent=self,
                message='Failed to execute {} {}'.format(selection.text(), e)
            ).exec_()

    def _handle_delete_backups(self):
        '''Private method that handles a user request to delete all backup 
        mso files. If backups cannot be deleted shows a message box indicating
        failure to delete.
        '''
        try:
            total_size = 0
            backups = list_dir_abs(str(BACKUP_DIR))
            if backups:
                total_size = sum([os.path.getsize(str(f)) for f in backups])
            
            choice = make_message_box(
                parent=self,
                message='You have {} Mb of backups. Would you like to delete these files?'.format(
                    total_size * 1e-6),
                buttons=QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
                ).exec_()
            if choice == QtWidgets.QMessageBox.Yes:
                are_you_sure = make_message_box(
                    parent=self,
                    message='Are you sure? You will lose these files FOREVER!',
                    buttons=QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
                ).exec_()
                if are_you_sure == QtWidgets.QMessageBox.Yes:
                    MainWindow.delete_all_backups()
                    make_message_box(parent=self,
                    message='Backups have been deleted.').exec_()
        except Exception as e:
            logger.error('Caught {} while calling {}'.format(
                            e, self._handle_delete_backups))
            make_message_box(
                parent=self,
                message='Could not delete backups. Failed {}.\
                    They can be deleted manually at {}'.format(e, BACKUP_DIR)
            ).exec_()

    def _handle_image_import(self, selection):
        '''Private method that handles when the user attempts to import images into Polo. 
        Effectively a wrapper around other methods that provide the functionality to
        each option in the import menu.

        :param selection: QAction. QAction from user menu selection.
        '''
        try:
            if selection == self.actionFrom_FTP:
                self.runOrganizer.import_run_from_ftp()
            elif selection == self.actionFrom_Saved_Run_3:
                self.runOrganizer.import_saved_runs()
            elif selection == self.actionFrom_Directory:
                self.runOrganizer.import_run_from_dialog()
            elif selection == self.actionCocktails:
                pass
        except Exception as e:
            logger.error('Caught {} at {}'.format(e, self._handle_image_import))
            make_message_box(
                parent=self,
                message='Failed to execute {} {}'.format(selection.text(), e)
            ).exec_()

    def _handle_export(self, action, export_path=None):
        '''Private method to handle when a user requests to export a run
        to a non-xtal file format.

        :param action: QAction that describes the export type the user has requested
        :type action: QAction
        :param export_path: Path to export file to, defaults to None
        :type export_path: str or Path, optional
        '''
        if self.current_run:        
            if action != self.actionAs_PPTX:
                if not export_path:
                    export_path = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Run')[0]

                if export_path:
                    export_path, export_results = Path(export_path), None
                
                    if action == self.actionAs_HTML:
                        writer = HtmlWriter(self.current_run)
                        QApplication.setOverrideCursor(Qt.WaitCursor)
                        self.setEnabled(False)
                        export_results = writer.write_complete_run(
                            export_path, encode_images=True)

                    elif action == self.actionAs_CSV:
                        export_path = export_path.with_suffix('.csv')
                        csv_exporter = RunCsvWriter(self.current_run, export_path)
                        export_results = csv_exporter.write_csv()

                    elif action == self.actionAs_MSO:
                        writer = MsoWriter(self.current_run, export_path)
                        export_results = writer.write_mso_file()
                    
                    elif action == self.actionAs_JSON:
                        writer = JsonWriter(self.current_run, export_path)
                        export_results = writer.write_json()

                    # check if need to show an error message
                    self.setEnabled(True)
                    QApplication.restoreOverrideCursor()
                    if export_results != True and export_results != None:
                        make_message_box(
                            message='Export failed', parent=self
                        ).exec_()
            else:
                presentation_maker = PptxDesignerDialog(
                    self.runOrganizer.ui.runTree.loaded_runs)
                presentation_maker.exec_()
        else:
            make_message_box(
                parent=self,
                message='Please load a run first'
                ).exec_()

    def _handle_file_menu(self, selection):
        '''Private method that handles user interaction with the file menu;
        this usually means saving a run as an xtal file.

        :param selection: QAction that describes user selection
        :type selection: QAction
        '''
        try:
            save_path = None
            if self.current_run:
                current_run_saver = XtalWriter(self.current_run, self)
                if selection == self.actionSave_Run:
                    sp = self.current_run.save_file_path
                    if sp and os.path.exists(sp):  # save run path already exist
                        save_path = sp
                elif selection == self.actionSave_Run_As or save_path == None:
                    save_path = self._save_file_dialog()

                if save_path:  # double check wonky stuff happening in save dialog
                    current_run_saver.write_xtal_file_on_thread(save_path)
                else:
                    make_message_box(
                        parent=self,
                        message='No suitable filepath was given.'
                        ).exec_()
        except Exception as e:
            logger.error('Caught {} at {}'.format(e, self._handle_file_menu))
            make_message_box(
                parent=self,
                message='Failed to execute {} {}'.format(selection.text(), e)
            )

    def _handle_help_menu(self, action):
        '''Private method that handles user interaction with the help menu. 
        All selections open links to various pages of the documentation website.

        :param action: QAction that describes the user's selection
        :type action: QAction
        '''
        try:
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
        except Exception as e:
            logger.error('Caught {} at {}'.format(e, self._handle_help_menu))
            make_message_box(
                parent=self,
                message='Failed to execute {} {}'.format(action.text(), e)
            )

    # Plot Window Methods
    # =========================================================================

    def _handle_plot_selection(self):
        '''Private method to handle user plot selections.

        TODO: Move all plot methods into their own widget
        '''
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
                    #self.matplotlib_widget.cocktail_distance_heatmap(self.current_run)
                    pass
    # allow or disallow access to ploting methods based on run object type
    def _plot_limiter(self):
        '''Private method to limit the types of plots that can be shown
        based on the type of the `current_run`.
        '''
        if self.current_run:
            self.listWidget_3.clear()
            self.listWidget_3.addItems(self.current_run.AllOWED_PLOTS)

    def _save_file_dialog(self):
        '''Private method to open a QFileDialog to get a location
        to save a run to.

        :return: Path to save file to
        :rtype: str
        '''
        file_name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Run')
        return file_name[0]

    def _on_changed_tab(self, i):
        '''Private method that handles GUI behavior when a user
        switches from one tab to another.

        :param i: Int. The index of the current tab, after user has changed tabs.
        '''
        i = int(i)  # make sure its actually an int
        if self.current_run:
            if i == 0:
                pass
                # self.new_slideshow_image_routine()
            elif i == 2:
                self._handle_plot_selection()  # refresh the current plot
            elif i == 5:  # run data editor
                self.current_run.annotations = self.plainTextEdit.toPlainText()
            elif i == 4:
                self.optimizeWidget.update()
    
    # other stuff



    # Depreciated Methods that just have too much sentimental value to delete
    # =========================================================================

    # def add_loaded_run(self, run):
    #     '''
    #     Add a run object to the loaded_runs attribute and add the run name to
    #     the available runs listWidget so the user may select this run for
    #     viewing. After this function call the run will be recoverable using
    #     its run name as a key in the loaded_runs dictionary.

    #     :param run: Run Object. New run to make available to the user.
    #     '''
    #     self.loaded_runs[run.run_name] = run
    #     item = QtWidgets.QListWidgetItem(self.listWidget)
    #     item.setText(run.run_name)
    #     # self.listWidget.addItem(item)
    #     logging.info('Loaded run named {}'.format(run.run_name))

    # def open_run_import_dialog(self):
    #     '''
    #     Creates an instance of the RunImporterDialog class and displays
    #     that dialog. After the instance is closed by the user checks to see
    #     if a new run has been created and stored in the new_run attribute of
    #     the RunImporterDialog instance. If one is present makes it available
    #     to the user by passing contents of new_run to add_loaded_run.
    #     '''
    #     importer_dialog = RunImporterDialog(
    #         current_run_names=list(self.loaded_runs.keys()))
    #     importer_dialog.exec_()
    #     if importer_dialog.new_run != None:
    #         self.add_loaded_run(importer_dialog.new_run)
    #         logging.info('Added run successfully')
    #     else:
    #         logging.info('Attempted to open empty run at {}'.format(
    #             self.open_run_import_dialog))
    # def get_current_plot_selections(self):
    #     return {
    #         'type': self.comboBox.currentText(),
    #         'x_axis': self.comboBox_2.currentText(),
    #         'y_axis': self.comboBox_3.currentText()
    #     }

    # def get_current_plot_labels(self):
    #     return {
    #         'title': self.lineEdit_2.text(),
    #         'x_lab': self.lineEdit_3.text(),
    #         'y_lab': self.lineEdit_4.text()
    #     }

    # def apply_plot_selection_logic(self):
    #     BAR_X_VARS = ['Human Classification', 'MARCO Classicication',
    #                   '']
    #     BAR_Y_VARS = ['Number Images']
    #     VIOLIN_X_VARS = ['Human Classification', 'MARCO Classification']
    #     VIOLIN_Y_VARS = ['Cocktail pH', 'Number Images']

    #     # method for enableing and disabling selections based on other selections
    #     if self.comboBox.currentText() == 'Plate Heatmaps':
    #         self.comboBox_2.clear()
    #         self.comboBox_3.clear()
    #     elif self.comboBox.currentText() == 'Bar':
    #         self.clear_and_set_variable_boxes(BAR_X_VARS, BAR_Y_VARS)
    #     elif self.comboBox.currentText() == 'Violin':
    #         self.clear_and_set_variable_boxes(VIOLIN_X_VARS, VIOLIN_Y_VARS)

    #     self.set_default_plot_labels()

    # def set_default_plot_labels(self):
    #     # set title
    #     x_var = self.comboBox_2.currentText()
    #     y_var = self.comboBox_3.currentText()

    #     self.lineEdit_2.setText('{} vs. {}'.format(
    #         x_var, y_var
    #     ))
    #     self.lineEdit_3.setText(x_var)
    #     self.lineEdit_4.setText(y_var)

    # def clear_and_set_variable_boxes(self, x_vars, y_vars):
    #     '''
    #     Helper function for apply_plot_selection_logic that clears the
    #     two variable combo boxes and sets new values to the values
    #     contained in the x_vars and y_vars lists.
    #     '''
    #     self.comboBox_2.clear()
    #     self.comboBox_3.clear()
    #     self.comboBox_2.addItems(x_vars)
    #     self.comboBox_3.addItems(y_vars)

    # Dialog Windows (Open and Handle Methods)
    # =========================================================================

    # def open_run_updater_dialog(self):
    #     if self.current_run:
    #         run_updater = RunUpdaterDialog(self.current_run,
    #         list(self.loaded_runs.keys()), self)
    #     else:
    #         make_message_box(
    #             parent=self,
    #             message='Please load a run first.'
    #             ).exec_()
    
    # NOTE: Time link and spectrum dialogs not currently used
    # as runs are linked automatically as they are loaded in
    # Keep this code for now as may remake a manual linking interface
    # later

    # def open_spectra_dialog(self):
    #     spec_dialog = SpectrumDialog(loaded_runs=self.loaded_runs)
    #     self.load_runs = spec_dialog.loaded_runs
    #     if self.current_run and self.current_run.alt_spectrum:
    #         self.plateInspector.set_alt_spectrum_buttons(allow=True)
    #         self.slideshowInspector.set_alt_spectrum_buttons()
            # enable alt spectrum selections

    # def open_time_link_dialog(self):
    #     time_dialog = TimeResDialog(available_runs=self.loaded_runs)
    #     self.loaded_runs = time_dialog.available_runs
    #     if self.current_run:  # run is open
    #         self.current_run = self.loaded_runs[self.current_run.run_name]
    
    # NOTE: Advanced tools have been temporarily removed since all functionality
    # they included has been applied automatically. May be adding in manual
    # interfaces later.

    # def handle_advanced_tools(self, selection):
    #     if selection == self.actionTime_Resolved:
    #         self.open_time_link_dialog()
    #     elif selection == self.actionView_Log_2:
    #         self.open_log_dialog()
    #     elif selection == self.actionAdd_Image_Type:
    #         self.open_spectra_dialog()
    #     elif selection == self.actionEdit_Current_Run_Data:
    #         self.open_run_updater_dialog()

    # def open_file_dialog(self, dialog_type='Dir'):
    #     file_dlg = QtWidgets.QFileDialog()
    #     if dialog_type == 'Dir':
    #         file_dlg.setFileMode(QtWidgets.QFileDialog.Directory)
    #     filenames = ''
    #     if file_dlg.exec():
    #         filenames = file_dlg.selectedFiles()
    #         return filenames[0]
    #     else:
    #         return False

    # def open_log_dialog(self):
    #     log_dialog = LogDialog()