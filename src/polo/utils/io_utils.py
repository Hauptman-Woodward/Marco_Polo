import base64
import csv
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from dateutil.parser import parse
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QApplication, QGridLayout

from jinja2 import Template
from polo import (ALLOWED_IMAGE_TYPES, COCKTAIL_DATA_PATH, COCKTAIL_META_DATA,
                  RUN_HTML_TEMPLATE, SCREEN_HTML_TEMPLATE, __version__,
                  make_default_logger, num_regex, unit_regex)
from polo.crystallography.cocktail import Cocktail, Reagent, SignedValue
from polo.threads.thread import QuickThread
from polo.utils.exceptions import EmptyRunNameError, ForbiddenImageTypeError
from polo.utils.math_utils import best_aspect_ratio, get_cell_image_dims

logger = make_default_logger(__name__)


class RunSerializer():

    def __init__(self, run):
        self.run = run

    @classmethod
    def make_thread(cls, job_function, **kwargs):
        '''
        Creates a new qthread object. The job function is the
        function the thread will execute and and arguments that the job
        function requires should be passed has keyword arguments. These are
        stored as a dictionary in the new thread object until the thread is
        activated and they are passed as arguments.
        '''
        return QuickThread(job_function, parent=None, **kwargs)

    @staticmethod
    def path_suffix_checker(path, desired_suffix):
        '''
        Check is a file path has a desired suffix, if not then replace the
        current suffix with the desired suffix. Useful for checking filenames
        that are taken from user input.

        :param desired_suffix: File extension for given file path.
        '''

        if isinstance(path, str):
            path = Path(path)
        if path.suffix == desired_suffix:
            return str(path)
        else:
            return str(path.with_suffix(desired_suffix))

    @staticmethod
    def make_message_box(message, icon=QtWidgets.QMessageBox.Information,
                         buttons=QtWidgets.QMessageBox.Ok,
                         connected_function=None):
        '''Return a QMessageBox instance to show to the user.

        :param message: Message to be displayed to the user
        :type message: str
        :param icon: Icon for message box, defaults to QtWidgets.QMessageBox.Information
        :type icon: QMessageBoxIcon, optional
        :param buttons: [description], defaults to QtWidgets.QMessageBox.Ok
        :type buttons: [type], optional
        :param connected_function: [description], defaults to None
        :type connected_function: [type], optional
        :return: [description]
        :rtype: [type]
        '''
        msg = QtWidgets.QMessageBox()
        msg.setIcon(icon)
        msg.setText(message)
        msg.setStandardButtons(buttons)
        if connected_function:
            msg.buttonClicked.connect(connected_function)
        logger.info('Made message box with message "{}"'.format(message))
        return msg

    @staticmethod
    def path_validator(path, parent=False):
        '''
        Tests to ensure a path exists. Passing parent = True will check for
        the existance of the parent directory of the path.
        '''

        if isinstance(path, (str, Path)):
            if isinstance(path, str):
                path = Path(path)
            if parent:
                return path.parent.exists()
            else:
                return path.exists()
        else:
            return False

    def __repr__(self):
        s = ''
        for key, value in self.__dict__.items():
            s += '{}: {}.unitsn'.format(key, value)
        return s[:-1]


