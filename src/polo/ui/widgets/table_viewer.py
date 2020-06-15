from PyQt5 import QtCore, QtGui, QtWidgets
from polo import IMAGE_CLASSIFICATIONS, DEFAULT_TABLE_HEADERS
from polo.crystallography.image import Image
from polo.crystallography.cocktail import SignedValue 
from polo.crystallography.run import HWIRun, Run
from polo import IMAGE_CLASSIFICATIONS
from polo.utils.io_utils import write_screen_html

import math


class TableViewer(QtWidgets.QTableWidget):

    default_headers = DEFAULT_TABLE_HEADERS

    def __init__(self, parent, run=None):
        super(TableViewer, self).__init__(parent)
        self.run = run
        self.__current_data = []

    @classmethod
    def edit_default_headers(cls, header):
        pass

    @property
    def __num_rows(self):
        '''Returns number of rows based on len of __current_data'''
        return len(self.__current_data)

    @property
    def __num_cols(self):
        '''
        Returns number of columns based on len of first item in
        __current_data.
        '''
        try:
            return len(self.__current_data[0])
        except IndexError:
            return 0

    @property
    def cell_map(self):
        '''
        Maps the list of lists that should be contained in __current_data
        to a nested dictionary. Fist dictionary keys are the row indexes of
        each outer list in __current_data. The second dict's keys are the
        column indexes (index of object in a __current_data outer list).

        :rtype dict 
        '''
        # maps the list data in the __current_data
        # attribute to a nested dictionary accessible first by
        # row index and then column index
        cell_dict = {}
        for i in range(0, self.__num_rows):
            for j in range(0, self.__num_cols):
                cur_table_item = QtWidgets.QTableWidgetItem(
                    self.__current_data[i][j])
                if i in cell_dict:
                    cell_dict[i][j] = cur_table_item
                else:
                    cell_dict[i] = {j: cur_table_item}
        return cell_dict

    def populate_table(self):
        self.setColumnCount(self.__num_cols)
        self.setRowCount(self.__num_rows)
        cell_map = self.cell_map
        for row_index in cell_map:
            for col_index in cell_map[row_index]:
                self.setItem(row_index, col_index,
                             cell_map[row_index][col_index])

    def apply_sort(self, crystal_confidence=False, cocktail_number=False,
                   well_number=False):
        pass

    def set_current_data(self, image_types, human, marco):
        table_data = []
        images = self.run.image_filter_query(image_types, human, marco)
        table_data.append(self.default_headers)
        for image in images:
            image_dict = image.__dict__
            table_data.append([str(image_dict[h])
                               for h in self.default_headers])
        self.__current_data = table_data
        return table_data


