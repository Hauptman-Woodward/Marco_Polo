from polo.utils.ftp_utils import list_dir, logon
from polo.designer.UI_image_pop_dialog import Ui_Dialog
from polo import make_default_logger, IMAGE_CLASSIFICATIONS
import os

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QBrush, QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QGridLayout
from polo.widgets.slideshow_viewer import PhotoViewer
from polo.crystallography.image import Image

logger = make_default_logger(__name__)


class ImagePopDialog(QtWidgets.QDialog):
    '''Pop up that displays a selected image in a larger view. Intended
    to be used with the `PlateViewer` widget when a user selects an
    image from the grid.

    :param image: Image to show
    :type image: Image
    '''

    def __init__(self, image, parent=None):
        super(ImagePopDialog, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.pushButton_2.clicked.connect(
            lambda: self.classify_image(crystals=True))
        self.ui.pushButton_3.clicked.connect(
            lambda: self.classify_image(precipitate=True))
        self.ui.pushButton_5.clicked.connect(
            lambda: self.classify_image(clear=True))
        self.ui.pushButton_4.clicked.connect(
            lambda: self.classify_image(other=True))
        self.ui.pushButton.clicked.connect(
            lambda: self.show_alt_image(next_date=True))
        self.ui.pushButton_6.clicked.connect(
            lambda: self.show_alt_image(prev_date=True))
        self.ui.pushButton_7.clicked.connect(
            lambda: self.show_alt_image(alt=True))
        self.image = image
        #self.set_allowed_navigation_functions()
        self.ui.radioButton.toggled.connect(
            self.change_favorite_status
        )
        # must set image before any other widget population

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, new_image):
        self._image = new_image
        self.show_image()

    def show(self):
        '''Shows the dialog window
        '''
        super(ImagePopDialog, self).show()
        self.show_image()

    def set_groupbox_title(self):
        '''Set the the title of main groupbox to the image path basename
        '''
        if self.image:
            self.ui.groupBox.setTitle(os.path.basename(str(self.image.path)))

    def set_cocktail_details(self):
        '''Shows image metadata in display widgets
        '''
        if self.image and self.image.cocktail:
            self.ui.textBrowser.setText(str(self.image.cocktail))
    
    def change_favorite_status(self):
        '''Update the favorite status of the current image to the
        state of the favorite radioButton.
        '''
        if self.image:
            self.image.favorite = self.ui.radioButton.isChecked()

    def set_image_details(self):
        '''Displays the current image metadata in a
        testBrowser widget.
        '''
        if self.image:
            self.ui.textBrowser_2.setText(str(self.image))

    def show_image(self):
        '''Show the image stored in the `image` attribute
        '''
        if self.image:
            self.ui.photoViewer.scene.clear()
            if self.image.isNull():
                self.image.setPixmap()
            self.ui.photoViewer.add_pixmap(self.image)
            self.ui.photoViewer.fitInView()
            self.set_groupbox_title()
            self.set_cocktail_details()
            self.set_image_details()
            self.set_allowed_navigation_functions()
    

    def classify_image(self, crystals=False, clear=False,
                       precipitate=False, other=False):
        '''Classify the image in the popout. Sets the human classification.

        :param crystals: Classify as crystals flag, defaults to False
        :type crystals: bool, optional
        :param clear: Classify as clear flag, defaults to False
        :type clear: bool, optional
        :param precipitate: Classify as precipitate flag, defaults to False
        :type precipitate: bool, optional
        :param other: Classify as other flag, defaults to False
        :type other: bool, optional
        '''
        if crystals:
            self.image.human_class = IMAGE_CLASSIFICATIONS[0]
        elif clear:
            self.image.human_class = IMAGE_CLASSIFICATIONS[1]
        elif precipitate:
            self.image.human_class = IMAGE_CLASSIFICATIONS[2]
        elif other:
            self.image.human_class = IMAGE_CLASSIFICATIONS[3]

        self.close()

    def show_alt_image(self, next_date=False, prev_date=False, alt=False):
        '''Show a linked image based on boolean flags. 

        :param next_date: If True, set `image` attribute to next
                          available imaging date, defaults to False
        :type next_date: bool, optional
        :param prev_date: If True, set `image` attribute to previous 
                          imaging date, defaults to False
        :type prev_date: bool, optional
        :param alt: If True, set `image` attribute to alt spectrum
                    image, defaults to False
        :type alt: bool, optional
        '''
        if next_date and self.image.next_image:
            self.image = self.image.next_image
        elif prev_date and self.image.previous_image:
            self.image = self.image.previous_image
        elif alt and self.image.alt_image:
            self.image = self.image.alt_image

    def set_allowed_navigation_functions(self):
        '''Enable or disable navigation by date or spectrum buttons
        based on the content of the current image. Tests the Image
        stored in the `image` attribute to determine if it is linked to
        a future date, previous date or alt spectrum image through it's
        `next_image`, `previous_image` and `alt_image` attributes
        respectively. If an attribute == None, then the button that
        requires that attribute will be disabled.
        '''
        if self.image.next_image:
            self.ui.pushButton.setEnabled(True)
        else:
            self.ui.pushButton.setEnabled(False)
        if self.image.previous_image:
            self.ui.pushButton_6.setEnabled(True)
        else:
            self.ui.pushButton_6.setEnabled(False)
        if self.image.alt_image:
            self.ui.pushButton_7.setEnabled(True)
        else:
            self.ui.pushButton_7.setEnabled(False)