class HtmlWriter(RunSerializer):

    def __init__(self, run, **kwargs):
        super(HtmlWriter, self).__init__(run)
        self.__dict__.update(kwargs)

    @staticmethod
    def make_template(template_path):
        '''
        Given a path to an html file to serve as a jinja2 template, read the
        file and create a new template object.
        '''
        with open(template_path, 'r') as template:
            contents = template.read()
            return Template(contents)

    def write_complete_run_on_thread(self, output_path, encode_images):
        '''
        Wrapper around `write_complete_run` that executes on a seperate
        Qthread.
        '''
        self.thread = HtmlWriter.make_thread(
            self.write_complete_run, output_path=output_path,
            encode_images=encode_images)
        self.thread.finished.connect(self.finished_writing)
        self.thread.start()

    def finished_writing(self):  # should only be called from connection to thread
        '''
        Method to connect to Qthread instance. Should not be called from
        anything other than a Qthread instance.
        '''
        result = str(self.thread.result)
        if os.path.exists(result):
            message = 'Export to {} was successful'.format(result)
        else:
            message = 'Export to HTML file failed. Returned {}'.format(result)
        HtmlWriter.make_message_box(message=message).exec_()

    def write_complete_run(self, output_path, encode_images=True):
        # write a run as html file with images and classifications
        # and that kind of stuff
        if HtmlWriter.path_validator(output_path, parent=True) and self.run:
            output_path = HtmlWriter.path_suffix_checker(output_path)
            if encode_images:
                run.encode_images_to_base64()
            images = json.loads(json.dumps(
                run.images, default=XtalWriter.json_encoder))
            template = HtmlWriter.make_template(RUN_HTML_TEMPLATE)
            if template:
                html = template.render(
                    images=images, run_name=self.run.run_name,
                    annotations='No annotations')
                with open(output_path, 'w') as html_file:
                    html_file.write(html)
                    return output_path

    def write_grid_screen(self, output_path, plate_list, well_number,
                          x_reagent, y_reagent, well_volume, run_name=None):
        '''Write the contents of optimization grid screen to an html file

        :param output_path: Path to html file
        :type output_path: str
        :param plate_list: list containing grid screen data
        :type plate_list: list
        :param well_number: well number of hit screen is created from
        :type well_number: int or str
        :param x_reagent: reagent varried in x direction
        :type x_reagent: Reagent
        :param y_reagent: reagent varried in y direction
        :type y_reagent: Reagent
        :param well_volume: Volume of well used in screen
        :type well_volume: int or str
        :param run_name: name of run, defaults to None
        :type run_name: str, optional
        '''
        if HtmlWriter.path_validator(output_path, parent=True):
            output_path = HtmlWriter.path_suffix_checker(ouput_path, '.html')
            template = HtmlWriter.make_template(SCREEN_HTML_TEMPLATE)
            if not run_name:
                run_name = self.run.run_name
            html = template.render(plate_list=plate_list, run_name=run_name,
                                   well_number=well_number, date=datetime.now(),
                                   x_reagent_stock=x_reagent,
                                   y_reagent_stock=y_reagent,
                                   well_volume=str(well_volume))
            with open(output_path, 'w') as screen_html:
                screen_html.write(html)


class XtalWriter(RunSerializer):
    header_flag = '<>'  # do not change unless very good reason
    header_line = '{}{}:{}\n'
    file_ext = '.xtal'

    def __init__(self, run, **kwargs):
        self.__dict__.update(kwargs)
        super(XtalWriter, self).__init__(run)

    @property
    def xtal_header(self):
        '''
        Creates the header for xtal file when called. Header lines are
        indicated as such by the string in the header_line constant,
        which should be '<>'. The last line of the header will be a row
        of equal signs and then the actual json content begins on the
        next line.
        '''
        header = ''
        header += self.header_line.format(
            self.header_flag, 'SAVE TIME', datetime.now())
        header += self.header_line.format(
            self.header_flag, 'VERSION', __version__)
        for key, value in self.__dict__.items():
            header += self.header_line.format(
                self.header_flag, str(key).upper(), value)
        return header + '='*79 + '\n'
        # add ==== as a break between json data and header data

    @staticmethod
    def json_encoder(obj):
        '''
        Use instead of the defauly json encoder. If the encoded object
        is from a module within Polo will include a module and class
        identifier so it can be more easily deserialized when loaded
        back into the program.

        :param: obj: An object to serialize to json.

        :returns: A dictionary or string version of passed object
        '''
        d = None
        if hasattr(obj, '__dict__'):  # can send to dict object
            d = obj.__dict__
            d['__class__'] = obj.__class__.__name__
            d['__module__'] = obj.__module__
            # store module and class name along with object as dict
        else:  # not castable to dict
            if isinstance(obj, bytes):  # likely the base64 encoded image
                d = obj.decode('utf-8')
            else:
                d = str(obj)  # if all else fails case to string
        return d

    def write_xtal_file_on_thread(self, output_path):
        """Wrapper method around `write_xtal_file` that executes on a Qthread
        instance to prevent freezing the GUI when saving large xtal files

        :param output_path: Path to xtal file
        :type output_path: str
        """

        self.thread = XtalWriter.make_thread(
            self.write_xtal_file, output_path=output_path)
        # connect to something when thread finishes
        self.thread.finished.connect(self.finished_save)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.thread.start()

    def finished_save(self):
        QApplication.restoreOverrideCursor()  # return cursor to normal
        # should contain path to now saved file
        if os.path.exists(str(self.thread.result)):
            message = 'Saved current run to {}!'.format(self.thread.result)
        else:
            message = 'Save to failed. Returned {}'.format(self.thread.result)

        XtalWriter.make_message_box(message).exec_()

    def write_xtal_file(self, output_path):
        '''Method to serialize run object to xtal file format.

        :param output_path: Xtal file path
        :type output_path: str
        :return: path to xtal file
        :rtype: str
        '''
        if XtalWriter.path_validator(output_path, parent=True):
            # path is good to go and ready to write file into
            self.run.encode_images_to_base64()
            run_str = self.run_to_dict()
            if isinstance(run_str, str):  # encoding worked, no errors caught
                output_path = XtalWriter.path_suffix_checker(
                    output_path, self.file_ext)  # make sure has .xtal suffix
                try:
                    with open(str(output_path), 'w') as xtal_file:
                        xtal_file.write(self.xtal_header)
                        xtal_file.write(run_str)
                        return output_path
                except PermissionError as e:
                    return e

    def clean_run_for_save(self):
        '''Remove circular references from a Run instance to avoid errors
        when serializing using json. Uses the run stored in the run attribute

        :return: The cleaned run
        :rtype: Run
        '''
        # removes references to other runs so not to throw a
        # json encoding error
        if self.run:
            self.run.previous_run, self.run.next_run, self.run.alt_spectrum = (
                None, None, None)
            for image in self.run.images:
                if image:
                    image.previous_image, image.next_image, image.alt_image = (
                        None, None, None
                    )
        return self.run

    def run_to_dict(self):
        '''Create a json string from the run stored in the run attribute.

        :return: Run instance serialized to json
        :rtype: str
        '''
        if self.run:
            try:
                self.clean_run_for_save()
                self.run.encode_images_to_base64()
                return json.dumps(self.run, ensure_ascii=True, indent=4,
                                  default=XtalWriter.json_encoder)
            except (TypeError, FileNotFoundError,
                    IsADirectoryError, PermissionError) as e:
                # logger.warning('Failed to write {} to {} Gave {}'.format(
                #     run, output_path, e
                # ))
                return e


