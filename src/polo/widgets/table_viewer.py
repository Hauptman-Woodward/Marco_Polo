import math

from PyQt5 import QtCore, QtGui, QtWidgets

from polo import IMAGE_CLASSIFICATIONS
from polo.crystallography.cocktail import UnitValue
from polo.crystallography.image import Image
from polo.crystallography.run import HWIRun, Run
from polo.utils.io_utils import RunCsvWriter, write_screen_html
from polo import make_default_logger


logger = make_default_logger(__name__)

class TableViewer(QtWidgets.QTableWidget):

    def __init__(self, parent, run=None):
        '''TableViewer instances override QTableWidget and provide a
        more convenient interface for translating the data in Run objects
        into a table format.

        :param parent: Parent widget
        :type parent: QtWidget
        :param run: Run to show in this table view, defaults to None
        :type run: Run, optional
        '''
        super(TableViewer, self).__init__(parent)
        self.run = run
        self.selected_headers = None

    @property
    def run(self):
        '''Return the run object

        :return: Run object
        :rtype: Run
        '''
        return self.__run

    @run.setter
    def run(self, new_run):
        '''Setter function for run attribute    

        :param new_run: New run to set as run attribute
        :type new_run: Run
        '''
        self.__run = new_run

    @property
    def table_data(self):
        '''Property to retrieve the current table fieldnames and table data
        using `get_csv_data` function of the RunCsvWriter class

        :return: fieldnames, table data
        :rtype: tuple
        '''
        if self.run:
            try:
                return RunCsvWriter(self.run).get_csv_data()
            except Exception as e :
                logger.error('Caught {} at trying to get table'.format(e))
                print(e)
                return [], {}  # empty list and dict need to handle better
                # down the line

    @property
    def fieldnames(self):
        '''Return just the fieldnames for the current run. Should only be
        used when setting the values for the listWidget in a tableInspector
        instance

        :return: list of fieldnames
        :rtype: list
        '''
        if self.run:  # expensive avoid using
            return self.table_data[0]

    @staticmethod
    def filter(row, image_classes, human, marco):
        '''Helper method to determine if a row should be included based on
        the image filters the user has selected

        :param row: row data
        :type row: dict
        :param image_classes: types of images to include, i.e Crystals, Clear
        :type image_classes: set or list
        :param human: If image_classes should be in reference to human classifier
        :type human: Bool
        :param marco: If image_classes should be in reference to machine classifier
        :type marco: Bool
        :return: If image should be filtered, False means do not filter image
        :rtype: Bool
        '''
        if not image_classes:
            image_classes = IMAGE_CLASSIFICATIONS

        # BUG / TODO
        # Properties of image class are being shown with underscores when read
        # from the class __dict__ temp fix for now is to just set the key to
        # include the __ and class name but need more robust less jank way
        # to do this for any given attribute
        human_key = '_human_class'
        if human_key not in row: human_key = 'human_class'
        machine_key = 'machine_class'
        if machine_key not in row: machine_key = '_machine_class'
        if human and row[human_key] in image_classes:
            return False
        if marco and row[machine_key] in image_classes:
            return False

        return True

    def make_header_map(self, headers):
        '''Helper method to map header keywords to their index (order). Need
        because headers come as a set and need to keep the order consistent.

        :param headers: set of headers strings
        :type headers: set
        :return: dictionary of header strings mapped to indices
        :rtype: dict
        '''
        return {h: i for i, h in enumerate(sorted(self.selected_headers))}

    def populate_table(self, image_classes, human, marco):
        '''Populates the table and displays data to the user based on their
        header and image filtering selections.

        :param image_classes: types of images to include, i.e Crystals, Clear
        :type image_classes: set or list
        :param human: If image_classes should be in reference to human classifier
        :type human: Bool
        :param marco: If image_classes should be in reference to machine classifier
        :type marco: Bool
        :return: If image should be filtered, False means do not filter image
        '''
        if self.run:
            self.clear()
            headers, data = self.table_data
            header_map = self.make_header_map(headers)
            header_labels = sorted(
                [h for h in header_map.keys()], key=lambda k: header_map[k])
            self.setHorizontalHeaderLabels(header_labels)
            table_data, row_count = {}, 0
            for row in data:  # dictionary
                if TableViewer.filter(row, image_classes, human, marco):
                    continue
                for col_name, col_value in row.items():
                    if col_name in header_map:
                        col_index = header_map[col_name]
                        table_data[(row_count, col_index)] = col_value
                row_count += 1

            self.setColumnCount(len(header_map))
            self.setRowCount(row_count)

            for k, v in table_data.items():
                r, c = k
                self.setItem(r, c, QtWidgets.QTableWidgetItem(v))
