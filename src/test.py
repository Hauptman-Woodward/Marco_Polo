# import json
# import json
# import os
# from pathlib import Path
# from datetime import datetime

# __version__ = '0.0.1'

# class RunSerializer():

#     def __init__(self, run):
#         self.__run = run
    
#     @property
#     def run(self):
#         return self.__run
    
#     @run.setter
#     def run(self, new_run):
#             self.__run = new_run

#     @classmethod
#     def path_suffix_checker(cls, path, desired_suffix):
#         # checked path to see if it has the desired_suffix as suffix
#         if isinstance(path, str):
#             path = Path(path)
#         if path.suffix == desired_suffix:
#             return str(path)
#         else:
#             return str(path.with_suffix(desired_suffix))

    
#     @classmethod
#     def path_validator(cls, path, parent=False):
#         # returns True if path exists false otherwise
#         # path can be string or Path object
#         # parent = True checks for existance of parent dir
#         # used for checking if location for a save file exists before the
#         # save file is made
#         if isinstance(path, (str, Path)):
#             if isinstance(path, str):
#                 path = Path(path)
#             if parent:
#                 return path.parent.exists()
#             else:
#                 return path.exists()
#         else:
#             return False
    
#     def __repr__(self):
#         s = ''
#         for key, value in self.__dict__.items():
#             s += '{}: {}\n'.format(key, value)
#         return s


# class XtalWriter(RunSerializer):
#     header_flag = '<>'
#     header_line = '{}{}:{}\n'
#     file_ext = '.xtal'

#     def __init__(self, run, **kwargs):
#         super(XtalWriter, self).__init__(run)
#         self.__dict__.update(kwargs)
    
#     @property
#     def xtal_header(self):
#         header = ''
#         header += self.header_line.format(
#             self.header_flag, 'SAVE TIME', datetime.now())
#         header += self.header_line.format(
#             self.header_flag, 'VERSION', __version__)
#         for key, value in self.__dict__.items():
#             header += self.header_line.format(
#                 self.header_flag, str(key).upper(), value)
#         return header + '='*79 + '\n'
#         # add ==== as a break between json data and header data
    
#     @classmethod
#     def json_encoder(cls, obj):
#         d = None
#         if hasattr(obj, '__dict__'):  # can send to dict object
#             d = obj.__dict__
#             d['__class__'] = obj.__class__.__name__
#             d['__module__'] = obj.__module__
#             # store module and class name along with object as dict
#         else:  # not castable to dict
#             if isinstance(obj, bytes):  # likely the base64 encoded image
#                 d = obj.decode('utf-8')
#             else:
#                 d = str(obj)  # if all else fails case to string
#         return d
    
#     def write_xtal_file(self, output_path):
#         if XtalWriter.path_validator(output_path, parent=True):
#             # path is good to go and ready to write file into 
#             run_str = self.run_to_dict()
#             if isinstance(run_str, str):  # encoding worked, no errors caught
#                 output_path = XtalWriter.path_suffix_checker(
#                     output_path, self.file_ext)  # make sure has .xtal suffix
#                 try:
#                     with open(str(output_path), 'w') as xtal_file:
#                         xtal_file.write(self.xtal_header)
#                         xtal_file.write(run_str)
#                         return output_path
#                 except PermissionError as e:
#                     return e

#     def clean_run_for_save(self):
#         # removes references to other runs so not to throw a
#         # json encoding error
#         if self.run:
#             # logger.info('Cleaning {} for export'.format(self.run))
#             self.run.previous_run, self.run.next_run, self.run.alt_spectrum = (
#                 None, None, None)
#             for image in self.run.images:
#                 if image:
#                     image.previous_image, image.next_image, image.alt_image = (
#                         None, None, None
#                     )
#         return self.run
    
#     def run_to_dict(self):
#         if self.run:
#             try:
#                 # self.clean_run_for_save()
#                 # self.run.encode_images_to_base64()
#                 return json.dumps(self.run, ensure_ascii=True, indent=4,
#                                 default=XtalWriter.json_encoder)
#             except (TypeError, FileNotFoundError,
#                     IsADirectoryError, PermissionError) as e:
#                     # logger.warning('Failed to write {} to {} Gave {}'.format(
#                     #     run, output_path, e
#                     # ))
#                     return e

# # data = {
# #   "name": "John",
# #   "age": 30,
# #   "city": "New York"
# # }