class RunDeserializer():  # convert saved file into a run

    def __init__(self, xtal_path):
        self.xtal_path = xtal_path

    @staticmethod
    def clean_base64_string(string):
        '''Image instances may contain byte strings that store their actual
        crystallization image encoded as base64. Previously, these byte strings
        were written directly into the json file as strings causing the b'
        byte string identifier to be written along with the actual base64 data.
        This method removes those artifacts if they are present and returns a
        clean byte string with only the actual base64 data.

        :param string: a string to interogate
        :type string: str
        :return: byte string with non-data artifacts removed
        :rtype: bytes
        '''
        if string:
            if string[0] == 'b':  # bytes string written directly to string
                string = string[1:]
            if string[-1] == "'":
                string = string[:-1]
            return bytes(string, 'utf-8')

    @staticmethod
    def dict_to_obj(our_dict):
        '''Oposite of the obj_to_dict method in XtalWriter class, this method
        takes a dictionary instance that has been previously serialized and
        attempts to convert it back into an object instance.

        :param our_dict: dictionary to convert back to object
        :type our_dict: dict
        :return: an object
        :rtype: object
        '''
        if our_dict:
            try:
                if "__class__" in our_dict:
                    class_name = our_dict.pop("__class__")
                    module_name = our_dict.pop("__module__")
                    module = __import__(module_name)
                    class_ = getattr(module, class_name)
                    our_dict_two = {}
                    for key, item in our_dict.items():
                        if '__' in key:
                            key = key.split('__')[-1]
                        elif '_' == key[0]:
                            key = key.replace('_', '')
                        our_dict_two[key] = item
                    obj = class_(**our_dict_two)
                else:
                    obj = our_dict
                return obj
            except NotADirectoryError as e:
                logger.error('Caught {} attempting to create object'.format(e))
                return None
        else:
            logger.warning(
                'Attempted to serialize an empty dictionary at {}'.format(dict_to_obj))
            return None

    def xtal_header_reader(self, xtal_file_io):
        '''Reads the header section of an open xtal file. Should always be
        called before reading the json content of an xtal file. Note than
        xtal files must always have a line of equal signs before the json
        content even if there is no header content otherwise this method will
        read one line into the json content causing the json reader to
        throw an error.

        :param xtal_file_io: xtal file currently being read
        :type xtal_file_io: TextIoWrapper
        :return: xtal header contents
        :rtype: list
        '''
        # pulls info in the header of an xtal file
        header_data = [xtal_file_io.readline()]
        while header_data[-1][0:len(XtalWriter.header_flag)] == XtalWriter.header_flag:
            header_data.append(xtal_file_io.readline())
        return header_data

    def xtal_to_run(self):
        '''Method that actually does the heavy lifting of converting the json
        contents of xtal files back into Run instances. Currently is pretty
        brittle and ugly so looking for a more flexible recursive solution.

        :raises e: Error raised while reading the xtal file
        :return: The contents of xtal file as a Run instance
        :rtype: Run
        '''
        logger.info('Attempting to load run from {}'.format(self.xtal_path))
        try:
            if os.path.isfile(self.xtal_path):
                with open(self.xtal_path) as xtal_data:
                    header_data = self.xtal_header_reader(
                        xtal_data)  # must read header first
                    j_d = json.load(xtal_data)
                run = RunDeserializer.dict_to_obj(j_d)

                run.date = datetime.strptime(
                    run.date, '%Y-%m-%d %H:%M:%S')
                for i, _ in enumerate(run.images):
                    run.images[i] = RunDeserializer.dict_to_obj(run.images[i])
                    run.images[i].bites = RunDeserializer.clean_base64_string(
                        run.images[i].bites)
                    if run.images[i]:
                        if run.images[i].date:
                            date = run.images[i].date
                            run.images[i].date = datetime.strptime(
                                date, '%Y-%m-%d %H:%M:%S')
                        reagents = []
                        if run.images[i].cocktail:
                            for j, _ in enumerate(run.images[i].cocktail['reagents']):
                                # holy mother of jank
                                run.images[i].cocktail['reagents'][j]['_Reagent__concentration'] = RunDeserializer.dict_to_obj(
                                    run.images[i].cocktail['reagents'][j]['_Reagent__concentration'])
                                reagents.append(RunDeserializer.dict_to_obj(
                                    run.images[i].cocktail['reagents'][j]))
                                # reagents[-1].concentration = RunDeserializer.dict_to_obj(
                                #     reagents[j].concentration)
                            run.images[i].cocktail = RunDeserializer.dict_to_obj(
                                run.images[i].cocktail)
                            run.images[i].cocktail.reagents = reagents
                return run  # TODO Interpret the header data
        except (json.JSONDecodeError, AttributeError, IsADirectoryError, PermissionError) as e:
            logger.error('Failed to read {} into run object at {}'.format(
                self.xtal_path, 'Place Holder'
            ))
            raise e


