import base64
import csv
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

from pptx import Presentation
from pptx.util import Inches, Pt

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QIcon, QPixmap, QImage, QPainter
from PyQt5.QtWidgets import QAction, QApplication, QGridLayout

from jinja2 import Template
from polo import *
from polo import __version__
from polo.threads.thread import QuickThread
from polo.utils.exceptions import EmptyRunNameError, ForbiddenImageTypeError
from polo.crystallography.image import Image
from polo.crystallography.cocktail import *
from polo.utils.dialog_utils import *
from polo.utils.unrar_utils import *
from polo.utils.math_utils import *



logger = make_default_logger(__name__)

class RunImporter():

    @staticmethod
    def directory_validator(dir_path):
        dir_path = str(dir_path)
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
    
    @staticmethod
    def parse_HWI_filename_meta(HWI_image_file):
        '''
        HWI images have a standard file nameing schema that gives info about when
        they are taken and well number and that kind of thing. This function returns
        that data
        '''
        HWI_image_file = os.path.basename(str(HWI_image_file))
        return (
            HWI_image_file[:10],
            int(HWI_image_file[10:14].lstrip('0')),
            datetime.strptime(HWI_image_file[14:22], '%Y''%m''%d'),
            HWI_image_file[22:]
        )

    @staticmethod
    def parse_hwi_dir_metadata(dir_name):
        try:
            dir_name = str(Path(dir_name).with_suffix('').name)
            image_type = dir_name.split('-')[-1].strip()
            if image_type in SPEC_KEYS:
                image_spectrum = SPEC_KEYS[image_type]
            else:
                image_spectrum = IMAGE_SPECS[0]  # default to visible
            plate_id = dir_name[:10]
            date = datetime.strptime(dir_name[10:].split('-')[0],
                                    '%Y''%m''%d''%H''%M')
            
            #return image_type, plate_id, date, run_name  # last is suggeseted run name
            return {
                'image_spectrum': image_spectrum,
                'plate_id': plate_id,
                'date': date,
                'run_name': dir_name
                }

        except Exception as e:
            logger.error('Caught {} at {} attempting to parse {}'.format(
                e, RunImporter.parse_hwi_dir_metadata, dir_name
            ))
            return False
    
    @staticmethod
    def crack_open_a_rar_one(rar_path):
        if not isinstance(rar_path, Path):
            rar_path = Path(rar_path)
        parent_path = rar_path.parent
        return unrar_archive(rar_path, parent_path)
    
    @staticmethod
    def import_from_xtal_thread(xtal_path):
        reader = RunDeserializer(xtal_path)
        if os.path.isfile(xtal_path):
            return reader.make_read_xtal_thread()
    
    @staticmethod
    def make_xtal_file_dialog(parent=None):
        file_dlg = QtWidgets.QFileDialog(parent=parent)
        file_dlg.setNameFilter('xtal or xtals (*.xtal *.xtals)')
        return file_dlg
    
    @staticmethod
    def unpack_rar_archive_thread(archive_path):
        archive_path = str(archive_path)
        if os.path.exists(archive_path) and Path(archive_path).suffix == '.rar':
            return QuickThread(job_func=RunImporter.crack_open_a_rar_one, rar_path=archive_path)

    @staticmethod
    def import_run_from_directory(data_dir, **kwargs):
        hwi_import_attempt = RunImporter.import_hwi_run(data_dir, **kwargs)
        if isinstance(hwi_import_attempt, HWIRun):
            return hwi_import_attempt
        else:
            return RunImporter.import_general_run(data_dir, **kwargs)

    @staticmethod
    def import_hwi_run(data_dir, **kwargs):
        if RunImporter.directory_validator(data_dir) == True:
            from polo import tim
            metadata = XmlReader().find_and_read_plate_data(data_dir)
            file_name_data = RunImporter.parse_hwi_dir_metadata(data_dir)

            if metadata and file_name_data:
                image_type, plate_id, date, run_name = file_name_data
                menu = tim.get_menu_by_date(date, 's')
                new_run = HWIRun(
                    image_dir=data_dir, run_name=run_name, cocktail_menu=menu,
                    image_spectrum=image_type, date=date
                )
                new_run.__dict__.update(metadata)  # from xml data
                new_run.__dict__.update(kwargs)  # for user supplied data
                # that could overwrite what is in metadata
                new_run.add_images_from_dir()
                return new_run
        else:
            return False

    @staticmethod
    def import_general_run(data_dir, **kwargs):
        if RunImporter.directory_validator(data_dir) == True:
            # add some rule if does not have run name and spectru
            new_run = Run(image_dir=data_dir, **kwargs)
            new_run.add_images_from_dir()
            return new_run

    @staticmethod
    def validate_run_name(text=None):
        '''
        Validates a given run name to ensure it can be used safely. Shows
        an error message to the user if the run name is not valid and clears
        the run name lineEdit widget.

        In order for a run name to be valid it must contain only UTF-8
        codable characters and not already be in use by another
        run object. This is because the run name is used as a key to refer
        to the run object in other functions.

        :param text: String. The run name to be validated.
        '''
        validator_result = run_name_validator(text, self.current_run_names)
        message = None
        if validator_result == UnicodeError:
            message = 'Run name is not UTF-8 Compliant'
        elif validator_result == TypeError:
            message = 'Run name must not be empty.'
        elif not validator_result:  # result is false already exists
            message = 'Run name already exists, please pick a unique name.'
            # TODO option to overwrite the run of that same name
        
        if message:
            return make_message_box(message).exec_()
        else:
            return True

        # def read_xml_data(self, dir_path):
        #     # read xml data from HWI uncompressed rar files
        #     reader = XmlReader(dir_path)
        #     plate_data = reader.find_and_read_plate_data(dir_path)
        #     if isinstance(plate_data, dict) and plate_data:
        #         return plate_data
        #     else:
        #         return {}  # empty dict so always safe to pass to update method


