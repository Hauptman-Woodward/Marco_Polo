import base64
import os
import time
from pathlib import Path
from datetime import datetime

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QGraphicsColorizeEffect, QGraphicsScene

from polo import (DEFAULT_IMAGE_PATH, IMAGE_CLASSIFICATIONS, MODEL,
                  make_default_logger)
from polo.marco.run_marco import classify_image



class Image(QtGui.QPixmap):

    '''Image objects hold the data relating to one image in a particular
    screening well of a paricular run. Images encode the actual image file as
    a file path to the image if it available on the local machine, as 
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
                 favorite=False, parent=None, **kwargs):

        super(Image, self).__init__(parent)
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

    @staticmethod
    def clean_base64_string(string):
        '''Image instances may contain byte strings that store their actual
        crystallization image encoded as base64. Previously, these byte strings
        were written directly into the json file as strings causing the b'
        byte string identifier to be written along with the actual base64 data.
        This method removes those artifacts if they are present and returns a
        clean byte string with only the actual base64 data.

        :param string: a string to interrogate for base64 compliance
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
                return bytes(string, 'utf-8')

    @classmethod
    def to_graphics_scene(cls, image):
        '''Convert an Image object to a `QGraphicsScene` with
        the Image added as a pixmap to the `QGraphicsScene`.

        :param image: Image instance
        :type image: Image
        :return: QGraphicsScene
        :rtype: QGraphicsScene
        '''
        scene = QtWidgets.QGraphicsScene()
        if image.isNull():
            image.setPixmap()
        scene.addPixmap(image)
        return scene

    @classmethod
    def no_image(cls):
        '''Return an Image instance with the default image data.
        Used to fill in for missing data and when filters cannot
        find any matching results.

        :return: Default image
        :rtype: Image
        '''
        # return default no images found image instance
        return cls(path=DEFAULT_IMAGE_PATH)

    @property
    def date(self):
        '''Retrun the date associated with this image. Presumably should be
        the date the image was taken.

        :return: datetime object representation of the image's imageing date
        :rtype: datetime
        '''
        return self._date

    @date.setter
    def date(self, date):
        if isinstance(date, str):
            d = BarTender.datetime_converter(date)
            self._date = d
        else:
            self._date = date

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, new_path):
        if new_path:
            if isinstance(new_path, Path):
                self._path = str(new_path)
            self._path = new_path
        else:
            self._path = None

    @property
    def bites(self):
        return self._bites

    @bites.setter
    def bites(self, new_bites):
        if isinstance(new_bites, bytes):
            self._bites = new_bites
        elif isinstance(new_bites, str):
            self._bites = Image.clean_base64_string(new_bites)
        else:
            self._bites = None

    @property
    def marco_class(self):
        '''Return the `__marco_class` hidden attribute.

        :return: Current MARCO classification of this image
        :rtype: str
        '''
        return self._marco_class

    @marco_class.setter
    def marco_class(self, new_class):
        '''Setter method for `_marco_class` attribute. If this image has alt images
        linked to it and has its `spectrum` attribute set as 'Visible' linked alt images
        will share this image's marco classification. This is because the MARCO
        model has only been trained on visible light images and therefore is
        not cabable of reliably classifying images taken in differenet spectrums.
        Since linked alt images should in theory be images of the exact same
        well in the exact same plate the visible spectrum image can share
        its MARCO classification with it's linked alt images.

        :param new_class: New MARCO classification for the image
        :type new_class: str
        '''
        if new_class in IMAGE_CLASSIFICATIONS:
            self._marco_class = new_class
            if hasattr(self, 'alt_image') and self.alt_image and self.spectrum == 'Visible':
                # alt images inherit their linked classifications
                alt_image = self.alt_image
                while alt_image.path and alt_image.path != self.path:
                    alt_image.__marco_class = new_class
                    alt_image = alt_image.alt_image
        else:
            self._marco_class = None

    @property
    def human_class(self):
        '''Return the `_human_class` hidden attribute

        :return: Current human classification of this image
        :rtype: str
        '''
        return self._human_class

    @human_class.setter
    def human_class(self, new_class):
        if new_class in IMAGE_CLASSIFICATIONS:
            self._human_class = new_class
        else:
            self._human_class = None
    
    @property
    def formated_date(self):
        '''Get the image's `data` attribute formated in the
        month/date/year format. If image has no `date` returns
        an empty string.

        :return: Date
        :rtype: str
        '''
        if isinstance(self.date, datetime):
            return datetime.strftime(self.date, '%m/%d/%Y')
        else:
            return ''


    def setPixmap(self, scaling=None):
        '''Loads the images pixmap into memory which then allows for displaying
        the image to the user. Images that are displayed before loading
        will not appear. It is recommended to only load the image pixmap when
        the image actually needs to be shown to the user as it is expensive
        to hold in memory.

        :param scaling: Scaler for the pixmap; between 0 and 1, defaults to None
        :type scaling: float, optional
        '''
        if os.path.exists(self.path):
            self.load(self.path)
        elif isinstance(self.bites, bytes):
            self.loadFromData(base64.b64decode(self.bites))
        if isinstance(scaling, float):
            self.scaled(self.width*scaling, self.height *
                        scaling, Qt.KeepAspectRatio)

    def delete_pixmap_data(self):
        '''Replaces the Image's pixmap data with a null pixmap which
        effectively deletes the existing pixmap data. Used to free up
        memory after a pixmap is no longer needed.
        '''
        self.swap(QPixmap())  # swap with null pixel map

    def delete_all_pixmap_data(self):
        '''Deletes the pixmap data for the Image object this function is
        called on and for any other images that this image is linked to. This
        includes images stored in the `alt_image`, `next_image` and `previous_image`
        attributes.
        '''
        for i in self.get_linked_images_by_date():
            i.delete_pixmap_data()
        for i in self.get_linked_images_by_spectrum():
            i.delete_pixmap_data()

    def height(self):
        '''Get the height of the image's pixmap. The pixmap must be set
        for this function to return an actual size.

        :return: Height of the image's pixmap
        :rtype: int
        '''
        return self.size().height()

    def width(self):
        '''Get the height of the image's pixmap. The pixmap must be set
        for this function to return an actual size.

        :return: Width of the image's pixmap
        :rtype: int
        '''
        return self.size().width()

    def __str__(self):
        image_string = 'Well Num: {}\n'.format(str(self.well_number))
        image_string += 'MARCO Class: {}\nHuman Class: {}\n'.format(
            str(self.machine_class), str(self.human_class))
        if self.machine_class and self.prediction_dict and self.machine_class in self.prediction_dict:
            image_string += 'MARCO Confidence: {} %\n'.format(
                round(float(self.prediction_dict[self.machine_class]) * 100, 1)
            )
        image_string += 'Date: {}\n'.format(self.formated_date)
        image_string += 'Spectrum: {}'.format(self.spectrum)

        return image_string

    def encode_base64(self):
        if not self.bites and os.path.exists(self.path):
            with open(self.path, 'rb') as image_file:
                self.bites = base64.b64encode(image_file.read())

    def encode_bytes(self):
        '''If the `path` attribute exists and is an image file then encodes
        that file as a base64 string and returns the encoded image data.

        :return: base64 encoded image
        :rtype: str
        '''
        if self.bites:
            return self.bites
        elif os.path.exists(self.path):
            with open(self.path, 'rb') as image:
                return base64.b64encode(image.read())

    def get_tool_tip(self):
        '''Create a string to use as the tooltip for this image.

        :return: Tooltip string
        :rtype: str
        '''
        if self.cocktail:
            cocktail = self.cocktail.number
        else:
            cocktail = None
        return 'Well: {}\nCocktail: {}\nDate: {} \nMARCO Class: {}\nHuman Class: {}'.format(
            str(self.well_number), cocktail, self.formated_date,
            str(self.machine_class), str(self.human_class)
        )

    def get_linked_images_by_date(self):
        '''Get all images that are linked to this Image instance by date. 
        Image linking by date is accomplished by creating a bi-directional
        linked list between Image instances, where each Image acts as a node
        and the `next_image` and `previous_images` act as the forwards and
        backwards pointers respectively.

        :return: All Images connected to this Image by date
        :rtype: list
        '''
        linked_images = [self]
        if self.next_image:
            start_image = self.next_image
            while isinstance(start_image, Image) and start_image.path != self.path:
                linked_images.append(start_image)
                start_image = start_image.next_image
        if self.previous_image:
            start_image = self.previous_image
            while isinstance(start_image, Image) and self.previous_image.path != self.path:
                linked_images.append(start_image)
                start_image = start_image.previous_image
        return sorted(linked_images, key=lambda i: i.date)

    def get_linked_images_by_spectrum(self):
        '''Get all images that are linked to this Image instance by
        spectrum. Linking images by spectrum is accomplished by
        creating a mono-directional circular linked list where
        Image instances serve as nodes and their `alt_image` attribute
        acts as the pointer to the next node.

        :return: List of all Images linked to this Image by spectrum
        :rtype: list
        '''
        linked_images, paths = [self], set([])
        if self.alt_image:
            start_image = self.alt_image
            while (isinstance(start_image, Image)
                   and start_image.path != self.path
                   and start_image.path not in paths):
                linked_images.append(start_image)
                paths.add(start_image.path)
                start_image = start_image.alt_image

            return sorted(linked_images, key=lambda i: len(i.spectrum))
        else:
            return linked_images

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

    def standard_filter(self, image_types, human, marco, favorite):
        '''Method that determines if this image should be included in a set
        of filtered images based on given image types and a classifier: human,
        marco or both. Returns True if the Image meets the filtering requirements
        specified by the method's arguments, otherwise returns False.

        :param image_types: Collection of image classifications. The Image's
                            classification must in included in this collection 
                            for the method to return True.
        :type image_types: list or set
        :param human: If True, use the Image's human classification as the
                      overall image classification.
        :type human: bool
        :param marco: If True, use the Image's MARCO classification as the
                      overall image classification.
        :type marco: bool
        :return: True if the Image meets the filter requirements, False otherwise 
        :rtype: bool
        '''
        if favorite == self.favorite:
            if image_types:  # have specificed some image types
                if self.human_class and human and self.human_class in image_types:
                    return True
                elif self.machine_class and marco and self.machine_class in image_types:
                    return True
                else:
                    return False
            else:
                if human or marco:  # set at least one classifier filter
                    if (human and self.human_class) or (marco and self.machine_class):
                        return True
                    else:
                        return False
                else:
                    return True  # set no filters so return True
        else:
            return False

from polo.utils.io_utils import BarTender