class BarTender():
    '''Class for organizing and accessing cocktail menus'''

    def __init__(self, cocktail_dir, cocktail_meta):
        '''Create instance of BarTender object. Probably only going to need
        to make one instance since the bartender should organize all
        available cocktail menus for the current Polo session. Currently,
        the BarTender instance that is used everywhere is declared in polo
        __init__ file.

        :param cocktail_dir: Path to directory holding cocktail menu files
        :type cocktail_dir: str
        :param cocktail_meta: Path to csv file containing cocktail menu metadata.units
        which includes things like when each menu was used, what kind.units
        of screens it was used for, etc.
        :type cocktail_meta: str
        '''
        self.cocktail_dir = cocktail_dir
        self.cocktail_meta = cocktail_meta
        self.menus = {}
        self.add_menus_from_metadata()

    @staticmethod
    def datetime_converter(date_string):
        '''General utility function for converting strings to datetime objects..units
            Attempts to convert the string by trying a couple of datetime.units
            formats that are common in cocktail menu files and other.units
            locations in the HWI file universe Polo runs across.

        :param date_string: string to convert to datetime
        :type date_string: str
        :return: datetime object
        :rtype: datetime
        '''
        date_string = date_string.strip()
        datetime_formats = ['%m/%d/%Y', '%m/%d/%y', '%m-%d-%Y', '%m-%d-%y']
        for form in datetime_formats:
            try:
                return datetime.strptime(date_string, form)
            except ValueError as e:
                continue

    @staticmethod
    def date_range_parser(date_range_string):
        '''Utility function for converting the date ranges in the cocktail.units
            metadata csv file to datetime objects using the `datetime_converter`
            classmethod.

            Date ranges should have the format

            start date - end date

            If the date range is for the most recent cocktail menu then there
            will not be an end date and the format will be

            start date - 

        :param date_range_string: string to pull dates out of   
        :type date_range_string: str
        :return: tuple of datetime objects, start date and end date
        :rtype: tuple
        '''
        s, e = date_range_string.split('-')
        s = BarTender.datetime_converter(s.strip())
        if e.strip():
            e = BarTender.datetime_converter(e.strip())
        else:
            e = None
        return s, e

    def add_menus_from_metadata(self):
        '''Adds menu objects to the menus attribute.'''
        if self.cocktail_meta:
            with open(str(self.cocktail_meta)) as menu_files:
                reader = csv.DictReader(menu_files)
                for row in reader:
                    path = os.path.join(
                        str(COCKTAIL_DATA_PATH), row['File Name'])
                    s, e = BarTender.date_range_parser(row['Dates Used'])
                    self.menus[path] = Menu(
                        path, s, e, row['Screen Type']
                    )
                    # add new menu to menus dict path to csv file is the menu
                    # key

    def get_menu_by_date(self, date, type_):
        '''Get a menu instance who's usage dates include the given date and
        match the given screen type.

        Screen types can either be 's' for 'soluble' screens or 'm' for
        membrane screens.

        :param date: Date to search menus with
        :type date: datetime
        :param type_: Type of screen to return (soluble or membrane)
        :type type_: str
        :return: menu matching the given date and type
        :rtype: Menu
        '''
        if isinstance(date, datetime):
            # search for a menu whos usage dates include this date
            menus_keys_by_date = sorted(
                [key for key in self.menus.keys() if self.menus[key].type_ == type_],
                # keys matching only the specified type
                key=lambda key: self.menus[key].start_date
            )
            # end up with a list of keys for menus of the specified type that
            # are sorted by the start date of their use at HWI cente
            for each_key in menus_keys_by_date:
                if date < self.menus[each_key].start_date:
                    return self.menus[each_key]
            return self.menus[menus_keys_by_date[-1]]

    def get_menus_by_type(self, type_):
        '''Returns all menus of a given screen type.

        's' for soluble screens and 'm' for membrane screens. No other
        characters should be passed to `type_`.

        :param type_: Key for type of screen to return
        :type type_: str (max length 1)
        :return: list of menus of that screen type
        :rtype: list
        '''

        return [menu for menu in self.menus.values() if menu.type_ == type_]

    def get_menu_by_path(self, path):
        '''Returns a menu by its file path, which is used as the key
        for accessing the menus attribute normally.

        :param path: file path of a menu csv file
        :type path: str
        :return: Menu instance that is mapped to given path
        :rtype: Menu
        '''
        if path in self.menus:
            return self.menus[path]


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
        '''Create a CocktailMenuReader instance, which is basically a
        csv.reader instance with extra steps. The iterator returns Cocktail
        instances instead or lists so when creating Menus, the csv file that
        holds the cocktail data can be read directly ad Cocktail instances
        instead of dealing with converting the rows to Cocktails when creating
        Menus.

        :param menu_file: Path to cocktail menu file to read. Should be csv
                          formated
        :type menu_file: str or Path 
        :param delim: Seperator for menu_file; really should not need to 
                      be changed, defaults to ','
        :type delim: str, optional
        '''
        self.menu_file = menu_file
        self.reader = csv.reader(self.menu_file)
        self.delim = delim
        self.__row_counter = 0
        self.__dict__.update(kwargs)

    @classmethod
    def set_cocktail_map(cls, map):
        '''Classmethod to edit the cocktail_map. The cocktail map describes
        where Cocktail level information is stored in a given cocktail menu
        file row. It is a dictionary that maps specific indicies in a row to
        the Cocktail attribute to set the value of the key index to.

        The default cocktail_map dictionary is below.

        cocktail_map = {
        0: 'well_assignment',
        1: 'number',
        8: 'pH',
        2: 'commercial_code'
        }

        This tells instances of CocktailMenuReader to look at index 0 of a row
        for the well_assignment attribute of the Cocktail class, index 1 for
        the number attribute of the Cocktail class, etc.

        :param map: Dictionary mapping csv row indicies to Cocktail object
                    attributes
        :type map: dict
        '''
        cls.cocktail_map = cocktail_map

    @classmethod
    def set_formula_pos(cls, pos):
        '''Classmethod to change the formula_pos attribute. The formula_pos
        describes the location (base 0) of the chemical formula in a row of
        a cocktail menu file csv. For some reason, HWI cocktail menu files
        will only have one chemical formula per row (cocktail) no matter
        the number of reagents that composite that cocktail. This is why
        its location is represented using an int instead of a dict.

        Generally, formula_pos should not be changed without a very good
        reason as the position of the chemical formula is consistent across
        all HWI cocktail menu files.

        :param pos: Index where chemical formula can be found
        :type pos: int
        '''
        cls.formula_pos = pos

    @property
    def menu_file(self):
        '''Get the instances menu file

        :return: the menu file path
        :rtype: str or Path or IO
        '''
        return self.__menu_file

    @menu_file.setter
    def menu_file(self, new_file):
        '''Setter method for the menu_file attribute. If the value passed in
        is a string will open the file, iterate over the first two lines as
        these are header lines in all the HWI cocktail menu files included with
        Polo and set menu_file to the IO stream.

        :param new_file: [description]
        :type new_file: [type]
        '''
        if isinstance(new_file, str):
            self.__menu_file = open(new_file)
            next(self.__menu_file)
            next(self.__menu_file)  # skip first two rows
        else:
            self.__menu_file = new_file

    # need to deciede how fixed on the current header system want to be
    def __next__(self):  # would be nice if returned a cocktail
        '''Dictates the behavior of CocktailMenuReader objects when `next`
        is called. Uses the csv.reader object stored in the reader attribute
        to get the next row of the csv file in a consistent way and then
        converts the information in that row to a Cocktail object.

        :return: Cocktail instance representing the cocktail at the next row of
                 the menu_file
        :rtype: Cocktail
        '''
        row = next(self.reader)
        d = {self.cocktail_map[index]: row[index]
             for index in self.cocktail_map}
        c = Cocktail(**d)
        reagent_pos = [i for i in range(
            len(row)) if i not in self.cocktail_map and i != self.formula_pos]
        # positions that should contain reagent information. Additionally,
        # reagent names and their concentrations should now be adjacent to
        # each other in the list of indicies
        for i in range(0, len(reagent_pos), 2):
            chem_add, con = row[reagent_pos[i]], row[reagent_pos[i+1]]
            if chem_add:
                con = SignedValue.make_from_string(con)
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