class RunSerializer():

    def __init__(self, run):
        self.run = run
        logger.info('Made RunSerializer {}'.format(self))

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
        try:
            if desired_suffix:
                if isinstance(path, str):
                    path = Path(path)
                if path.suffix == desired_suffix:
                    return str(path)
                else:
                    return str(path.with_suffix(desired_suffix))
        except Exception as e:
            return None

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
        if isinstance(template_path, Path):
            template_path = str(template_path)

        with open(template_path, 'r') as template:
            contents = template.read()
            return Template(contents)

    def write_complete_run(self, output_path, encode_images=True):
        # write a run as html file with images and classifications
        # and that kind of stuff
        if HtmlWriter.path_validator(output_path, parent=True) and self.run:
            output_path = HtmlWriter.path_suffix_checker(output_path, '.html')
            if output_path:
                if encode_images:
                    self.run.encode_images_to_base64()
                images = json.loads(json.dumps(
                    self.run.images, default=XtalWriter.json_encoder))
                [RunDeserializer.clean_base64_string(image['_Image__bites'], str) for image in images]

                template = HtmlWriter.make_template(RUN_HTML_TEMPLATE)
                if template:
                    try:
                        html = template.render(
                            images=images, run_name=self.run.run_name,
                            annotations='No annotations')
                        with open(output_path, 'w') as html_file:
                            html_file.write(html)
                            return True
                    except Exception as e:
                        return e

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
            output_path = HtmlWriter.path_suffix_checker(output_path, '.html')
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


