import base64
import os

from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QPixmap

from polo import MODEL
from polo.marco.run_marco import classify_image


class Image():

    DEFAULT_IMAGE = ''  # TODO Add default image

    def __init__(self, path=None, bites=None, well_number=None, human_class=None,
                 machine_class=None, prediction_dict=None,
                 plate_id=None, date=None, cocktail=None, spectrum=None,
                 previous_image=None, next_image=None, alt_image=None):

        self.path = str(path)
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
        self.bites = bites

    def __str__(self):
        image_string = 'Well Num: {}\n'.format(str(self.well_number))
        image_string += 'MARCO Class: {}\nHuman Class: {}\n'.format(str(self.machine_class),
                                                                        str(self.human_class))
        image_string += 'Date: {}\n'.format(str(self.date))
        image_string += 'Spectrum: {}'.format(self.spectrum)

        return image_string


    def encode_base64(self):
        if os.path.exists(self.path):
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
        return 'Well: {}\nCocktail: {}\nMARCO Class: {}\nHuman Class: {}'.format(
            str(self.well_number), 'pass', str(self.machine_class), str(self.human_class)
        )


    def __iter__(self):
        attribs = [self.path, self.human_class, self.machine_class,
                   self.well_number, self.plate_id, self.date]
        for item in attribs:
            yield item

    def get_pixel_map(self):
        if self.bites:
            pm = QPixmap()
            pm.loadFromData(base64.b64decode(self.bites))
            return pm
        elif os.path.exists(self.path):
            return QPixmap(self.path)

        # if path does exist and there is no base64 encoding then
        # there is goin to be an issue

    def classify_image(self):
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

    def get_cocktail_number(self):
        '''
        Returns the numerical cocktail number as an integer. If it does not
        exist returns 0.
        '''
        if self.cocktail:
            return int(self.cocktail.number.split('_C')[-1].lstrip('0'))
        else:
            return 0