class Menu():  # holds the dictionary of cocktails

    def __init__(self, path, start_date, end_date, type_):
        '''Creates a Menu instance. Menu objects are used to organize a single
        screening run plate set up. They should contain 1536 unique screening
        conditions; one for each well in the HWI highthrouput plate. HWI
        has altered what cocktails are used in each of the 1536 wells over the
        years and so many versions of cocktail menus have been used. A single
        Menu instance represents one of these versions and accordingly has a
        start and end date to identify when the menu was used. Additionally, 
        HWI offers two types of high throughput screens; membrane or solulbe
        screens. Both use 1536 well plates but have very different chemical
        conditions at the same well index. 

        Menus that hold conditions for soluble screens are the `type_`
        attribute set to 's' and menus that hold conditions for membrane
        screens have the `type_` attribute set to 'm'.

        :param path: Location of the menu csv file
        :type path: str
        :param start_date: Date when this screen menu was first used
        :type start_date: datetime
        :param end_date: Last date this screen menu was used
        :type end_date: datetime
        :param type_: Membrane or soluble screen
        :type type_: str
        '''
        self.start_date = start_date
        self.end_date = end_date
        self.type_ = type_
        self.__cocktails = {}  # holds all cocktails (items on the menu)
        self.path = path

    @property
    def cocktails(self):
        '''Property to return the Menu instance's cocktail dict

        :return: cocktail attribute
        :rtype: dict
        '''
        return self.__cocktails

    @property
    def path(self):
        '''Property to return the Menu instance's path attribute

        :return: The path attribute
        :rtype: str or IO
        '''
        return self.__path

    @path.setter
    def path(self, new_path):
        '''Setter function for path attribute. Creates an instance of
        a CocktailMenuReader class and passes the path attribute to it.
        Then uses the CocktailMenuReader instance to read the contents of
        the new_path (which should be a csv file) as Cocktail objects.
        Cocktail instances are added to the __cocktail dict by their
        well number assignemnt.

        :param new_path: [description]
        :type new_path: [type]
        '''
        self.__path = new_path  # set the path to the new_path
        cocktail_reader = CocktailMenuReader(self.path)
        for cocktail in cocktail_reader:
            self.cocktails[cocktail.well_assignment] = cocktail
        # create dictionary from cocktails, key is the well number (assignment)


