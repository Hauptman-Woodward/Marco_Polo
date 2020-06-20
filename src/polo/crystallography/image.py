import base64
import os

from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QPixmap

from polo import MODEL
from polo.marco.run_marco import classify_image


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
                 favorite=False):

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
        self.favorite = favorite

    def __str__(self):
        image_string = 'Well Num: {}\n'.format(str(self.well_number))
        image_string += 'MARCO Class: {}\nHuman Class: {}\n'.format(
            str(self.machine_class), str(self.human_class))
        image_string += 'Date: {}\n'.format(str(self.date))
        image_string += 'Spectrum: {}'.format(self.spectrum)

        return image_string


    def encode_base64(self):
        '''If the `path` attribute exists and is an image file then encodes
        that file as base64 and returns the encoded image.

        :return: base64 encoded image
        :rtype: str
        '''
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

    def get_pixel_map(self):
        '''Create a pixelmap object from either the base64 encoded version
        of the image or the actual image file if it exists. Base64 takes
        precedence. The pixelmap is what is eventually displayed to the user.

        :return: Pixelmap
        :rtype: QPixmap
        '''
        if self.bites:
            pm = QPixmap()
            pm.loadFromData(base64.b64decode(self.bites))
            return pm
        elif os.path.exists(self.path):
            return QPixmap(self.path)

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

