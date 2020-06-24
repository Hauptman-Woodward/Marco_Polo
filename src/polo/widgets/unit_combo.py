from PyQt5 import QtCore, QtGui, QtWidgets

from polo import ALLOWED_IMAGE_COUNTS, COLORS, IMAGE_CLASSIFICATIONS
from polo.crystallography.cocktail import SignedValue
from polo.crystallography.run import HWIRun, Run
from polo.designer.UI_unit_combo import Ui_unitCombo
from polo.utils.math_utils import *

# class Unit():

#     scalers = {'n': 1e-9, 'u': 1e-6, 'm': 1e-3, 'c': 1e-2}
#     base_units = {}  # stores all established base units update for the
#     # entire class
#     # SI unit scalers from the bae unit

#     def __init__(self, unit_string):
#         self.unit_string = unit_string


#     @classmethod
#     def add_base_unit(cls, new_unit):
#         if isinstance(new_unit, Unit):
#             cls.base_units[new_unit.unit_string] = new_unit


#     @property
#     def base_unit(self):
#         return self.__base_unit

#     @base_unit.setter
#     def base_unit(self, new_unit_string):
#         # first character of string should be scaler if string len > 1
#         if len(new_unit_string) > 1:
#             base_unit = new_unit_string[1:]
#         else:
#             base_unit = new_unit_string

#         if base_unit in self.base_units:
#             self.__base_unit = self.base_units[base_unit]


class UnitComboBox(QtWidgets.QWidget):

    saved_scalers = {'u': 1e-6, 'm': 1e-3, 'c': 1e-2}

    def __init__(self, parent=None, base_unit=None, scalers=[]):
        super(UnitComboBox, self).__init__(parent)
        self.ui = Ui_unitCombo()
        self.ui.setupUi(self)
        self.base_unit = base_unit
        self.scalers = scalers  # dict

    @property
    def scalers(self):
        return self.__scalers

    @scalers.setter
    def scalers(self, scaler_list):
        # units should be list of scaler prefixes if they are not predefined
        # in scalers then should be a tuple with first value the scaler char
        # and the second how it modifies the base unit
        if scaler_list == self.saved_scalers:
            self.__scalers = scaler_list
        else:
            scalers = {}
            for each_scaler in scaler_list:
                if isinstance(each_scaler, (tuple, list)):
                    if len(each_scaler) == 2:
                        scalers[each_scaler[0]] = each_scaler[1]
                    else:
                        continue
                elif each_scaler in self.saved_scalers:
                    scalers[each_scaler] = self.saved_scalers[each_scaler]
            self.__scalers = scalers
        if self.scalers:
            self.set_unit_combobox_text()

    @property
    def sorted_scalers(self):
        if self.scalers:
            return sorted(
                [s for s in self.scalers], key=lambda s: self.scalers[s])
        else:
            return []

    @property
    def unit_combobox_text(self):
        if self.scalers:
            scaler_text = ['{}{}'.format(s, str(self.base_unit)) for s in self.sorted_scalers]
            scaler_text.append(str(self.base_unit))
            return scaler_text
        else:
            return []

    def set_unit_combobox_text(self):
        items = self.unit_combobox_text
        if items:
            self.ui.comboBox.addItems(items)
            self.ui.comboBox.setCurrentIndex(len(items)-1)  # set t base unit
        return items

    def unit_text_parser(self, unit_text=None):
        if not unit_text:
            unit_text = self.ui.comboBox.currentText()
        if unit_text:
            if len(unit_text) > 1:
                return unit_text[0], unit_text[1:]
            else:
                return unit_text

    def get_value(self):
        # base == True means return value in reference to the base unit
        value = self.ui.doubleSpinBox.value()
        unit_text = self.ui.comboBox.currentText()

        return SignedValue(value, unit_text)
    
    def set_zero(self):
        self.ui.doubleSpinBox.setValue(0.0)
    
    def set_value(self, value, *args):
        if isinstance(value, SignedValue):
            self.ui.doubleSpinBox.setValue(value.value)
            unit_index = self.ui.comboBox.findText(value.units)
            self.ui.comboBox.setCurrentIndex(unit_index)
        else:
           self.set_zero()