# orphan functions that have not made it into a class yet
# =============================================================================


def write_screen_html(plate_list, well_number, run_name, x_reagent,
                      y_reagent, well_volume, output_path):

    template = SCREEN_HTML_TEMPLATE
    template_string = open(str(SCREEN_HTML_TEMPLATE)).read()
    template = Template(template_string)

    html = template.render(plate_list=plate_list, run_name=run_name,
                           well_number=well_number, date=datetime.now(),
                           x_reagent_stock=x_reagent,
                           y_reagent_stock=y_reagent,
                           well_volume=str(well_volume))

    output_path = Path(str(output_path))
    if output_path.suffix != '.html':
        output_path = str(output_path.with_suffix('.html'))

    with open(str(output_path), 'w') as screen_html:
        screen_html.write(html)


def make_dict_from_run_via_json(run):
    return json.loads(json.dumps(run, default=encoder))


def get_cocktail_number_as_int(cocktail_number_string):
    return int(cocktail_number_string.split('_C')[-1].lstrip('0'))


def parse_HWI_filename_meta(HWI_image_file):
    '''
    HWI images have a standard file nameing schema that gives info about when
    they are taken and well number and that kind of thing. This function returns
    that data
    '''
    HWI_image_file = os.path.basename(HWI_image_file)
    return (
        HWI_image_file[:10],
        int(HWI_image_file[10:14].lstrip('0')),
        datetime.strptime(HWI_image_file[14:22], '%Y''%m''%d'),
        HWI_image_file[22:]
    )


