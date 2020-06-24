import base64
import os

from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QPixmap

from polo import MODEL, IMAGE_CLASSIFICATIONS, make_default_logger
from polo.marco.run_marco import classify_image
from pathlib import Path
import time

class Image():

    '''Image objects hold the data relating to one image of a particular
    screening well in a larger run. Images encode the actual image file as
    a file path to the image if it is on the machine Polo is being run from,
    as a base64 encoded image or both.

    :param path: Path to the actual image file, defaults to None
    :type path: str or Path, optional
    :param bites: Image encoded as base64, defaults to None
    :type bites: str or bytes, optional
    :param well_number: Well number of the image, defaults to None
    :type well_number: int, optional
    :param human_class: Human classification of this image, defaults to None
    :type human_class: str, optional
    :param machine_class: MARCO classification of this image, defaults to None
    :type machine_class: str, optional
    :param prediction_dict: Dictionary containing MARCO model confidence for
                            all image classifications, defaults to None
    :type prediction_dict: dict, optional
    :param plate_id: HWI given unique ID for plate this image belongs to
                     , defaults to None
    :type plate_id: str, optional
    :param date: Date this image was taken on, defaults to None
    :type date: Datetime, optional
    :param cocktail: Cocktail assigned to the well this image is of, defaults to None
    :type cocktail: Cocktail, optional
    :param spectrum: Keyword describing the imaging tech used to take the image
                    , defaults to None
    :type spectrum: str, optional
    :param previous_image: Image of the same well and sample but taken on a previous date
                            , defaults to None
    :type previous_image: Image, optional
    :param next_image: Image of the same well and sample but taken on a future 
                        date, defaults to None
    :type next_image: Image, optional
    :param alt_image: Image of the same well and sample but taken with a 
                      different imaging tech, defaults to None
    :type alt_image: Image, optional
    '''

    def __init__(self, path=None, bites=None, well_number=None, human_class=None,
                 machine_class=None, prediction_dict=None,
                 plate_id=None, date=None, cocktail=None, spectrum=None,
                 previous_image=None, next_image=None, alt_image=None, 
                 favorite=False, **kwargs):

        self.path = str(path)
        self.bites = bites
        self.human_class = human_class
        self.machine_class = machine_class
        self.well_number = well_number
        self.prediction_dict = prediction_dict
        self.plate_id = plate_id
        self.date = date
        self.cocktail = cocktail
        self.spectrum = spectrum
        self.previous_image = previous_image
        self.next_image = next_image
        self.alt_image = alt_image
        self.favorite = favorite
        self.__pixmap = None
    
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
            if isinstance(string, bytes): string = str(string, 'utf-8')
            if string[0] == 'b':  # bytes string written directly to string
                string = string[1:]
            if string[-1] == "'":
                string = string[:-1]
            if string:
                return bytes(string, 'utf-8')

    def __str__(self):
        image_string = 'Well Num: {}\n'.format(str(self.well_number))
        image_string += 'MARCO Class: {}\nHuman Class: {}\n'.format(
            str(self.machine_class), str(self.human_class))
        image_string += 'Date: {}\n'.format(str(self.date))
        image_string += 'Spectrum: {}'.format(self.spectrum)

        return image_string

    @property
    def pixmap(self):
        if self.__pixmap:
            return self.__pixmap
        else:
            self.__pixmap = self.make_pixmap()
            return self.__pixmap
    
    # @pixmap.setter
    # def pixmap(self, new_map):
    #     if new_map

    def encode_base64(self):
        if not self.bites and os.path.exists(self.path):
            with open(self.path, 'rb') as image_file:
                self.bites = base64.b64encode(image_file.read())
    
    def make_pixmap(self):
        pm = QPixmap()
        if os.path.exists(self.path):
            pm.load(self.path)
        elif isinstance(self.bites, bytes):
            pm.loadFromData(base64.b64decode(self.bites))
        return pm
    
    # @pixmap.setter
    # def pixmap(self, new_data):
    #     if os.path.exists(self.path):
    #         self.__pixmap = QPixmap(new_data)
    #     elif isinstance(new_data, bytes):
    #         pm = QPixmap()
    #         pm.loadFromData(new_data)
    #         pm.loadFromData(base64.b64decode(new_data))
    #         self.__pixmap = pm
    #     else:
    #         self.__pixmap = None
    
    @property
    def path(self):
        return self.__path
    
    @path.setter
    def path(self, new_path):
        if new_path:
            if isinstance(new_path, Path):
                self.__path = str(new_path)
            self.__path = new_path
        else:
            self.__path = None
    
    @property
    def bites(self):
        return self.__bites
    
    @bites.setter
    def bites(self, new_bites):
        if isinstance(new_bites, bytes):
            self.__bites = new_bites
        elif isinstance(new_bites, str):
            self.__bites = Image.clean_base64_string(new_bites)
        else:
            self.__bites = None

    @property
    def marco_class(self):
        '''Return the `__marco_class` hidden attribute.

        :return: Current MARCO classification of this image
        :rtype: str
        '''
        return self.__marco_class
    
    @marco_class.setter
    def marco_class(self, new_class):
        '''Setter method for `__marco_class`. If this image has alt images
        linked to it and has its `spectrum` set as 'Visible' linked alt images
        will share this image's marco classification. This is because MARCO
        model has only been trained on visible light images so should not be
        used to classify images taken with alternative photographic technologies.
        Since linked alt images should in theory be images of the exact same
        well in the exact same plate the visible spectrum image can share
        its MARCO classification with it's linked alt images.

        :param new_class: New MARCO classification for the image
        :type new_class: str
        '''
        if new_class in IMAGE_CLASSIFICATIONS:
            self.__marco_class = new_class
            if hasattr(self, 'alt_image') and self.alt_image and self.spectrum == 'Visible':
                # alt images inherit their linked classifications
                alt_image = self.alt_image
                while alt_image.path and alt_image.path != self.path:
                    alt_image.__marco_class = new_class
                    alt_image = alt_image.alt_image       
        else:
            self.__marco_class = None
    
    @property
    def human_class(self):
        '''Return the `__human_class` hidden attribute

        :return: Current human classification of this image
        :rtype: str
        '''
        return self.__human_class
    
    @human_class.setter
    def human_class(self, new_class):
        '''Change the human classification of this image and any alternative
        spectrum images it is linked to. The motivation for sharing human
        classifications between spectrums is that in theory linked spectrums
        are images of the exact same well just using a different photographic
        technology. Therefore the classifications should be consistent across
        the runs.

        :param new_class: New image classification
        :type new_class: str
        '''
        if new_class in IMAGE_CLASSIFICATIONS:
            self.__human_class = new_class
            if hasattr(self, 'alt_image') and self.alt_image:
                # alt images inherit their linked classifications
                alt_image = self.alt_image
                while alt_image.path and alt_image.path != self.path:
                    alt_image.__human_class = new_class
                    # assign directly to hidden attr to avoid creating an
                    # endless recursive call loop
                    alt_image = alt_image.alt_image        
        else:
            self.__human_class = None


    def encode_bytes(self):
        '''If the `path` attribute exists and is an image file then encodes
        that file as base64 and returns the encoded image.

        :return: base64 encoded image
        :rtype: str
        '''
        if self.bites:
            return self.bites
        elif os.path.exists(self.path):
            with open(self.path, 'rb') as image:
                return base64.b64encode(image.read())

    def resize(self, x, y, preserve_aspect=True):
        '''
        Resizes an image given x and y resolution. Copy is true will copy
        the image instead of overwriting it.
        '''
        pixel_map = self.get_pixel_map()
        if preserve_aspect:
            return pixel_map.scaled(x, y, QtCore.Qt.KeepAspectRatio)
    
    def get_tool_tip(self):
        '''Format a string to use as a tooltip for this image instance.

        :return: Tooltip string
        :rtype: str

        # TODO Pick a better way to add cocktail to the tooltip
        '''
        if self.cocktail:
            cocktail = self.cocktail.number
        else:
            cocktail = None
        return 'Well: {}\nCocktail: {}\nMARCO Class: {}\nHuman Class: {}'.format(
            str(self.well_number), cocktail, str(self.machine_class),
            str(self.human_class)
        )


    def __iter__(self):
        attribs = [self.path, self.human_class, self.machine_class,
                   self.well_number, self.plate_id, self.date]
        for item in attribs:
            yield item
    

        # if path does exist and there is no base64 encoding then
        # there is goin to be an issue

    def classify_image(self):
        '''Classify the image using the MARCO CNN model. Sets the 
           `machine class` and `prediction_dict` attributes based on the
           model results.
        '''
        try:
            self.machine_class, self.prediction_dict = classify_image(MODEL,
                                                                      self.path)
        except AttributeError as e:
            return e
        # exception in case there is not image stored for that well. Maybe it
        # got deleted for something
        # at some point probably want an image that is a default image not found
        # and can have a warning pop up if import from HWIrun and there are
        # still null images in run.images