class RunCsvWriter(RunSerializer):

    def __init__(self, run, output_path=None, **kwargs):
        self.__dict__.update(kwargs)
        self.output_path = output_path
        super(RunCsvWriter, self).__init__(run)

    @classmethod
    def image_to_row(cls, image):
        '''Given an Image object, convert it into a list that could be
        easily written to a csv file.

        :param image: Image object to convert to list
        :type image: Image
        :return: List
        :rtype: list
        '''
        row = {}
        for attr, value in image.__dict__.items():
            if isinstance(value, Cocktail):
                row[attr] = value.number
            elif isinstance(value, Image):
                row[attr] = value.path
            elif isinstance(value, dict):
                # unwrap the dict
                for attr_b, value_b in value.items():
                    if attr_b not in row:  # only add if will not override higher level attr
                        # only go one level deep for now
                        row[attr_b] = str(value_b)
            elif isinstance(value, bytes):
                continue  # currently do not encode bytes (base 64 stuff)
            else:
                row[attr] = str(value)  # default to case to string
        return row

    @property
    def output_path(self):
        '''Get the hidden attribute `__output_path`.

        :return: Output path
        :rtype: str
        '''
        return self.__output_path

    @property
    def fieldnames(self):  # could use more efficent way of determining feildnames
        '''Get the current fieldnames bases on the data stored in the
        `run` attribute. Currently is somewhat expensive to call since it
        requires parsing all records in `run` in order to determine all the
        fieldnames that should be included in order to definitely avoid
        keyerrors later down the line.

        :return: List of fieldnames (headers) for the csv data 
        :rtype: list
        '''
        rows = [row for row in self]
        fieldnames = set([])
        for row in rows:
            fieldnames = fieldnames.union(set(row.keys()))

        return fieldnames

    @output_path.setter
    def output_path(self, new_path):
        if isinstance(new_path, Path):
            new_path = str(new_path)

        self.__output_path = new_path

    def get_csv_data(self):
        '''Convert the `run` attribute to csv style data. Returns a tuple of
        headers and a list of dictionaries with each dictionary representing
        one row of csv data.

        :raises e: Catch all exception. TODO: Make more specific
        :return: Tuple, list of headers and list of dicts
        :rtype: tuple
        '''
        try:
            rows = [row for row in self]
            fieldnames = set([])
            for row in rows:
                fieldnames = fieldnames.union(set(row.keys()))
            return fieldnames, rows
        except Exception as e:
            raise e  # pass it along will ya

    def write_csv(self):
        '''Write the Run object stored in the `run` attribute as a csv file
        to the location specified by the `output_path` attribute. 

        :return: True, if csv file content was written successfully,
                 return error thrown otherwise.
        :rtype: Bool or Exception
        '''
        try:
            rows = [row for row in self]
            fieldnames = set([])
            for row in rows:
                fieldnames = fieldnames.union(set(row.keys()))
            with open(self.output_path, 'w') as csv_path:
                writer = csv.DictWriter(csv_path, fieldnames)
                writer.writeheader()
                for row in rows:
                    writer.writerow(row)
            return True
        except Exception as e:
            logger.warning(
                'Caught exception {} at {}'.format(e, self.write_csv))
            return e

    def __iter__(self):
        for image in self.run.images:
            yield RunCsvWriter.image_to_row(image)

class SceneExporter():

    def __init__(self, graphics_scene=None, file_path=None):
        self.graphics_scene = graphics_scene
        self.file_path = file_path
    
    @staticmethod
    def write_image(scene, file_path):
        try:
            image = QImage(scene.width(), scene.height(), QImage.Format_ARGB32_Premultiplied)
            painter = QPainter(image)
            scene.render(painter)
            image.save(file_path)
            painter.end()
            return file_path
        except Exception as e:
            return e
    
    def write(self):
        return SceneExporter.write_image(self.graphics_scene, self.file_path)


class MsoWriter(RunSerializer):

    mso_version = 'msoversion2'

    def __init__(self, run, output_path):
        self.run = run
        self.output_path = output_path

    @staticmethod
    def row_formater(cocktail_row):
        # well number should be first index in the list
        # total list length should be 18 last item is the mso code
        return cocktail_row + ([''] * (len(cocktail_row) - 17))

    
    @property
    def first_line(self):
        return [
            MsoWriter.path_suffix_checker(self.run.run_name, '.rar'), 
            self.mso_version
        ]
    
    def get_cocktail_csv_data(self):
        cocktail_menu = self.run.cocktail_menu.path
        with open(cocktail_menu, 'r') as menu_file:
            next(menu_file)  # skip first row
            return [row for row in csv.reader(menu_file)]

    def write_mso_file(self, use_marco_classifications=False):
        if isinstance(self.run, HWIRun):  # must be hwi run to write to mso
            cocktail_data = self.get_cocktail_csv_data()
            self.output_path = str(MsoWriter.path_suffix_checker(self.output_path, '.mso'))
            with open(self.output_path, 'w') as mso_file:
                writer = csv.writer(mso_file, delimiter='\t')
                writer.writerow(self.first_line)
                writer.writerow(cocktail_data.pop(0))  # header row
                for row in cocktail_data:
                    row = MsoWriter.row_formater(row)
                    well_num = int(float(row[0]))

                    image = self.run.images[well_num-1]
                    if image and image.human_class:
                        row.append(MSO_DICT[image.human_class])
                    elif use_marco_classifications and image.machine_class:
                        row.append(MSO_DICT[image.machine_class])
                    else:
                        row.append(MSO_DICT[IMAGE_CLASSIFICATIONS[3]])
                    writer.writerow(row)
            return True
        else:
            return False
            