# # f = XtalWriter(run=data, fuck=10, username='Ethan Holleman', god='Hello')
# # f.write_xtal_file('./fuck')

# # xtal_file_io = open('./fuck.xtal')

# # header_data=[]
# # hf = XtalWriter.header_flag
# # while True:
# #     hd = xtal_file_io.readline()
# #     if hd[0:len(hf)] == hf:
# #         header_data.append(hd)
# #     else:
# #         break
# # print(header_data)

# # print(json.load(xtal_file_io))

# def tester(**kwargs):
#     return kwargs

# print(tester(hello=10))

# class test():

#     a = 10

#     def __getitem__(self, value, **kwargs):
#         print(kwargs)

# t = test()
# t[10], can=10
from molmass import Formula
import re

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

    num_regex = re.compile('[-+]?([0-9]*\.[0-9]+|[0-9]+)')
    peg_regex = re.compile('[0-9]+')
    unit_regex = re.compile('v/v|w/v|M', re.I)

    def __init__(self, chemical_additive=None, concentration=None,
                 chemical_formula=None,stock_con=None):

        self.chemical_additive = chemical_additive
        self.__concentration = concentration
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
                num_waters = self.num_regex.findall(water[0])[0]
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
                mm = self.peg_regex.findall(peg_string)
                if mm:
                    return float(mm[0])
        return False

    def stock_volume(self, target_volume):  # stock con must be in molarity
        # target volume in liters
        if self.stock_con and self.molarity:
            #print(type(self.molarity.value), type(target_volume.value), type(self.stock_con.value))
            L = (self.molarity.value * target_volume.value) / self.stock_con.value
            return SignedValue(L, 'L')
        else:
            return False

    def __str__(self):
        return '{} {}'.format(self.chemical_additive, self.concentration)


num_regex = re.compile('[-+]?([0-9]*\.[0-9]+|[0-9]+)')
peg_regex = re.compile('[0-9]+')
unit_regex = re.compile('v/v|w/v|M', re.I)
water_regex = re.compile('\*[0-9]*h2o', re.I)



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

class BarTender():

    def __init__(self, cocktail_dir, cocktail_meta):
        self.cocktail_dir = cocktail_dir
        self.cocktail_meta = cocktail_meta
        self.menus = {}
    
    @staticmethod
    def datetime_converter(date_string):
        date_string = date_string.strip()
        datetime_formats = ['%m/%d/%Y', '%m/%d/%y', '%m-%d-%Y', '%m-%d-%y']
        for form in datetime_formats:
            try:
                return datetime.strptime(date_string, form)
            except ValueError as e:
                continue
    
    @staticmethod
    def date_range_parser(date_range_string):
        s, e = date_range_string.split('-')
        s = BarTender.datetime_converter(s.strip())
        if e.strip():
            e = BarTender.datetime_converter(e.strip())
        else:
            e = None
        return s, e
    
    def add_menus_from_metadata(self):
        if self.cocktail_meta:
            with open(str(self.cocktail_meta)) as menu_files:
                reader = csv.DictReader(menu_files)
                for row in reader:
                    path = os.path.join(str(COCKTAIL_DATA_PATH), row['File Name'])
                    s, e = BarTender.date_range_parser(row['Dates Used'])
                    self.menus[path] = Menu(
                        path, s, e, row['Screen Type']
                    )
                    # add new menu to menus dict path to csv file is the menu
                    # key

    def get_menu_by_date(self, date, type_):
         if isinstance(date, datetime):
            # search for a menu whos usage dates include this date
            menus_keys_by_date = sorted(
                [key for key in self.menus.keys() if self.menus[key].type_ == type_],
                # keys matching only the specified type
                key=lambda key: self.menus[key].start_date
            )
            print(menus_keys_by_date)
            # end up with a list of keys for menus of the specified type that
            # are sorted by the start date of their use at HWI cente
            for each_key in menus_keys_by_date:
                if date < self.menus[each_key].start_date:
                    return self.menus[each_key]
            return menus[menus_keys_by_date[-1]]



                # if date >= self.menus[each_key].start_date:
                    # print('after this')
                    # if self.menus[each_key].end_date: # not current menu
                    #     if date <= self.menus[each_key].end_date:
                    #         return self.menus[each_key]
                    # else:  # at the current date, must return this one
                    #     return self.menus[each_key]
    
    def get_menus_by_type(self, type_):
        return [menu for menu in self.menus if menu.type_ == type_]
        
import csv

