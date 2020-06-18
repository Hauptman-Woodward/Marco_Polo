from polo.utils.exceptions import NotASolutionError
from molmass import Formula
import re
from polo import *


class Cocktail():
    '''Cocktail instances are used to hold a collection of reagents
    that form one chemical cocktail screen. Also hold metadata including
    their commerical code if one exists, the cocktail pH and the
    well they are assigned to. Currently, cocktails are only supported
    for HWIRuns.

    :param number: The cocktail number, defaults to None
    :type number: str, optional
    :param well_assignment: Well number in plate this cocktail belongs to, \
        defaults to None
    :type well_assignment: int, optional
    :param commercial_code: Commercial code of cocktail if supplied by \
        third party, defaults to None
    :type commercial_code: str, optional
    :param pH: pH of cocktail, defaults to None
    :type pH: float, optional
    :param reagents: list of reagent instances that make up the contents \
        of the cocktail instance, defaults to None
    :type reagents: Reagent, optional
    '''

    def __init__(self, number=None, well_assignment=None,
                 commercial_code=None, pH=None, reagents=None):
        self.well_assignment = well_assignment
        self.number = number
        self.commercial_code = commercial_code
        self.pH = pH
        self.reagents = []

    @property
    def cocktail_index(self):
        '''Attempt to pull out the cocktail number from the cocktail number
        string. Dependent on consistent formating between cocktail menus that
        I have not currently varrified.

        :return: cocktail number
        :rtype: int
        '''     
        return self.number.split('_C').lstrip('0')
        # normal cocktail number format 13_C0001

    @property
    def well_assignment(self):
        '''Return the current well assignment for this cocktail

        :return: well assignment
        :rtype: int
        '''
        return self.__well_assignment

    @well_assignment.setter
    def well_assignment(self, value):
        '''Setter function for the well_assignment attribute.

        :param value: well number
        :type value: str, int or float
        '''
        if isinstance(value, (str, float)):
            value = int(value)
        self.__well_assignment = value

    def add_reagent(self, new_reagent):
        '''Adds a reagent to the existing list of reagents stored in the
        reagents attribute.

        :param new_reagent: Reagent to add to this cocktail
        :type new_reagent: Reagent
        '''
        if new_reagent:
            self.reagents.append(new_reagent)

    def __repr__(self):
        return ''.join(sorted(['{}: {}\n'.format(key, value) for key, value in self.__dict__.items()]))

    def __str__(self):
        cocktail_string = 'Cocktail {}\n'.format(self.number)
        cocktail_string += '-'*len(cocktail_string) + '\n'
        cocktail_string += 'pH: {}\n'.format(self.pH)
        for reagent in self.reagents:
            cocktail_string += '{} {}\n'.format(
                reagent.chemical_additive, reagent.concentration)
        return cocktail_string


