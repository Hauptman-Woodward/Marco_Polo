# from cockatoo.screen import _parse_cocktail_csv
# from cockatoo.metric import distance
from molmass import Formula
import re
from polo import *

logger = make_default_logger(__name__)

class Cocktail():
    '''Cocktail instances are used to hold a collection of 
    :class:`~polo.crystallography.cocktail.Reagent`
    instances that form one chemical cocktail. 
    Cocktails also hold other metadata including their commercial code,
    the cocktail pH and the well they are assigned to.
    Currently, cocktails are only supported for HWIRuns. 

    :param number: The cocktail number, defaults to None
    :type number: str, optional
    :param well_assignment: Well number in the screening plate this
                            cocktail belongs to, defaults to None
    :type well_assignment: int, optional
    :param commercial_code: Commercial code of cocktail, defaults to None
    :type commercial_code: str, optional
    :param pH: pH of the cocktail, defaults to None
    :type pH: float, optional
    :param reagents: list of reagent instances that make up the contents
        of the cocktail, defaults to None
    :type reagents: Reagent, optional
    '''

    def __init__(self, number=None, well_assignment=None,
                 commercial_code=None, pH=None, reagents=[]):
        self.well_assignment = well_assignment
        self.number = number
        self.commercial_code = commercial_code
        self.pH = pH
        self.reagents = reagents

    @property
    def cocktail_index(self):
        '''Attempt to pull out the cocktail number as an integer
        from the :attr:`~polo.crystallography.cocktail.Cocktail.number` attribute.
        This property is dependent on consistent formating 
        between cocktail menus that has not checked at this time.

        :return: Cocktail number
        :rtype: int
        '''
        try:     
            return int(self.number.split('_C')[-1].lstrip('0'))
        except IndexError as e:
            logger.error('Caught {} at cocktail_index property'.format(e))
            return None
        # normal cocktail number format 13_C0001

    @property
    def well_assignment(self):
        '''Return the current well assignment for this Cocktail.

        :return: well assignment
        :rtype: int
        '''
        return self._well_assignment

    @well_assignment.setter
    def well_assignment(self, value):
        if isinstance(value, (str, float)):
            value = int(value)
        self._well_assignment = value

    def add_reagent(self, new_reagent):
        '''Adds a reagent to the existing list of reagents referenced by the
        :attr:`~polo.crystallography.cocktail.Cocktail.reagents attribute.

        :param new_reagent: Reagent to add to this cocktail
        :type new_reagent: Reagent
        '''
        if new_reagent:
            self.reagents.append(new_reagent)

    # def compute_distance(self, other_cocktail):
    #     if isinstance(other_cocktail, Cocktail):
    #         this_cockatoo_cocktail = self._to_cockatoo_cocktail()
    #         other_cockatoo_cocktail = other_cocktail._to_cockatoo_cocktail()
    #         if this_cockatoo_cocktail and other_cockatoo_cocktail:
    #             return distance(this_cockatoo_cocktail, other_cockatoo_cocktail)
    #     return False

    # def _to_cockatoo_cocktail(self):
    #     # convert cocktail object to a "row" as read from a csv file for use with
    #     # cockatoo package
    #     # name,overall_ph,[conc,unit,name,ph]*
    #     row = [self.number, str(self.pH)]
    #     for reagent in self.reagents:
    #         if reagent.molarity != False:
    #             reagent_row = [
    #                 str(reagent.concentration.value),
    #                 str(reagent.concentration.units),
    #                 reagent.chemical_additive,
    #                 self.pH]  # doesnt seem like reagent pH is used in distance calc
    #             row += reagent_row
    #             return _parse_cocktail_csv(row)  # should return cocktail object if it worked
    #         # then can compare two cocktail objects
    #         else:
    #             break
    #     return False

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
    '''Reagent instances represent one specific kind of chemical compound at
    a specific concentration. Multiple Reagents make up a cocktail. Reagents
    are generally created from the contents of HWI cocktail csv files which
    describe all 1536 cocktails and the reagents that compose them in one file.
    The cocktail csv files can be found in the `data` directory.

    :param chemical_additive: Name of the chemical reagent,
                                defaults to None
    :type chemical_additive: str, optional
    :param concentration: Concentration of the reagent,
                            defaults to None
    :type concentration: UnitValue, optional
    :param chemical_formula: Chemical formula for this reagent, defaults
                                to None
    :type chemical_formula: Formula, optional
    :param stock_con: Concentration of this reagent's stock solution,
                        defaults to None
    :type stock_con: UnitValue, optional
    '''
    units = ['M', '(w/v)', '(v/v)']

    def __init__(self, chemical_additive=None, concentration=None,
                 chemical_formula=None, stock_con=None):


        self.chemical_additive = chemical_additive
        self.concentration = concentration
        self._chemical_formula = chemical_formula
        self.stock_con = stock_con  # should be in Molarity

    @property
    def chemical_formula(self):
        '''The chemical formula for of this Reagent. Not all
        Reagents have available chemical formulas as cocktail csv files do not
        include formulas for all reagents. See the setter method for more details
        on how chemical formulas are converted from strings to `Formula` objects.

        :return: Chemical formula
        :rtype: Formula
        '''
        return self._chemical_formula

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
            self._chemical_formula = Formula(new_formula)
        else:
            raise TypeError

    @property
    def concentration(self):
        '''The current concentration of this Reagent. Concentration
        ultimately refers back to a condition in a specific screening well.

        :return: Chemical concentration
        :rtype: UnitValue
        '''
        return self._concentration

    @concentration.setter
    def concentration(self, new_con):
        '''Setter function for the concentration attribute.

        :param new_con: New value for concentration
        :type new_con: UnitValue
        :raises TypeError: Raised when attempt to pass object that is not an\
            instance of UnitValue as the new_con
        '''
        if isinstance(new_con, UnitValue):
            self._concentration = new_con
        else:
            raise TypeError

    @property
    def molarity(self):
        '''Attempt to calculate the molarity of this reagent at its current
        concentration. This calculation is not certain to return a value
        as HWI cocktail menu files use a variety of units to describe
        chemical concentrations, including %w/v or %v/v.

        %w/v is defined as grams of colute per 100 ml of solution * 100. This can
        be converted to molarity when the molar mass of the reagent is known.

        %v/v is defined as the volume of solute over the total volume of solution
        * 100. The density of the reagent is required to convert %w/v to molarity
        which is not included in HWI cocktail menu files. This makes conversion
        from %w/v out of reach for now.
        
        If the reagent concentration cannot be converted to molarity then
        this function will return False.

        :return: molarity or False
        :rtype: UnitValue or Bool
        '''
        base_con = self._concentration.to_base()
        if base_con.units == 'M':
            return base_con
        elif base_con.units == 'w/v' and self.molar_mass:
            M = (base_con.value / self.molar_mass) * 10
            return UnitValue(M, 'M')
        else:
            return False

    @property
    def molar_mass(self):
        '''Attempt to calculate the molar mass of this reagent. Closely related
        to the molarity property. The molar mass of the reagent cannot be
        calculated for all HWI reagents. 
      
        :return: Molar mass of the Reagent if it is calculable, False otherwise.
        :rtype: UnitValue or bool
        '''
        mm = None
        if isinstance(self.chemical_formula, Formula):
            mm = self.chemical_formula.mass
        PEG = self.peg_parser(self.chemical_additive)
        if PEG:
            mm = PEG
        if mm:
            return mm
        return False

    def peg_parser(self, peg_string):
        '''Attempts to pull out a molar mass from a PEG species since the
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
                peg_string = peg_string.replace(',', '')
                mm = peg_regex.findall(peg_string)
                if mm:
                    return float(mm[0])
        return False

    def stock_volume(self, target_volume):  # stock con must be in molarity
        '''Attempt to calculate the required amount of stock solution to
        produce the Reagent's set concentration in the given `target_volume`
        argument. Stock concentration is taken from the 
        :attr:`~polo.crystallography.cocktail.Cocktail.stock_con` attribute. If
        :attr:`~polo.crystallography.cocktail.Cocktail.stock_con` is not
        set or the molarity of the reagent can not be calculated this method
        will return False.

        :param target_volume: Volume in which stock will be diluted into
        :type target_volume: UnitValue
        :return: Volume of stock or False
        :rtype: UnitValue or False
        '''
        # target volume in liters
        if self.stock_con and self.molarity:
            L = (self.molarity.value * target_volume.value) / \
                self.stock_con.to_base().value
            return UnitValue(L, 'L')
        else:
            return False

    def __str__(self):
        return '{} {}'.format(self.chemical_additive, self.concentration)


class UnitValue():
    # class for handling anything that comes with a unit
    '''UnitValues are used to help handle numbers with units. They
    are not the most robust but help to keep things more organized.
    UnitValues can be created by either passing values to the
    `values` and `units` args explicitly or by calling the classmethod
    :meth:`~polo.crystallography.cocktail.UnitValue.make_from_string`
    which will use regex to pull out supported units and
    values.
    '''
    saved_scalers = {'u': 1e-6, 'm': 1e-3, 'c': 1e-2}

    def __init__(self, value=None, units=None):
        self.value = value
        self.units = units

    def set_from_string(self, string):
        self.value = string
        self.units = string

    @classmethod
    def make_from_string(cls, string):
        '''Create a `UnitValue` from a string containing a value and a unit.
        Utilizes the :const:`polo.unit_regex` expression 
        to pull out the units. 

        .. highlight:: python
        .. code-block:: python

            unit_string = '10.0 M'  # concentration of 10 molar
            sv = UnitValue.make_from_string(unit_string)
            # sv.value = 10 sv.units = 'M'


        :param string: The string to extract the UnitValue from
        :type string: str
        :return: UnitValue instance
        :rtype: UnitValue
        '''
        units = unit_regex.findall(string)
        if units:
            units = units[0]
        return cls(value=string, units=units)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if isinstance(value, (int, float)):
            self._value = value
        elif isinstance(value, str):
            value = num_regex.findall(value)
            if value:
                value = float(value[0])
        else:
            value = 0.0
        self._value = value

    def scale(self, scale_key):
        '''Scale the :attr:`~polo.crystallography.cocktail.UnitValue.value`
        using a key character that exists in the 
        :const:`~polo.crystallography.cocktail.UnitValue.saved_scalers`
        dictionary. First converts the value to its
        base unit and then divides by the `scale_key` argument value. 
        The `scale_key` can be thought of as a SI prefix for a base unit.

        .. highlight:: python
        .. code-block:: python

            # self.saved_scalers = {'u': 1e-6, 'm': 1e-3, 'c': 1e-2}
            v_one = UnitValue(10, 'L')  # value of 10 liters
            v_one = v_one.scale('u')  # get v_one in microliters

        :param scale_key: Character in :const:`~polo.crystallography.cocktail.UnitValue.saved_scalers`
                          to convert value to.
        :type scale_key: str
        :return: UnitValue converted to scale_key unit prefix
        :rtype: UnitValue
        '''
        if scale_key in self.saved_scalers:
            temp = self.to_base()  # send to base unit
            return UnitValue(
                temp.value / self.saved_scalers[scale_key], scale_key + temp.units)
    
    def to_base(self):
        '''Converts the :attr:`~polo.crystallography.cocktail.UnitValue.value`
        to the base unit, if it is not already in the base unit.

        :return: UnitValue converted to base unit
        :rtype: UnitValue
        '''
        if self.units and self.units[0] in self.saved_scalers:
            return UnitValue(
                self.value * self.saved_scalers[self.units[0]], self.units[1:])
        else:
            return self
    
    def round(self, digits):
        pass
        # reduct the total number of digits so it looks nice to print


    def __add__(self, other):
        if self.units == other.units:
            self.value += other.value

    def __sub__(self, other):
        if self.units == other.units:
            self.value -= other.value

    def __str__(self):
        return '{} {}'.format(self.value, self.units)

    def __float__(self):
        return float(self.value)