def export_run_to_csv(run, output_path):
    output_path = str(output_path)
    csv_data = []
    for image in run.images:
        if image:
            pass


def get_available_cocktails():  # change this to parse metadata
    '''
    Returns a list of cocktail csv files that are included with the Polo
    program. List is sorted from most recently used cocktails to least 
    recently used. The year the cocktails were first used are the first two
    characters of the csv file name if downloaded from HWI website.

    TODO: Inculde metadata file on available cocktails that gives when they
    were used at the screening center. Add another function to read in that
    metadata and create dialog so user can select cocktail that would go with
    their screen.

    NOTE: Cocktail TSV file had unicode error in it when read using UTF-8
    incoding but one on webiste did not. Need to ask Bowman about that one.
    '''
    cocktail_paths = list_dir_abs(COCKTAIL_DATA_PATH)
    return [parse_cocktail_csv(csv_path) for csv_path in sorted(cocktail_paths,
                                                                key=lambda x: os.path.basename(x.split('_')[0]))]
    # returns list of dictionaries


def list_dir_abs(parent_dir, allowed=False):
    files, allowed_files = os.listdir(parent_dir), []
    for f in files:
        abs_file_path = os.path.join(parent_dir, f)
        if allowed:
            ext = os.path.splitext(f)[-1]
            if ext in ALLOWED_IMAGE_TYPES:
                allowed_files.append(Path(abs_file_path))
        else:
            allowed_files.append(Path(abs_file_path))

    return allowed_files


def parse_reagents(row):
    reagents = []
    formula = row[4]
    row = [i.strip() for i in [row[3]] + row[5:8] + row[9:]]
    row = [i for i in row if i]
    if len(row) > 1:
        for i in range(0, len(row), 2):
            con, units = row[i+1].split(' ')[0], row[i+1].split(' ')[-1]
            if row[i]:  # some solutions without units all have additive name
                reagents.append(Reagent())
                reagents[-1].chemical_additive = row[i]
                con = num_regex.findall(con)[0]
                units = unit_regex.findall(units)[0]
                reagents[-1].concentration = SignedValue(con, units)

        if formula:
            reagents[0].chemical_formula = formula

    return reagents