class Reagent():
    '''Reagent instances represent one specific kind of chemical compound
    used in a screening cocktail. 

    :param chemical_additive: Name of the reagent chemical,
                                defaults to None
    :type chemical_additive: str, optional
    :param concentration: Concentration of the reagent in a given well,
                            defaults to None
    :type concentration: SignedValue, optional
    :param chemical_formula: Chemical formula for this reagent, defaults
                                to None
    :type chemical_formula: str, optional
    :param stock_con: Concentration of this reagent's stock solution,
                        defaults to None
    :type stock_con: SignedValue, optional
    '''
    units = ['M', '(w/v)', '(v/v)']

    def __init__(self, chemical_additive=None, concentration=None,
                 chemical_formula=None, stock_con=None):


        self.chemical_additive = chemical_additive
        self.concentration = concentration
        self.__chemical_formula = chemical_formula
        self.stock_con = stock_con  # should be in Molarity
        #print(self.__concentration, self.__concentration_units)

    @property
    def chemical_formula(self):
        '''Return the current chemical formula for this Reagent. It is not
        certain that a reagent will have a chemical formula.

        :return: Chemical formula
        :rtype: molmass.Formula
        '''
        return self.__chemical_formula

    @chemical_formula.setter
    def chemical_formula(self, new_formula):
        '''Setter function for the chemical formula attribute. Assumes that
        a string will be passed in and attempts to convert that string to a
        Formula instance. The HWI formating for associated water molecules is
        not understood by Formula objects so this method uses regex to extract
        the number of water molecules are rewrite the formula to an equivalent
        one that Formula object can understand.

        :param new_formula: chemical formula
        :type new_formula: str
        :raises TypeError: Raised when attemping to set chemical_formula to\
            something other than a string
        '''
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
        '''Return the current concentration for this reagent. Concentration
        utimately refers back to a condition in a specific screening well.

        :return: Chemical concentration
        :rtype: SignedValue
        '''
        return self.__concentration

    @concentration.setter
    def concentration(self, new_con):
        '''Setter function for the concentration attribute.

        :param new_con: New value for concentration
        :type new_con: SignedValue
        :raises TypeError: Raised when attempt to pass object that is not an\
            instance of SignedValue as the new_con
        '''
        if isinstance(new_con, SignedValue):
            self.__concentration = new_con
        else:
            raise TypeError

    @property
    def molarity(self):
        '''Attempt to calculate the molarity of this reagent at its current
        concentration. This calculation is not certain to return a molarity
        because HWI cocktail menu files use a variety of units to describe
        chemical concentrations, including %w/v or %v/v. Currently, Polo is
        not able to convert %v/v units to molarity as it would require knowing
        both the molar mass of the reagent and its density. If the reagent
        concentration cannot be converted to mols / liter then returns false.

        :return: molarity or False
        :rtype: SignedValue or Bool
        '''
        if self.__concentration.units == 'M':
            return self.concentration
        elif self.__concentration.units == 'w/v' and self.molar_mass:
            M = (self.__concentration.value / self.molar_mass) * 10
            print(SignedValue(M, 'M'), 'molarity')
            return SignedValue(M, 'M')
        else:
            return False

    @property
    def molar_mass(self):
        '''Attempt to calculate the molar mass of this reagent. Closely related
        to the molarity property. See its docstring for why this is not always
        possible. Return False if cannot be calculated.

        :return: Molarity or False
        :rtype: SignedValue or False
        '''
        if isinstance(self.chemical_formula, Formula):
            return self.chemical_formula.mass
        PEG = self.peg_parser(self.chemical_additive)
        if PEG:
            return PEG
        return False

    def peg_parser(self, peg_string):
        '''Attempts to pull out a molar mass from a chemical name since the
        molar mass is often included in the name of PEG species. A string is
        considered to be a potential PEG species if it contains 'PEG' or
        'Polyethylene glycol' in it.

        :param peg_string: String to look for PEG species in
        :type peg_string: str
        :return: molar mass if found to be valid PEG species, False otherwise.
        :rtype: float or Bool
        '''
        keywords = set(['PEG', 'Polyethylene glycol'])
        for k in keywords:
            if k in peg_string:
                peg_string.replace(',', '')
                mm = peg_regex.findall(peg_string)
                if mm:
                    return float(mm[0])
        return False

    def stock_volume(self, target_volume):  # stock con must be in molarity
        '''Attempt to calculate the required amount of stock solution to
        produce the reagent's set concentration in the given target_volume.
        Stock concentration is taken from the stock_con attribute. If
        stock_con is not set or the molarity of the reagent can not be
        calculated this method will return False.

        :param target_volume: Volume in which stock will be diluted into
        :type target_volume: SignedValue
        :return: Volume of stock or False
        :rtype: SignedValue or False
        '''
        # target volume in liters
        if self.stock_con and self.molarity:
            #print(type(self.molarity.value), type(target_volume.value), type(self.stock_con.value))
            L = (self.molarity.value * target_volume.value) / \
                self.stock_con.value
            print(SignedValue(L, 'L'), 'stock con')
            return SignedValue(L, 'L')
        else:
            return False

    def __str__(self):
        return '{} {}'.format(self.chemical_additive, self.concentration)


class SignedValue():
    # class for handling anything that comes with a unit
    '''SignedValues are used to help handle numbers with units. They
    are not the most robust but help to keep things more organized.
    SignedValues can be created by either passing values to the
    `values` and `units` args explicitly or by calling the classmethod
    `make_from_string` which will use regex to pull out supported units and
    values.
    '''
    supported_units = set(['M', 'v/v', 'w/v', 'L', 'X'])  # x is missing unit

    def __init__(self, value=None, units=None):
        self.value = value
        self.units = units

    def set_from_string(self, string):
        self.value = string
        self.units = string

    @classmethod
    def make_from_string(cls, string):
        '''Create a SignedValue instance from a string containing a value
        and a supported unit

        :param string: The string to extract the SignedValue from
        :type string: str
        :return: SignedValue instance
        :rtype: SignedValue
        '''
        return cls(value=string, units=string)

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    @property
    def units(self):
        return self.__units

    @units.setter
    def units(self, string):
        r = unit_regex.findall(str(string))
        if r and r[0] in self.supported_units:
            self.__units = string
        else:
            self.__units = 'X'  # missing units

    @property
    def milli(self):
        '''Convert the current `value` to milli scale. This assumes that the value
        is the base unit.

        :return: Value converted to milli
        :rtype: float
        '''
        return SignedValue(self.value / 1e-3, 'm{}'.format(self.units))

    @property
    def micro(self):
        '''Convert the current `value` to micro scale. This assumes that the value
        is the base unit.

        :return: Value converted to micro
        :rtype: float
        '''
        return SignedValue(self.value / 1e-6, 'u{}'.format(self.units))

    @property
    def nano(self):
        '''Convert the current `value` to nano scale. This assumes that the value
        is the base unit.

        :return: Value converted to nano
        :rtype: float
        '''
        return SignedValue(self.value / 1e-6, 'n{}'.format(self.units))

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
