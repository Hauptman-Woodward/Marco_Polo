import math

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBitmap, QBrush, QColor, QIcon, QPainter, QPixmap
from PyQt5.QtWidgets import QGraphicsColorizeEffect, QGraphicsScene

from polo import DEFAULT_TABLE_HEADERS, ICON_DICT, IMAGE_CLASSIFICATIONS
from polo.crystallography.cocktail import SignedValue
from polo.crystallography.image import Image
from polo.crystallography.run import HWIRun, Run
from polo.ui.designer.UI_optimizeWidget import Ui_Form
from polo.utils.io_utils import write_screen_html


class OptimizeWidget(QtWidgets.QWidget):

    HTML_ICON = str(ICON_DICT['html'])
    GRID_ICON = str(ICON_DICT['grid'])

    def __init__(self, parent, run=None):
        super(OptimizeWidget, self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.__run = run
        self.__current_reagents = None
        self.ui.comboBox_12.currentTextChanged.connect(
            self.update_current_reagents
        )
        self.ui.doubleSpinBox_6.valueChanged.connect(
            lambda x: self.change_reagent_stock_con(x, self.y_reagent)
        )
        self.ui.doubleSpinBox.valueChanged.connect(
            lambda x: self.change_reagent_stock_con(x, self.x_reagent)
        )
        self.ui.comboBox_6.currentTextChanged.connect(
            self.set_reagent_stock_con
        )
        self.ui.comboBox_13.currentTextChanged.connect(
            self.set_reagent_stock_con
        )
        self.ui.doubleSpinBox_7.valueChanged.connect(
            self.change_constant_reagent_stock_con
        )
        self.ui.listWidget_4.currentTextChanged.connect(
            self.set_constant_reagent_stock_con
        )
        self.ui.pushButton_27.clicked.connect(self.write_optimization_screen)
        self.ui.pushButton_26.clicked.connect(self.export_screen)
        self.__header = self.ui.tableWidget.horizontalHeader()
        self.__sider = self.ui.tableWidget.verticalHeader()
        self.__header.setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeToContents)
        self.__sider.setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeToContents)

        self.ui.pushButton_26.setIcon(QIcon(self.HTML_ICON))
        self.ui.pushButton_27.setIcon(QIcon(self.GRID_ICON))

    @property
    def x_wells(self):
        '''Returns spinBox value that is to be interpreted as number x wells'''
        return self.ui.spinBox_2.value()

    @property
    def y_wells(self):
        '''Returns spinBox value that is number of y wells'''
        return self.ui.spinBox_3.value()

    @property
    def x_reagent(self):
        '''
        Used to retrieve the Reagent object that is to be varied along
        the x axis of the optimization plate.
        '''
        reagent_text = self.ui.comboBox_6.currentText()
        if reagent_text and reagent_text in self.__current_reagents:
            return self.__current_reagents[reagent_text]
        else:
            return None

    @property
    def y_reagent(self):
        '''
        Used to retreive the Reagent object that is to be varied along
        the y axis of the optimization plate
        '''
        reagent_text = self.ui.comboBox_13.currentText()
        if reagent_text and reagent_text in self.__current_reagents:
            return self.__current_reagents[reagent_text]

    @property
    def constant_reagents(self):
        '''
        Retrieved a set of reagents that are not included as either the
        x reagent of the y reagent but are still part of the crystallization
        cocktail and therefore need to be included in the screen. Unlike
        either the x or y reagents, constant reagents do not change their
        concentration across the screening plate.
        '''
        x, y = self.x_reagent, self.y_reagent
        if x and y:
            v = set([x, y])
            a = set(list(self.__current_reagents.values()))
            return a - v

    @property
    def well_volume(self):
        '''
        Returns the well volume set by the user modifed by whatever well
        volume unit is currently selected.
        '''
        v = self.ui.spinBox_4.value()
        if self.ui.comboBox_11.currentText() == 'ul':
            v *= 1e-6
        elif self.ui.comboBox_11.currentText() == 'ml':
            v *= 1e-3
        return SignedValue(v, 'L')  # always return in liters

    @property
    def hit_images(self):
        '''
        Retrieves a list of Image object instances that have the human
        classification (human_class attribute) of Crystals. Used to
        determine what wells to allow the user to optimize. Currently, only
        allow the user to optimize wells that they have marked as crystal.
        '''
        hits = []
        if isinstance(self.run, (Run, HWIRun)):
            for image in self.run.images:
                if image.human_class == IMAGE_CLASSIFICATIONS[0]:
                    hits.append(image)
        return hits

    @property
    def x_step(self):
        '''
        Retrieves the x_step divided by 100. Determines the percent
        variance between x_reagent wells.
        '''
        return self.ui.doubleSpinBox_4.value() / 100

    @property
    def y_step(self):
        '''
        Retrieves the y_step divided by 100. Determines the percent
        variance between y_reagent wells.
        '''
        return self.ui.doubleSpinBox_5.value() / 100

    @property
    def run(self):
        return self.__run

    @run.setter
    def run(self, new_run):
        '''
        Setter method for the __run attribute. Also sets the hit well choices
        and updates the current reagents that are selectable by the user.
        '''
        self.__run = new_run
        if isinstance(new_run, (Run, HWIRun)):
            self.set_hit_well_choices()  # give use options of crystal hits
            self.update_current_reagents()

    def update(self):
        '''
        Method to update reagents and wells selectable to the user after
        they have made additional classifications that would increase or
        decrease the pool of crystal classified images.
        '''
        self.set_hit_well_choices()  # set wells to pick from
        self.ui.comboBox_12.setCurrentIndex(0)
        # set the current index in order to update the reagent choices
        self.set_constant_reagents()

    def set_hit_well_choices(self):
        '''
        Sets the hit well comboBox widget choices based on the images
        in the __run attribute that are human classified as crystal.
        '''
        if isinstance(self.run, (Run, HWIRun)):
            hits = self.hit_images
            if hits:
                self.ui.comboBox_12.clear()
                self.ui.comboBox_12.addItems(
                    [str(image.well_number) for image in hits]
                )
        # sets options to well numbers of hits

    def update_current_reagents(self, image_index=None):
        '''
        Updates x and y comboBox widgets to show what reagents are contained
        in the currently selected well.
        '''
        if self.run and image_index:
            image_index = int(image_index) - 1
            self.__current_reagents = {
                str(r): r for r in self.run.images[image_index].cocktail.reagents}
            self.set_reagent_choices()  # change whats listed in combo boxes

    def set_constant_reagents(self):
        '''
        Method that populates the listWidget with constant reagents to display
        to the user.
        '''
        constants = self.constant_reagents
        self.ui.listWidget_4.clear()
        if constants:
            items = [str(r) for r in constants]
            self.ui.listWidget_4.addItems(items)
            self.ui.listWidget_4.setCurrentRow(0)

    def change_constant_reagent_stock_con(self, value):
        '''Changes the stock concentration of the currently selected
        constant reagent to the concentration of the doublespinbox widget
        associated with the constant reagents tab.

        :param value: new concentration in mols / liter
        :type value: float
        '''
        if value and self.ui.listWidget_4.currentItem():
            selected_reagent = self.ui.listWidget_4.currentItem().text()
            if selected_reagent:
                selected_reagent = self.__current_reagents[selected_reagent]
                selected_reagent.stock_con = SignedValue(
                    self.ui.doubleSpinBox_7.value(), 'M'
                )

    def set_constant_reagent_stock_con(self):
        '''Display the currently selected constant reagent's stock
        concentration in the constant reagent double spin box widget.
        '''
        current_reagent = self.ui.listWidget_4.currentItem()
        if current_reagent and current_reagent.text():
            current_reagent = self.__current_reagents[current_reagent.text()]
            if current_reagent.stock_con:
                self.ui.doubleSpinBox_7.setValue(
                    current_reagent.stock_con.value)
            else:
                self.ui.doubleSpinBox_7.setValue(0.0)

    def set_reagent_choices(self):
        '''Set reagent choices for the x and y reagents based on the currently
        selected well. Reagents must come from the cocktail associated with
        the selected well.

        TODO: Add the option to vary pH instead of a reagent along either
        axis. This would also mean that the constant reagents would need to
        be updated.
        '''
        # assumes current reagents have already been set
        if self.__current_reagents:
            self.ui.comboBox_6.clear()
            self.ui.comboBox_13.clear()
            for reagent in self.__current_reagents:
                self.ui.comboBox_6.addItem(str(reagent))
                self.ui.comboBox_13.addItem(str(reagent))
            # self.ui.comboBox_6.addItem('pH') TODO allow user to varry pH instead of reagents
            # self.ui.comboBox_6.addItem('pH')
            self.ui.comboBox_6.setCurrentIndex(0)
            self.ui.comboBox_13.setCurrentIndex(len(self.__current_reagents)-1)

    def set_reagent_stock_con(self):
        '''Sets the value of either the x or y reagent concentration double
        spin box to the value for its respective reagent stock concentration.
        This method is how we show the user what the current stock concentration
        of a selected reagent is.
        '''
        if self.x_reagent and self.x_reagent.stock_con:
            self.ui.doubleSpinBox.setValue(self.x_reagent.stock_con.value)
        else:
            self.ui.doubleSpinBox.setValue(0.0)
        if self.y_reagent and self.y_reagent.stock_con:
            self.ui.doubleSpinBox_6.setValue(self.y_reagent.stock_con.value)
        else:
            self.ui.doubleSpinBox_6.setValue(0.0)
        self.set_constant_reagents()

    def change_reagent_stock_con(self, value, reagent):
        '''Change the stock concentration of a give reagent to a new value.
        TODO: Support more units besides molarity.

        :param value: The new concentration in mols / liter
        :type value: float  
        :param reagent: The reagent who's stock con is being changed 
        :type reagent: Reagent
        '''
        if value and reagent:
            reagent.stock_con = SignedValue(value, 'M')

    def gradient(self, reagent, num_wells, step, stock=False):
        '''Use this method for varying the concentration of a given
        reagent along either the x or y axis of the optimization plate. The
        gradient of concentrations are always centered around the hit
        concentration for the reagent being varied.

        :param reagent: Reagent to vary concentration
        :type reagent: Reagent
        :param num_wells: Number of wells to vary concentration across
        :type num_wells: int
        :param step: Proportion of hit concentration to vary each well by
        :type step: float < 1
        :param stock: If True, vary the stock volume not the hit \
            concentration unit, defaults to False
        :type stock: bool, optional
        :return: List of SignedValues that make up the gradient
        :rtype: list
        '''
        if stock and reagent.stock_volume(self.well_volume):
            c = reagent.stock_volume(self.well_volume)
        else:
            c = reagent.concentration
        m = math.floor(num_wells / 2)
        s = float(c) * step
        return [SignedValue((c.value + (s * (n-m))), c.units) for n in range(
            1, num_wells+1)]  # return a list of signed values

    def write_optimization_screen(self):
        '''Method to call to write the current to the table widget for display
        to the user.
        '''
        if self.error_checker():
            x_grad_stock, x_grad_con = (
                self.gradient(self.x_reagent, self.x_wells,
                              self.x_step, stock=True),
                self.gradient(self.x_reagent, self.x_wells, self.x_step))
            y_grad_stock, y_grad_con = (
                self.gradient(self.y_reagent, self.y_wells,
                              self.y_step, stock=True),
                self.gradient(self.y_reagent, self.y_wells, self.y_step)
            )
            constants = []
            for c in self.constant_reagents:
                stock_vol = c.stock_volume(self.well_volume)
                if not stock_vol:
                    stock_vol = c.concentration
                constants.append((c.chemical_additive,
                                  c.concentration, stock_vol))

            self.ui.tableWidget.setRowCount(len(y_grad_con))
            self.ui.tableWidget.setColumnCount(len(x_grad_con))
            # x is column y is row
            breaker = False
            for i in range(0, len(y_grad_con)):
                for j in range(0, len(x_grad_con)):
                    volume_list = [x_grad_stock[j],
                                   y_grad_stock[i]] + [c[-1] for c in constants]
                    # pull out the concentrations from constant tuples
                    water_volume = self.check_for_overflow(volume_list)
                    if water_volume:  # well does not overflow
                        well_string = self.make_well_html(
                            x_grad_con[j], x_grad_stock[j], y_grad_con[i],
                            y_grad_stock[i], constants, water_volume)
                        widget = QtWidgets.QTextBrowser(self)
                        widget.setText(well_string)
                        self.ui.tableWidget.setCellWidget(i, j, widget)
                    else:  # well overflows
                        msg = QtWidgets.QMessageBox()
                        msg.setIcon(QtWidgets.QMessageBox.Warning)
                        msg.setText('Well Overflow Error! Try increasing \
                            your stock concentrations or using a higher well volume.')
                        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                        msg.exec_()
                        self.ui.tableWidget.clear()
                        breaker = True
                        break
                if breaker:
                    break

    def adjust_unit(self, signed_value, new_unit):
        if signed_value.units == 'L':  # only convert volume for now
            if new_unit == 'ul':
                return signed_value.micro
            elif new_unit == 'ml':
                return signed_value.milli
            else:
                return signed_value
        else:
            return signed_value

    def make_well_html(self, x_con, x_stock, y_con, y_stock, constants, water):
        '''Format the information that describes the contents of an
        individual well into nice html that can be displayed to the user
        in a textBrowser widget.

        :param x_con: Concentration of x reagent in this well
        :type x_con: SignedValue
        :param x_stock: Volume of x reagent stock in this well
        :type x_stock: SignedValue
        :param y_con: Concentration of y reagent in this well
        :type y_con: SignedValue
        :param y_stock: Volume of y reagent stock in this well
        :type y_stock: SignedValue
        :param constants: Tuples of constant reagents to be included in each well
        :type constants: list of tuples
        :param water: Volume of water to be added to this well
        :type water: Signed Value
        :return: Html string to be rendered to the user
        :rtype: str
        '''
        write_unit = self.ui.comboBox_16.currentText()
        print(write_unit)
        print(x_stock, y_stock, 'stock values before write')
        template, s = '<h4>{} {}</h4>\n{} of stock\n', ''
        s += template.format(self.x_reagent.chemical_additive, x_con, self.adjust_unit(x_stock, write_unit))
        s += template.format(self.y_reagent.chemical_additive, y_con, self.adjust_unit(y_stock, write_unit))
        for c in constants:
            a, b, d = c
            s += template.format(a, b, self.adjust_unit(d, write_unit))  # rename this so it makes sense
        s += '<h4>Volume of H20</h4>\n{}'.format(self.adjust_unit(water, write_unit))
        return s

    def error_checker(self):
        '''
        Check if all widgets and attributes have allowed values before
        calculating the actual grid screen. Show error message if there is
        a conflict.
        '''
        error, message = False, ''
        if self.well_volume.value <= 0:
            error, message = True, 'Please set well volume > 0.'
        elif self.x_wells == 0 or self.y_wells == 0:
            error, message = True, 'Please set well dimensions > 0'
        elif not self.x_reagent or not self.y_reagent:
            error, message = True, 'Please select x and y reagents'
        elif not self.x_reagent.stock_con or not self.y_reagent.stock_con:
            error, message = True, 'Please set stock concentrations for all reagents including constants'
        if error:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText(message)
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()
            return False
        else:
            return True

    def make_plate_list(self):
        '''Converts the concents of the tablewidget (assuming that a optimization
        screen has been already rendered to the user) to a list of lists that
        is easier to write to html using the jinja2 template.

        :return: tableWidget contents converted to list
        :rtype: list
        '''
        plate_list = []
        for i in range(0, self.ui.tableWidget.rowCount()):
            plate_list.append([])
            for j in range(0, self.ui.tableWidget.columnCount()):
                plate_list[i].append(
                    self.ui.tableWidget.cellWidget(i, j).toHtml())
        return plate_list

    def export_screen(self):
        '''
        Write the screen to html.
        '''
        if self.__run and self.error_checker():
            export_path = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Screen')[
                0]
            if export_path:
                well_number = self.ui.comboBox_12.currentText()
                run_name = self.__run.run_name
                plate_list = self.make_plate_list()
                write_screen_html(plate_list, well_number, run_name,
                                  self.x_reagent, self.y_reagent, self.well_volume, export_path)

    def check_for_overflow(self, volume_list):
        ''' Check to see if the volume of reagents in a given well exceeds
        the well volume.

        :param volume_list: List of SignedValues that make up all contents \
            of a given well. Currently assumes units are all liters. 
        :type volume_list: list
        :return: True if the sum of the values of volume_list are less than\
            the current well volume, False otherwise.
        :rtype: Bool
        '''
        # args should be volumes as signed value of all stuff
        max_volume, total_volume = self.well_volume, 0
        for value in volume_list:
            if isinstance(value, SignedValue):
                if value.units == 'L':
                    total_volume += value.value
                elif value.units == 'w/v':
                    pass
                    # some kind of warning here about could not convert
                    # weight volume
                elif value.units == 'v/v':
                    total_volume += max_volume.value * (value.value/100)
        if total_volume > max_volume.value:
            return False
        else:
            # does fit in the well
            return SignedValue(max_volume.value - total_volume, 'L')
            # return the value of water that should be included in the well in
            # liters