def parse_cocktail_csv(file_path):
    cocktail_dict = {}
    try:
        with open(file_path, 'r') as cocktails:
            reader = csv.reader(cocktails, delimiter=',')
            for row in reader:
                try:
                    well_pos, number, commercial_code = row[:3]
                    well_pos = int(round(float(well_pos)))
                    pH = row[8]
                    cocktail_dict[well_pos] = Cocktail(number=number,
                                                       well_assignment=well_pos,
                                                       commercial_code=commercial_code,
                                                       pH=pH)
                    cocktail_dict[well_pos].reagents = parse_reagents(row)
                except (IndexError, TypeError, ValueError) as e:
                    logger.warning('Caught {} at {} attempting to read {}'.format(
                        e, parse_cocktail_csv, file_path
                    ))
                    continue
        logger.info('Successfully parsed cocktail file at {}'.format(file_path))
        return cocktail_dict
    except FileNotFoundError as e:
        logger.error('Caught {} at {} attempting to open {}'.format(
            e, parse_cocktail_csv, file_path
        ))
        return e


# attempts to convert date string using bunch of formats
def datetime_converter(date_string):
    date_string = date_string.strip()
    datetime_formats = ['%m/%d/%Y', '%m/%d/%y', '%m-%d-%Y', '%m-%d-%y']
    for form in datetime_formats:
        try:
            return datetime.strptime(date_string, form)
        except ValueError as e:
            continue


def parse_hwi_dir_metadata(dir_name):
    try:
        dir_name = os.path.basename(dir_name)
        image_type = dir_name.split('-')[-1]
        plate_id = dir_name[:10]
        date = datetime.strptime(dir_name[10:].split('-')[0],
                                 '%Y''%m''%d''%H''%M')

        return image_type, plate_id, date, dir_name  # last is suggeseted run name
    except ValueError as e:
        logger.error('Caught {} at {} attempting to parse {}'.format(
            e, parse_hwi_dir_metadata, dir_name
        ))
        return e


def parse_cocktail_metadata():
    # parse the metadata csv file into a dictionary of cocktail csv files
    cocktail_dict = {}
    dates_header = 'Dates Used'
    path_header = 'File Name'
    data = COCKTAIL_META_DATA.read_text()
    try:
        with open(str(COCKTAIL_META_DATA)) as meta_cock:
            reader = csv.DictReader(meta_cock)
            for row in reader:
                dates = row[dates_header]
                start, end = dates.split('-')
                if start:  # convert dates to datetime
                    start = datetime_converter(start)
                if end:
                    try:
                        end = datetime_converter(end)
                    except ValueError as e:
                        logger.warning('Caught {} at {}'.format(
                            e, parse_cocktail_metadata))
                row[dates_header] = (start, end)
                file_name = os.path.basename(row[path_header]).split('.')[0]
                cocktail_dict[file_name] = row

        return cocktail_dict

    except (FileNotFoundError, TypeError) as e:
        logger.error('Caught {} at {}'.format(e, parse_cocktail_metadata))
        logger.debug(data)
        return e


def read_import_descriptors():
    pass


def directory_validator(dir_path):
    if os.path.exists(dir_path):
        if os.path.isdir(dir_path):
            files = list_dir_abs(dir_path, allowed=True)
            if files:
                return True
            else:
                e = ForbiddenImageTypeError
                logger.warning('Directory validation failed with {}'.format(e))
                return e
        else:
            e = NotADirectoryError
            logger.warning('Directory validation failed with {}'.format(e))
            return e
    else:
        e = FileNotFoundError
        logger.warning('Directory validation failed with {}'.format(e))
        return FileNotFoundError


def check_for_missing_images(dir_path, expected_image_count):
    number_images = len(list_dir_abs(dir_path, allowed=True))
    if number_images != expected_image_count:
        return False
    else:
        return True


def run_name_validator(new_run_name, current_run_names):
    # checks that new run name is utf 8 and
    try:
        new_run_name = new_run_name.encode('utf-8')
        new_run_name = new_run_name.decode('utf-8')
    except UnicodeError as e:
        logger.info('{} failed run name validation with {}'.format(
            new_run_name, e
        ))
        return e
    if new_run_name == '' or new_run_name == None:
        return TypeError
    if new_run_name not in current_run_names:
        return True
    else:
        return False


def if_dir_not_exists_make(parent_dir, child_dir=None):
    '''
    If only parent_dir is given attempts to make that directory. If parent
    and child are given tries to make a directory child_dir within parent dir.
    '''
    if child_dir:
        path = os.path.join(parent_dir, child_dir)
    else:
        path = parent_dir

    if not os.path.exists(path):
        try:
            os.mkdir(path)
        except FileNotFoundError as e:
            logger.warning('Could not make directory with path {}. Returned {}'.format(
                path, e
            ))
            return e

    return path
