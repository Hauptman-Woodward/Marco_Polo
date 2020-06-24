from polo.utils.ftp_utils import list_dir, logon
from polo.designer.UI_image_pop_dialog import Ui_Dialog
from polo import make_default_logger, IMAGE_CLASSIFICATIONS
import os

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QBrush, QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QGridLayout
from polo.widgets.slideshow_viewer import PhotoViewer

logger = make_default_logger(__name__)


class ImagePopDialog(QtWidgets.QDialog):
    '''Pop up that displays a selected image in a larger view. Intended
    to be used with the PlateViewer widget when a user selects an
    image from the grid.

    :param image: Image to show
    :type image: Image
    '''

    def __init__(self, image):
        QtWidgets.QDialog.__init__(self)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.image = image
        self.ui.pushButton_2.clicked.connect(
            lambda: self.classify_image(crystals=True))
        self.ui.pushButton_3.clicked.connect(
            lambda: self.classify_image(precipitate=True))
        self.ui.pushButton_5.clicked.connect(
            lambda: self.classify_image(clear=True))
        self.ui.pushButton_4.clicked.connect(
            lambda: self.classify_image(other=True))

        self.set_groupbox_title()
        self.set_cocktail_details()

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

    def show_image(self):
        '''Show the image stored in the `image` attribute
        '''
        if self.image:
            self.ui.photoViewer.set_image(pixmap=self.image.pixmap)

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
