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
        #self._set_allowed_navigation_functions()
        self.ui.radioButton.toggled.connect(
            self._change_favorite_status
        )
        logger.info('Created {}'.format(self))
        # must set image before any other widget population

    @property
    def image(self):
        '''The :class:`~polo.crystallography.image.Image`
         being displayed.

        :return: The :class:`~polo.crystallography.image.Image` instance to be displayed
        :rtype: Image
        '''
        return self._image

    @image.setter
    def image(self, new_image):
        self._image = new_image
        self.show_image()

    def show(self):
        '''Shows the dialog window.
        '''
        super(ImagePopDialog, self).show()
        self.show_image()

    def _set_groupbox_title(self):
        '''Private method that set the the title of main groupbox to the 
        basename of the :attr:`~polo.crystallography.image.Image.path`
        attribute of the :class:`~polo.crystallography.image.Image` instance
        referenced by the :attr:`~polo.windows.image_pop_dialog.ImagePopDialog.image`
        attribute.
        '''
        if self.image:
            self.ui.groupBox.setTitle(os.path.basename(str(self.image.path)))

    def _set_cocktail_details(self):
        '''Private method that shows the 
        :attr:`~polo.windows.image_pop_dialog.ImagePopDialog.image`
        attribute metadata in the text display widgets.
        '''
        if self.image and self.image.cocktail:
            self.ui.textBrowser.setText(str(self.image.cocktail))
    
    def _change_favorite_status(self):
        '''Private method that updates the favorite status of the current 
        :attr:`~polo.windows.image_pop_dialog.ImagePopDialog.image`
        attribute to the state of the favorite radioButton.
        '''
        if self.image:
            self.image.favorite = self.ui.radioButton.isChecked()

    def _set_image_details(self):
        '''Private method that displays the :class:`~polo.crystallography.image.Image` instance referenced
        by the :attr:`~polo.windows.image_pop_dialog.ImagePopDialog.image` attribute.
        '''
        if self.image:
            self.ui.textBrowser_2.setText(str(self.image))

    def show_image(self):
        '''Show the :class:`~polo.crystallography.image.Image`
        instance referenced by the
        :attr:`~polo.windows.image_pop_dialog.ImagePopDialog.image` attribute.
        '''
        if self.image:
            self.ui.photoViewer.scene.clear()
            if self.image.isNull():
                self.image.setPixmap()
            self.ui.photoViewer.add_pixmap(self.image)
            self.ui.photoViewer.fitInView()
            self._set_groupbox_title()
            self._set_cocktail_details()
            self._set_image_details()
            self._set_allowed_navigation_functions()
    

    def classify_image(self, crystals=False, clear=False,
                       precipitate=False, other=False):
        '''Set the human classification of the 
        :class:`~polo.crystallography.image.Image` instances
        referenced by the :attr:`~polo.windows.image_pop_dialog.ImagePopDialog.image`
        attribute.

        :param crystals: If True, classify the `image` as crystal,
                         default False
        :type crystals: bool, optional
        :param clear: If True, classify the `image` as clear,
                      defaults to False
        :type clear: bool, optional
        :param precipitate: If True, classify the `image` as precipitate, 
                            defaults to False
        :type precipitate: bool, optional
        :param other: If True, classify as the `image` as other,
                      defaults to False
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

        :param next_date: If True, set
                          :attr:`~polo.windows.image_pop_dialog.ImagePopDialog.image` 
                          attribute to next the available imaging date, defaults to False
        :type next_date: bool, optional
        :param prev_date: If True, set 
                          :attr:`~polo.windows.image_pop_dialog.ImagePopDialog.image`
                          attribute to previous 
                          imaging date, defaults to False
        :type prev_date: bool, optional
        :param alt: If True, set 
                    :attr:`~polo.windows.image_pop_dialog.ImagePopDialog.image`
                    attribute to an alt spectrum
                    image, defaults to False
        :type alt: bool, optional
        '''
        if next_date and self.image.next_image:
            self.image = self.image.next_image
        elif prev_date and self.image.previous_image:
            self.image = self.image.previous_image
        elif alt and self.image.alt_image:
            self.image = self.image.alt_image

    def _set_allowed_navigation_functions(self):
        '''Private method to enable or disable navigation by date or spectrum buttons
        based on the content of the current image. 
        Tests the :class:`~polo.crystallography.image.Image` instance
        referenced by the :attr:`~polo.windows.image_pop_dialog.ImagePopDialog.image`
        attribute to determine if it is linked to
        a future date, previous date or alt spectrum image through it's
        :attr:`~polo.crystallography.image.Image.next_image`
        , :attr:`~polo.crystallography.image.Image.next_image.previous_image 
        and :attr:`~polo.crystallography.image.Image.next_image.alt_image attributes
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