class OptimizeScreen(QtWidgets.QTableWidget):

    UNITS = ['M', '(w/v)', '(v/v)']

    def __init__(self, parent, x_wells=None, y_wells=None, run=None,
                 x_step=None, y_step=None, well_volume=2e-6):
        super(OptimizeScreen, self).__init__(parent)
        self.x_wells = x_wells
        self.y_wells = y_wells
        self.x_step = x_step
        self.y_step = y_step
        self.run = run
        self.well_volume = well_volume
        self.__current_hit = None  # index of well number to populate with
        self.__x_reagent = None
        self.__y_reagent = None
        self.__header = self.horizontalHeader()
        self.__sider = self.verticalHeader()
        self.__header.setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeToContents)
        self.__sider.setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeToContents)

    @property
    def current_hit(self):
        return self.__current_hit

    @current_hit.setter
    def current_hit(self, new_hit):
        new_hit = int(new_hit) - 1
        if self.run:
            self.__current_hit = new_hit
    
    @property
    def constant_reagents(self):
        '''
        Returns any reagents in a set that are not either the x or y
        reagent. These reagents still need to be included in the screen but
        their values are not stepped along either plate axis.
        '''
        if self.__current_hit and self.__x_reagent and self.__y_reagent:
            return set(self.run.images[self.__current_hit].cocktail.reagents).difference(
                set([self.__x_reagent, self.__y_reagent])
            )
        else:
            return []
        # should return a reagent object

    @property
    def x_reagent(self):
        return self.__x_reagent

    @x_reagent.setter
    def x_reagent(self, reagent):  # set from a string in combobox
        if isinstance(reagent, str):
            reagent_index = int(reagent.split(':')[0].strip())
            self.__x_reagent = self.run.images[self.current_hit].cocktail.reagents[reagent_index]
        else:
            self.__x_reagent = None

    @property
    def y_reagent(self):
        return self.__y_reagent

    @y_reagent.setter
    def y_reagent(self, reagent):
        if isinstance(reagent, str):
            reagent_index = int(reagent.split(':')[0].strip())
            self.__y_reagent = self.run.images[self.current_hit].cocktail.reagents[reagent_index]
        else:
            self.__y_reagent = None

    @property
    def number_wells(self):
        return self.x_wells * self.y_wells

    @property
    def crystal_hits(self):
        if self.run:
            hits = []
            for i, image in enumerate(self.run.images):
                if image.human_class == IMAGE_CLASSIFICATIONS[0]:
                    hits.append(str(i+1))
            if hits:
                return hits
        return 'None'

    @property
    def reagents(self):  # return reagents mapped to current hit image
        if isinstance(self.current_hit, int) and self.run:
            cocktail = self.run.images[int(self.current_hit)].cocktail
            if cocktail:
                return cocktail.reagents
        return []

    def populate_table(self, write_prefix=None):
        if self.x_reagent and self.y_reagent:
            x_grad_stock, x_grad_con = (
                self.gradient(self.x_reagent, self.x_wells, self.x_step,stock=True),
                self.gradient(self.x_reagent, self.x_wells, self.x_step))
            y_grad_stock, y_grad_con = (
                self.gradient(self.y_reagent, self.y_wells, self.y_step, stock=True),
                self.gradient(self.y_reagent, self.y_wells, self.y_step)
            )
            self.setRowCount(len(x_grad_con))
            self.setColumnCount(len(y_grad_con))
            for i in range(0, len(x_grad_con)):
                for j in range(0, len(y_grad_con)):
                    x_string = self.format_well_string(
                        self.x_reagent.chemical_additive, x_grad_con[i], x_grad_stock[i]
                    )
                    y_string = self.format_well_string(
                        self.y_reagent.chemical_additive, y_grad_con[j], y_grad_stock[j]
                    )
                    cell_content = x_string + y_string
                    self.setCellWidget(i, j, cell_content)
    
    def setCellWidget(self, row, col, content):
        widget = QtWidgets.QTextBrowser(self)
        widget.setText(content)
        super(OptimizeScreen, self).setCellWidget(row, col, widget)

    def format_well_string(self, reagent_name, concentration, stock_volume):
        return '<h4>{} {}</h4>\n{} of stock'.format(
            concentration, reagent_name, stock_volume
        )

    def gradient(self, reagent, num_wells, step, stock=False):
        if stock and reagent.stock_volume(self.well_volume):  # TODO change well volume to signed value
            c = reagent.stock_volume(self.well_volume)
        else:
            c = reagent.concentration  # already a signed value
        m = math.floor(num_wells / 2)
        s = float(c) * step
        return [SignedValue((c.value + (s * (n-m))), c.unit) for n in range(
            1, num_wells+1)]  # return a list of signed values


    def write_current_screen_html(self, output_path):
        plate = []
        for i in range(self.rowCount()):
            plate.append([])
            for j in range(self.columnCount()):
                plate[i].append(self.cellWidget(i, j).toHtml())
        
        x_stock = '{} stock concentration {}'.format(self.x_reagent.chemical_additive,
        self.x_reagent.stock_con)
        y_stock = '{} stock concentration {}'.format(self.y_reagent.chemical_additive,
        self.y_reagent.stock_con)
        write_screen_html(plate, self.current_hit+1, self.run.run_name, x_stock,
                          y_stock, self.well_volume, output_path)
