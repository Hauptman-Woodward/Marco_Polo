from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QBrush, QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QGridLayout

from polo import make_default_logger
from polo.crystallography.run import HWIRun, Run
from polo.designer.UI_spectrum_dialog import Ui_Dialog
from polo.utils.ftp_utils import logon

logger = make_default_logger(__name__)

# TODO: Downloading function and reflect files in the actual FTP server
# Probably want to look into threads for downloading so not being done on
# the GUI thread

class SpectrumDialog(QtWidgets.QDialog):
    '''Small dialog used to link runs together by image spectrum. This is
    generally done when the same plate has been imaged using different
    photographic technologies. Linking the runs together allows the user to
    switch between the images in either run easily.

    :param loaded_runs: List of runs that have been loaded into Polo
    :type loaded_runs: list
    '''

    def __init__(self, loaded_runs):

        QtWidgets.QDialog.__init__(self)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.loaded_runs = loaded_runs
        self.suggested_links = None
        self.current_suggestion = None

        self.ui.pushButton_3.clicked.connect(self.display_suggestion)
        self.ui.pushButton_2.clicked.connect(self.close)
        self.ui.pushButton.clicked.connect(self.link_current_selection)

        self.populate_list_widgets()
        self.suggest_links()
        logger.debug('Opened {}'.format(self))
        self.exec_()

    def populate_list_widgets(self):
        '''Adds items to each image spectrum type list widget based on the
        Run objects stored in the `loaded_runs` attribute. 
        '''
        for run_name, run in self.loaded_runs.items():
            if type(run) == HWIRun:
                if run.image_spectrum == 'Visible':
                    self.ui.listWidget.addItem(run_name)
                elif run.image_spectrum == 'UV-TPEF':
                    self.ui.listWidget_2.addItem(run_name)
                elif run.image_spectrum == 'SHG':
                    self.ui.listWidget_3.addItem(run_name)
                else:
                    self.ui.listWidget_4.addItem(run_name)

    def suggest_links(self):
        '''Suggest runs to link together based on their imaging dates. A link
        suggestion will be made if the images were taken on the same day but the
        runs are labeled as different image types.

        :return: Suggested links as list of tuples, each tuple containing two
                 runs that are suggested for linking.
        :rtype: list
        '''
        # suggest links based on dates of runs and spectrums
        runs = sorted([run for _, run in self.loaded_runs.items()],
                      key=lambda x: x.date)
        links = []
        for i in range(len(runs)-1):
            run_a, run_b = runs[i], runs[i+1]
            if run_a.date.date == run_b.date.date and run_a.image_spectrum != run_b.image_spectrum:
                links.append((run_a, run_b))
        self.suggested_links = links
        logger.debug('Suggested run spectrum links')
        return links

    def display_suggestion(self):
        '''Show the link suggestion to the user by selecting suggested links.
        '''
        if self.suggested_links:
            self.current_suggestion = self.suggested_links.pop()
            for run in self.current_suggestion:
                spectrum_list_widget = self.get_spectrum_list(run)
                spectrum_list_widget.setCurrentItem(run.run_name)

    def link_current_selection(self):
        '''Link the currently selected runs together. Creates a circular
        linked list structure.
        '''
        selected_runs = self.get_selections()
        if self.validate_selection(selected_runs):
            for i in range(len(selected_runs)-1):
                run_a, run_b = (
                    self.loaded_runs[selected_runs[i]],
                    self.loaded_runs[selected_runs[i+1]]
                )
                run_a.link_to_alt_spectrum(run_b)
            first_run, last_run = (
                self.loaded_runs[selected_runs[0]],
                self.loaded_runs[selected_runs[-1]])
            last_run.link_to_alt_spectrum(first_run)
            message = ''
            for run in selected_runs:
                message += run + ' '
            message += 'have been linked as alternative spectrums successfully.'

            self.show_error_message(message=message)
        else:
            logger.warning('Link validation failed for {}'.format(selected_runs))

    def show_error_message(self, message=':('):
        '''
        Helper method for showing a QErrorMessage dialog to the user.

        :param message: String. The message text to show to the user.
        '''
        err = QtWidgets.QErrorMessage(parent=self)
        err.showMessage(message)
        err.exec()

    def validate_selection(self, selected_runs):
        if len(selected_runs) < 2:
            self.show_error_message('At least 2 runs must be selected')
            return False
        return True

        # TODO add warning messages when dates are not the
        # same and suggest using the other linker for
        # time resolved runs

    def get_selections(self):
        '''Retrieve the runs that have been selected by the user or by
        suggestion.

        :return: list of selected run names
        :rtype: list
        '''
        selections = []
        list_widgets = [
            self.ui.listWidget, self.ui.listWidget_2,
            self.ui.listWidget_3, self.ui.listWidget_4
        ]
        for widget in list_widgets:
            if widget.currentItem():
                selections.append(widget.currentItem().text())
        return selections

    def get_spectrum_list(self, run):
        '''Returns the listwidget that a run should be assigned to based
        on the run's image type.

        :param run: Run object to assign to a listWidget
        :type run: Run
        :return: QListWidget to place that run into
        :rtype: QListWidget
        '''
        if run.image_spectrum == 'Visible':
            return self.ui.listWidget
        elif run.image_spectrum == 'UV-TPEF':
            return self.ui.listWidget_2
        elif run.image_spectrum == 'SHG':
            return self.ui.listWidget_3
        else:
            return self.ui.listWidget_4
