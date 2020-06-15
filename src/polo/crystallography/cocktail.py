from polo.utils.exceptions import NotASolutionError
from polo import water_regex
from molmass import Formula
import re

from polo import num_regex, unit_regex, water_regex, peg_regex


class Cocktail():

    def __init__(self, number=None, well_assignment=None,
                 commercial_code=None, pH=None, reagents=None):
        self.well_assignment = well_assignment
        self.number = number
        self.commercial_code = commercial_code
        self.pH = pH
        self.reagents = []

    @property
    def cocktail_index(self):
        return self.number.split('_C').lstrip('0')
        # normal cocktail number format 13_C0001
    
    @property
    def well_assignment(self):
        return self.__well_assignment
    
    @well_assignment.setter
    def well_assignment(self, value):
        if isinstance(value, (str, float)):
            value = int(value)
        self.__well_assignment = value
    
    def add_reagent(self, new_reagent):
        if new_reagent:
            self.reagents.append(new_reagent)

    def __repr__(self):
        return ''.join(sorted(['{}: {}\n'.format(key, value) for key, value in self.__dict__.items()]))

    def __str__(self):
        cocktail_string = 'Cocktail {}\n'.format(self.number)
        cocktail_string += '-'*len(cocktail_string)*2 + '\n\n'
        cocktail_string += 'pH: {}\n'.format(self.pH)
        for reagent in self.reagents:
            cocktail_string += '{} {}\n'.format(
                reagent.chemical_additive, reagent.concentration)
        return cocktail_string


class Reagent():

    units = ['M', '(w/v)', '(v/v)']

    def __init__(self, chemical_additive=None, concentration=None,
                 chemical_formula=None,stock_con=None):

        self.chemical_additive = chemical_additive
        self.concentration = concentration
        self.__chemical_formula = chemical_formula
        self.stock_con = stock_con  # should be in Molarity
        #print(self.__concentration, self.__concentration_units)

    @property
    def chemical_formula(self):
        return self.__chemical_formula
    
    @chemical_formula.setter
    def chemical_formula(self, new_formula):
        if isinstance(new_formula, str):
            water = water_regex.findall(new_formula)
            if water:
                num_waters = num_regex.findall(water[0])[0]
                new_formula = new_formula.replace(
                    water[0], '[H2O]{}'.format(num_waters)
                )
            self.__chemical_formula = Formula(new_formula)
        else:
            raise TypeError

    @property
    def concentration(self):
        return self.__concentration

    @concentration.setter
    def concentration(self, new_con):
        if isinstance(new_con, SignedValue):
            self.__concentration = new_con
        else:
            raise TypeError
            
    @property
    def molarity(self):
        if self.__concentration.unit == 'M':
            return self.concentration
        elif self.__concentration.unit == 'w/v' and self.molar_mass:
            M = (self.__concentration.value / self.molar_mass) * 10
            return SignedValue(M, 'M')
        else:
            return False


    @property
    def molar_mass(self):
        if isinstance(self.chemical_formula, Formula):
            return self.chemical_formula.mass
        PEG = self.peg_parser(self.chemical_additive)
        if PEG:
            return PEG
        return False

    def peg_parser(self, peg_string):
        keywords = set(['PEG', 'Polyethylene glycol'])
        for k in keywords:
            if k in peg_string:
                peg_string.replace(',', '')
                mm = peg_regex.findall(peg_string)
                if mm:
                    return float(mm[0])
        return False

    def stock_volume(self, target_volume):  # stock con must be in molarity
        # target volume in liters
        print(type(target_volume), 'target volume type')
        if self.stock_con and self.molarity:
            #print(type(self.molarity.value), type(target_volume.value), type(self.stock_con.value))
            L = (self.molarity.value * target_volume.value) / self.stock_con.value
            return SignedValue(L, 'L')
        else:
            return False

    def __str__(self):
        return '{} {}'.format(self.chemical_additive, self.concentration)


class SignedValue():
    # class for handling anything that comes with a unit
    supported_units = set(['M', 'v/v', 'w/v', 'L', 'X'])  # x is missing unit

    def __init__(self, string):
        self.value = string
        self.units = string
    
    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, string):
        if string:
            r = num_regex.findall(string)
            if r:
                self.__value = float(r[0])
            else:
                self.__value = 0.0
        else:
            self.__value = 0.0

    @property
    def units(self):
        return self.__units
    
    @units.setter
    def units(self, string):
        r = unit_regex.findall(string)
        if r and r[0] in self.supported_units:
            self.__units = r[0]
        else:
            self.__units = 'X' # missing units

    @property
    def milli(self):
        return self.value / 1e-3

    @property
    def micro(self):
        return self.value / 1e-6

    @property
    def nano(self):
        return self.value / 1e-9
    
    def __add__(self, other):
        if self.units == other.units:
            self.value += other.value

    def __sub__(self, other):
        if self.units == other.units:
            self.value -= other.value
    
    def __str__(self):
        return '{} {}'.format(self.value, self.units)
    
    def __float__(self):
        return self.value