class XtalWriter(RunSerializer):
    header_flag = '<>'  # do not change unless very good reason
    header_line = '{}{}:{}\n'
    file_ext = '.xtal'

    def __init__(self, run, main_window, **kwargs):
        self.__dict__.update(kwargs)
        self.main_window = main_window
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
        self.main_window.setEnabled(False)
        self.thread.start()

    def finished_save(self):
        self.main_window.setEnabled(True)
        QApplication.restoreOverrideCursor()  # return cursor to normal
        # should contain path to now saved file
        if os.path.exists(str(self.thread.result)):
            message = 'Saved current run to {}!'.format(self.thread.result)
        else:
            message = 'Save to failed. Returned {}'.format(self.thread.result)

        XtalWriter.make_message_box(message).exec_()

    def write_xtal_file(self, output_path=None):
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
                    logger.warning('Caught {} at {}'.format(
                        e, self.write_xtal_file))
                    return e

    def clean_run_for_save(self):
        '''Remove circular references from a Run instance to avoid errors
        when serializing using json. Uses the run stored in the run attribute

        :return: The cleaned run
        :rtype: Run
        '''
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
                logger.warning('Failed to encode {} to dict. Gave {}'.format(
                    self.run, e))
                return e


class RunDeserializer():  # convert saved file into a run

    def __init__(self, xtal_path):
        self.xtal_path = xtal_path

    @staticmethod
    def clean_base64_string(string, out_fmt=bytes):
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
            if isinstance(string, bytes):
                string = str(string, 'utf-8')
            if string[0] == 'b':  # bytes string written directly to string
                string = string[1:]
            if string[-1] == "'":
                string = string[:-1]
            if string: 
                if isinstance(out_fmt, bytes):
                    return bytes(string, 'utf-8')
                else:
                    return string
            

    @staticmethod
    def dict_to_obj(d):
        '''Opposite of the obj_to_dict method in XtalWriter class, this method
        takes a dictionary instance that has been previously serialized and
        attempts to convert it back into an object instance. Used as the
        `object_hook` argument when calling `json.loads` to read xtal files.

        :param d: dictionary to convert back to object
        :type d: dict
        :return: an object
        :rtype: object
        '''
        if d:
            if '__class__' in d:  # is a serialized object
                class_name, mod_name = d.pop('__class__'), d.pop('__module__')
                try:
                    module = __import__(mod_name)
                    class_ = getattr(module, class_name)
                except AttributeError:
                    return None
                temp_d = {}
                for key, item in d.items():
                    if '__' in key:  # deal with object properties
                        key = key.split('__')[-1]
                    elif '_' == key[0]:
                        key = key.replace('_', '')
                    temp_d[key] = item
                obj = class_(**temp_d)

                if isinstance(obj, Image):  # clean up base64 encoded data
                    if obj.bites:
                        obj.bites = RunDeserializer.clean_base64_string(
                            obj.bites)
            else:
                obj = d  # just a regular dictionary to read in
            return obj
        else:
            logger.warning(
                'Attempted to serialize an empty dictionary at {}'.format(dict_to_obj))
            return None

    def xtal_to_run_on_thread(self):
        '''Wrapper method around `xtal_to_run` method. Does the exact same thing
        except creates a `QuickThread` instance and runs `xtal_to_run` on the
        thread. When finished adds the newly created run to the main window's
        loaded_run dictionary to signify that the run has been loaded and is
        ready for further operations.
        '''
        return QuickThread(self.xtal_to_run, xtal_path=self.xtal_path)

        # def finished():
        #     self.main_window.add_loaded_run(thread.result)

        # thread.finished.connect(finished)
        thread.start()

    def make_read_xtal_thread(self):
        return QuickThread(self.xtal_to_run, xtal_path=self.xtal_path)

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

    def xtal_to_run(self, **kwargs):
        '''Attempt to convert the file specified by the path stored in the
        `xtal_path` attribute to a Run object. 

        :return: Run object encoded by an xtal file
        :rtype: Run
        '''
        try:
            if 'xtal_path' in kwargs:
                xtal_path = kwargs['xtal_path']
            else:
                xtal_path = self.xtal_path
            if os.path.isfile(str(xtal_path)):
                with open(xtal_path) as xtal_data:
                    header_data = self.xtal_header_reader(
                        xtal_data)  # must read header first
                    r = json.load(xtal_data,  # update date since datetime goes right to string
                                object_hook=RunDeserializer.dict_to_obj)
                    r.date = BarTender.datetime_converter(r.date)
                    r.save_file_path = xtal_path
                    return r
            else:
                return FileNotFoundError
        except Exception as e:
            return e