class CocktailMenuReader():

    cocktail_map = {  # map Cocktail attributes to index in menu rows
        0: 'well_assignment',
        1: 'number',
        8: 'pH',
        2: 'commercial_code'
        }
    
    formula_pos = 4  # each reagent could have a formula but only ever
    # one is included per cocktail entry

    # all other indicies are reagent names and concentrations

    def __init__(self, menu_file, delim=',', **kwargs):
        self.menu_file = menu_file
        self.reader = csv.reader(self.menu_file)
        self.delim = delim
        self.__row_counter = 0
        self.__dict__.update(kwargs)
    
    @classmethod
    def set_cocktail_map(cls, map):
        cls.cocktail_map = cocktail_map
    
    @classmethod
    def set_formula_pos(cls, pos):
        cls.formula_pos = pos
    
    @property
    def menu_file(self):
        return self.__menu_file

    @menu_file.setter
    def menu_file(self, new_file):
        if isinstance(new_file, str):
            self.__menu_file = open(new_file)
            next(self.__menu_file)
            next(self.__menu_file)  # skip first two rows
        else:
            self.__menu_file = new_file
    
    def parse_row(self, row):
        return [i.replace('"', '') for i in row.strip().split(self.delim)]

    # need to deciede how fixed on the current header system want to be
    def __next__(self):  # would be nice if returned a cocktail
        row = next(self.reader)
        d = {self.cocktail_map[index]: row[index] for index in self.cocktail_map}
        c = Cocktail(**d)
        reagent_pos = [i for i in range(len(row)) if i not in self.cocktail_map and i != self.formula_pos]
        # positions that should contain reagent information. Additionally,
        # reagent names and their concentrations should now be adjacent to
        # each other in the list of indicies
        for i in range(0, len(reagent_pos), 2):
            chem_add, con = row[reagent_pos[i]], row[reagent_pos[i+1]]
            if chem_add:
                con = SignedValue(con)
                c.add_reagent(
                    Reagent(
                        chemical_additive=chem_add,
                        concentration=con
                    )
                )
        if row[self.formula_pos]:
            c.reagents[0].chemical_formula = row[self.formula_pos].strip()
        return c
    
    def __iter__(self):
        while True:
            try:
                yield self.__next__()
            except StopIteration:
                break
            


        # for i in range(0, len(reagent_pos), 2):
        #     if row[i]:
        #         chem_add = row[reagent_pos[i]].strip()
        #         con = num_regex.findall(row[i+1])
        #         units = unit_regex.findall(row[reagent_pos[i+1]])

        #         if con:
        #             con = con[0]
        #         else:
        #             con = 0.0  # missing con
        #         if units:
        #             units = units[0]
        #         else:
        #             units = 'X'  # missing units
            
        #     c.add_reagent(
        #         Reagent(
        #             chem_add, SignedValue(con, units)
        #         )
        #     )
        # add all cocktail attributes using the cocktail map
        # now need to parse through the reagents

        # dont know how many reagents there could be or if they will be missing
        # values

        #return c
        
from pathlib import Path
from datetime import datetime
import os
import csv

        


class Menu():  # holds the dictionary of cocktails
    
    def __init__(self, path, start_date, end_date, type_):
        self.start_date = start_date
        self.end_date = end_date
        self.type_ = type_
        self.__cocktails = {}  # holds all cocktails (items on the menu)
        self.path = path
    
    @property
    def cocktails(self):
        return self.__cocktails

    @property
    def path(self):
        return self.__path
    
    @path.setter
    def path(self, new_path):
        self.__path = new_path  # set the path to the new_path
        cocktail_reader = CocktailMenuReader(self.path)
        for cocktail in cocktail_reader:
            self.cocktails[cocktail.well_assignment] = cocktail
        # create dictionary from cocktails, key is the well number (assignment)
    
from pathlib import Path
from datetime import datetime
import os
import csv

data_prefix = 'data/'

COCKTAIL_DATA_PATH = Path(os.path.join(data_prefix, 'cocktail_data/'))
COCKTAIL_META_DATA = Path(os.path.join(data_prefix, 'cocktail_data/cocktail_meta.csv'))

tim = BarTender(COCKTAIL_DATA_PATH, COCKTAIL_META_DATA)
tim.add_menus_from_metadata()
c = (tim.menus['data/cocktail_data/12_C1536.csv'].cocktails)

f = tim.get_menu_by_date(datetime.strptime('12/31/2012', '%m/%d/%Y'), type_='s')
print(type(f), f.path)