class PptxWriter():

    # 13.33 x 7.5 
    def __init__(self, output_path, included_attributes={},
                 image_types = None, human=False, marco=False, favorite=False):
        self.output_path = output_path
        self.included_attributes = included_attributes
        self.human = human
        self.marco = marco
        self.favorite = favorite
        self.image_types = image_types
        self.__temp_images = []
        self.__bumper = 1
        self.__slide_width = 10
        self.__slide_height = 6
        self.__presentation = Presentation()
    
    def delete_presentation(self):
        self.__presentation = Presentation()
    
    def delete_temp_images(self):
        try:
            [os.remove(img_path) for img_path in self.__temp_images]
            return True
        except (FileNotFoundError, IsADirectoryError, PermissionError) as e:
            return e
    
    def sort_runs_by_spectrum(self, runs):
        visible, other = [], []
        for run in runs:
            if run.image_spectrum == IMAGE_SPECS[0]:
                visible.append(run)
            else:
                other.append(run)
        return visible, other
           
    def make_sample_presentation(self, sample_name, runs, title, subtitle, cocktail_data=True):
        visible, other = self.sort_runs_by_spectrum(runs)
        title_slide = self.add_new_slide(0)
        title_slide.shapes.title.text = title
        if subtitle:
            title_slide.placeholders[1].text = subtitle

        if visible or other:
            show_all_dates, show_single_image, show_alt_specs = False, False, False
            if visible:
                if len(visible) > 1:
                    show_all_dates = True
                else:
                    show_single_image = True
            if other:
                show_alt_specs = True

            if show_all_dates or show_single_image:
                rep_run = visible[0]
            else:
                rep_run = other[0]
            
            for i in range(10):
                if show_all_dates:
                    self.add_timeline_slide([r.images[i] for r in visible], i+1)
                elif show_single_image:
                    metadata = str(rep_run.images[i])
                    if hasattr(rep_run.images[i], 'cocktail') and cocktail_data:
                        metadata += '\n\n' + str(rep_run.images[i].cocktail)
                    title = 'Well Number {}'.format(rep_run.images[i].well_number)
                    self.add_single_image_slide(rep_run.images[i], title, metadata)
                
                if show_alt_specs:
                    well_number = i + 1
                    self.add_multi_spectrum_slide([r.images[i] for r in other], well_number)
            
            self.__presentation.save(str(self.output_path))
            self.delete_temp_images()
                
        else:
            return False
        

    def make_single_run_presentation(self, run, title, subtitle=None, cocktail_data=True):
        title_slide = self.add_new_slide(0)
        title_slide.shapes.title.text = title
        if subtitle:
            title_slide.placeholders[1].text = subtitle
        
        slide_title_formater = 'Well Number {}'
        for image in run.images:
            if image.standard_filter(self.image_types, self.human, self.marco, self.favorite):
                metadata = str(image)
                if cocktail_data and hasattr(image, 'cocktail'):
                    metadata += '\n\n' + str(image.cocktail)
                self.add_single_image_slide(
                    image, 
                    slide_title_formater.format(image.well_number),
                    metadata=metadata
                    )
        
        self.output_path = RunSerializer.path_suffix_checker(self.output_path, '.pptx')
        self.__presentation.save(str(self.output_path))
        self.delete_temp_images()
                
    
    def add_classification_slide(self, well_number, rep_image):
        new_slide = self.add_new_slide()
        title = 'Well {} Classifications'.format(well_number)
        new_slide.shapes.title.text = title

        data = [
            ['Human Classification', 'MARCO Classification']
            [rep_image.human_class, rep_image.machine_class]
        ]

        self.add_table_to_slide(new_slide, data, self.__bumper, 2)
        # do for most recent human classification image if it exits

    def add_new_slide(self, template=5):
        return self.__presentation.slides.add_slide(
            self.__presentation.slide_layouts[template])
    
    def add_timeline_slide(self, images, well_number):
        date_images = sorted(images, key=lambda i: i.date)
        new_slide = self.add_new_slide()
        labeler = lambda i: i.formated_date
        self.add_multi_image_slide(new_slide, images, labeler)
        title = 'Well {}: {} - {}'.format(
            well_number, date_images[0].formated_date, date_images[-1].formated_date)
        new_slide.shapes.title.text = title

        return new_slide
    

    def add_multi_spectrum_slide(self, images, well_number):
        spec_images = sorted(images, key=lambda i: len(i.spectrum))
        new_slide = self.add_new_slide()
        labeler = lambda i: i.spectrum
        self.add_multi_image_slide(new_slide, images, labeler)
        title = 'Well {} Alternate Imagers'.format(well_number)
        new_slide.shapes.title.text = title

        return new_slide
    
    def add_cocktail_slide(self, well, cocktail):
        new_slide = self.add_new_slide(5)
        title = 'Well {} Cocktail: {}'.format(well, cocktail.number)
        new_slide.shapes.title.text = title

    def add_table_to_slide(self, slide, data, left, top):
        rows, cols = len(data), max([len(r) for r in data])
        shapes = slide.shapes
        
        width = (self.slide_width - (self.__bumper * 2))
        height = self.__slide_height - 2
        table = shapes.add_table(rows, cols, Inches(left), Inches(top), 
                                 Inches(width), Inches(height))

        for k in range(cols):
            table.columns[k].width = (self.slide_size - (self.__bumper * 2)) / cols
            # set column width
        for i in range(rows):
            for j in range(cols):
                table.cell(i, j).text = data[i][j]
        return slide

    def add_multi_image_slide(self, slide, images, labeler):
        top = 3
        img_size = (self.__slide_width - (self.__bumper * 2)) / len(images)
        if img_size >= 0.4 * self.__slide_height: img_size = 0.4 * self.__slide_height

        left = ((self.__slide_width - (img_size * len(images))) / 2) - 0.2

        for image in images:
            self.add_image_to_slide(
                image, slide, left, top, img_size
            )
            label_text = labeler(image)
            self.add_text_to_slide(
                slide, label_text, left, top + (img_size * 1.5), img_size, 1.5, 
                rotation=90)
            left += img_size
        return slide
    
    def add_single_image_slide(self, image, title, metadata=None, img_scaler=0.65):
        new_slide = self.add_new_slide(5)
        new_slide.shapes.title.text = title
        img_size = self.__slide_height * img_scaler
        self.add_image_to_slide(
            image, new_slide, self.__bumper, 2, img_size)

        if metadata:
            metadata_offset = ((self.__bumper + img_size) - self.__slide_width) - self.__bumper
            metadata_left = img_size + (self.__bumper * 2)
            metadata_width = self.__slide_width - metadata_left - self.__bumper
            metadata_height = self.__slide_height - 2 - self.__bumper
            self.add_text_to_slide(
                new_slide, metadata, metadata_left, 2, metadata_width,
                metadata_height)
        return new_slide
        
    
    def add_text_to_slide(self, slide, text, left, top, width, height,
                          rotation=0, font_size=14):
        text_box = slide.shapes.add_textbox(
            Inches(left), Inches(top), Inches(width), Inches(height))
        text_box.rotation = rotation
        tf = text_box.text_frame
        tf.word_wrap = True
        p = tf.add_paragraph()
        p.text = text
        p.font.size = Pt(font_size)

        return text_box
    
    def add_image_to_slide(self, image, slide, left, top, height):
        # if the image path does not exist then will have to encode
        # is somehow or think about how that will work
        if os.path.isfile(image.path):
            img_path = image.path
        else:
            temp_path = str(TEMP_DIR.joinpath(str(hash(image.path))))
            with open(temp_path, 'wb') as tmp:
                tmp.write(base64.decodebytes(image.bites))
                self.__temp_images.append(temp_path)
            img_path = temp_path
        
        return slide.shapes.add_picture(img_path, Inches(left), Inches(top), 
                                        height=Inches(height))


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
        datetime_formats = ['%m/%d/%Y', '%m/%d/%y',
                            '%m-%d-%Y', '%m-%d-%y', '%Y-%m-%d %H:%M:%S']
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
                    new_menu = Menu(path, s, e, row['Screen Type'])
                    self.menus[path] = new_menu
                    # add new menu to menus dict path to csv file is the menu
                    # key

    def get_menu_by_date(self, date, type_='s'):
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

    def get_menus_by_type(self, type_='s'):
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

    def get_menu_by_basename(self, basename):
        for menu_key in self.menus:  # self.menus is dictionary
            if os.path.basename(menu_key) == basename:
                return self.menus[menu_key]


class CocktailMenuReader():
    '''CocktailMenuReader instances should be used to read a csv file containing
    a collection of cocktail screens. The csv file should contain cocktail
    related formulations and assign each cocktail to a specific well in the
    screening plate. CocktailMenuReader is essentially a wrapper around 
    the `csv.DictReader` class. However it returns a Cocktail instance 
    instead of returning a dictionary via when it's __iter__ method is called.

    .. highlight:: python
    .. code-block:: python

        cocktail_menu = 'path/to/my/csv'
        my_reader = CocktailMenuReader(cocktail_menu)
        csv_cocktails = my_reader.read_menu_file()
        # csv_cocktails now holds list of Cocktail objects read from
        # cocktail_menu

    :param menu_file: Path to cocktail menu file to read. Should be csv
                        formated
    :type menu_file: str or Path 
    :param delim: Seperator for menu_file; really should not need to 
                    be changed, defaults to ','
    :type delim: str, optional
    '''

    cocktail_map = {  # map Cocktail attributes to index in menu rows
        0: 'well_assignment',
        1: 'number',
        8: 'pH',
        2: 'commercial_code'
    }
    formula_pos = 4  # each reagent could have a formula but only ever
    # one is included per cocktail entry
    # all other indicies are reagent names and concentrations

    def __init__(self, menu_file_path, delim=','):
        self.menu_file_path = menu_file_path
        self.delim = delim
        self.__row_counter = 0

    @classmethod
    def set_cocktail_map(cls, map):
        '''Classmethod to edit the cocktail_map. The cocktail map describes
        where Cocktail level information is stored in a given cocktail menu
        file row. It is a dictionary that maps specific indices in a row to
        the Cocktail attribute to set the value of the key index to.

        The default cocktail_map dictionary is below.

        >>> cocktail_map = {
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
        cls.cocktail_map = map

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

    def read_menu_file(self):
        '''Read the contents of cocktail menu csv file. The menu file path
        is read from the `menu_file_path` attribute. The first **two** lines
        of all the cocktail menu files included in Polo are header lines and
        so the reader will skip the first two lines before actually reading
        in any data. Each row is converted to a `Cocktail` object and then
        added to a dictionary based on the cocktail's well assignment.

        :return: Dictionary of Cocktail instances. Key value is the Cocktail's
                 well assignment in the screening plate (base 1).
        :rtype: dict
        '''
        cocktail_menu = {}
        with open(self.menu_file_path, 'r') as menu_file:
            reader = csv.reader(menu_file)
            next(reader)
            next(reader)  # skip first two rows
            for row in reader:
                d = {self.cocktail_map[index]: row[index]
                     for index in self.cocktail_map}
                new_cocktail = Cocktail(**d)
                new_cocktail.reagents = []
                # BUG: when new cocktail is intialized it contains the reagents
                # of all previously initialized cocktails. For now setting
                # new_cocktail.reagents to a new empty list fixes the
                # problem but does not address the source
                reagent_positions = [i for i in range(
                    len(row)) if i not in self.cocktail_map and i != self.formula_pos]
                for i in range(0, len(reagent_positions), 2):
                    chem_add, con = (row[reagent_positions[i]],
                                     row[reagent_positions[i+1]])
                    if chem_add:
                        con = SignedValue.make_from_string(con)
                        new_cocktail.add_reagent(
                            Reagent(
                                chemical_additive=chem_add,
                                concentration=con
                            )
                        )
                cocktail_menu[new_cocktail.well_assignment] = new_cocktail
        return cocktail_menu


class RunLinker():

    def __init__(self, loaded_runs):
        self.loaded_runs = loaded_runs
    
    def the_big_link(self):
        self.link_runs_by_date()
        self.link_runs_by_spectrum()

    def link_runs_by_date(self):
        for run in self.loaded_runs:
            if hasattr(run, 'link_to_decendent') and isinstance(run.date, datetime):
                continue
            else:
                return False
        runs = [r for r in sorted(
            self.loaded_runs, key=lambda r: r.date) if r.image_spectrum == IMAGE_SPECS[0]]
        # only visible runs liked by date
        if runs and len(runs) > 1:  # if length is only one will be linked to self
            for i in range(0, len(runs)-1):
                runs[i].link_to_decendent(runs[i+1])
        return runs

    def link_runs_by_spectrum(self):
        # for now this links all runs of the sample to the alt spectrums when
        for run in self.loaded_runs:
            if hasattr(run, 'link_to_alt_spectrum'):
                continue
            else:
                return False
        visible, other = [], []
        for run in self.loaded_runs:
            if run.image_spectrum == IMAGE_SPECS[0]:  # visible images only
                visible.append(run)
            else:
                other.append(run)
        if other:
            # ISSUE WITH LINKING ALT RUNS HERE
            if len(other) > 1:
                other = sorted(other, key=lambda o: len(str(o.image_spectrum)))
                for i in range(len(other)-1):
                    other[i].link_to_alt_spectrum(other[i+1])
                other[-1].link_to_alt_spectrum(other[0])

            if visible:
                for run in visible:
                    run.link_to_alt_spectrum(other[0])  # link to first run of alts

            # setting up the linked list structure
            # all alt spectrum (non visible) runs get linked together in a
            # circular linked list. Visible runs then point at the one
            # alt spectrum run. When a run is loaded in if it is in the visible
            # spectrum the visible run is temprorarly inserted into the alt
            # spec linked list and reconnected. If a new visible run is selected
            # the current visible run in the linked list is replaced with the
            # new current run


class XmlReader():

    platedef_key = 'platedef'  # keyword that is always in plate definition
    # xml file names

    def __init__(self, xml_path=None, xml_files=[]):
        '''XmlReader class can be used to read the xml metadata files that are
        included in HWI screening run rar archives. Currently, is primarily ment
        to extract metadata about the plate and the sample in that plate

        :param xml_path: File path to xml file
        :type xml_path: str or Path
        :param xml_files: list of xml file paths, defaults to []
        :type xml_files: list, optional
        '''
        self.xml_path = xml_path
        self.xml_files = xml_files

    @staticmethod
    def get_data_from_xml_element(xml_element):
        return {elem.tag: elem.text for elem in xml_element
                if elem.tag and elem.text}

    def read_plate_data_xml(self, xml_path=None):
        if not xml_path:
            xml_path = self.xml_file
        xml_path = str(xml_path)
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            d = XmlReader.get_data_from_xml_element(root[0])
            d.update(
                XmlReader.get_data_from_xml_element(root[1])
            )
            return d

        except (FileNotFoundError, IsADirectoryError, PermissionError) as e:
            return e

    def discover_xml_files(self, parent_dir):
        parent_dir = Path(str(parent_dir))
        try:
            file_paths = [parent_dir.joinpath(f)
                          for f in os.listdir(str(parent_dir))]
            xmls = [f for f in file_paths if f.suffix.lower() == '.xml']
            return xmls
        except (PermissionError, FileNotFoundError) as e:
            return e

    def find_and_read_plate_data(self, parent_dir):
        xml_files = self.discover_xml_files(parent_dir)
        if isinstance(xml_files, list):
            for xml_file in xml_files:
                if self.platedef_key in str(xml_file):
                    return self.read_plate_data_xml(xml_file)
        else:
            return None


class Menu():  # holds the dictionary of cocktails

    def __init__(self, path, start_date, end_date, type_, cocktails={}):
        '''Creates a Menu instance. Menu objects are used to organize a single
        screening run plate set up. They should contain 1536 unique screening
        conditions; one for each well in the HWI high-throughput plate. HWI
        has altered what cocktails are used in each of the 1536 wells over the
        years and so many versions of cocktail menus have been used. A single
        Menu instance represents one of these versions and accordingly has a
        start and end date to identify when the menu was used. Additionally, 
        HWI offers two types of high throughput screens; membrane or soluble
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
        self.path = path
        self.cocktails = cocktails  # holds all cocktails (items on the menu)

    @property
    def cocktails(self):
        return self.__cocktails

    @cocktails.setter
    def cocktails(self, new_cocktails):
        if new_cocktails:
            self.__cocktails = new_cocktails
        else:
            self.__cocktails = CocktailMenuReader(self.path).read_menu_file()


class BulkImporter():

    def __init__(self, image_dir):
        self.image_dir = image_dir

    # or potentially use a file browser to do this one and put it in a wdiget


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

from polo.crystallography.run import *
