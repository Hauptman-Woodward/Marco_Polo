from polo import COLORS, IMAGE_CLASSIFICATIONS, ALLOWED_IMAGE_COUNTS
from polo.crystallography.run import Run, HWIRun
from polo.utils.math_utils import *
import os
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsColorizeEffect, QGraphicsScene
from PyQt5.QtGui import QBrush, QColor, QIcon, QPixmap, QColor, QBitmap, QPainter
from polo.ui.widgets.slideshow_viewer import PhotoViewer
from polo.ui.designer.UI_slideshow_inspector import Ui_slideshowInspector
import copy
from polo import ICON_DICT


class slideshowInspector(QtWidgets.QWidget):
    def __init__(self, parent, run=None):
        super(slideshowInspector, self).__init__(parent)
        self.ui = Ui_slideshowInspector()
        self.ui.setupUi(self)
        self.__run = run

        self.class_buttons = [self.ui.pushButton, self.ui.pushButton_2,
                              self.ui.pushButton_5, self.ui.pushButton_3]
        self.class_checkboxs = [self.ui.checkBox, self.ui.checkBox_2,
                                self.ui.checkBox_3, self.ui.checkBox_4]

        self.ui.spinBox.valueChanged.connect(
           self.show_image_from_well_number
        )
        self.set_classification_button_labels()
        self.set_image_class_checkbox_labels()

        self.class_buttons[0].clicked.connect(
            lambda: self.classify_image(self.class_buttons[0].text())
        )
        self.class_buttons[1].clicked.connect(
            lambda: self.classify_image(self.class_buttons[1].text())
        )
        self.class_buttons[2].clicked.connect(
            lambda: self.classify_image(self.class_buttons[2].text())
        )
        self.class_buttons[3].clicked.connect(
            lambda: self.classify_image(self.class_buttons[3].text())
        )

        self.ui.pushButton_6.clicked.connect(
            lambda: self.navigate_carousel(next_image=True))
        self.ui.pushButton_4.clicked.connect(
            lambda: self.navigate_carousel(prev_image=True))
        self.ui.pushButton_11.clicked.connect(self.submit_filters)

        self.ui.pushButton_10.clicked.connect(
            lambda: self.set_alt_image(next_date=True))
        self.ui.pushButton_9.clicked.connect(
            lambda: self.set_alt_image(prev_date=True)
        )
        self.ui.pushButton_12.clicked.connect(
            lambda: self.set_alt_image(alt_spec=True)
        )


    def set_classification_button_labels(self):
        '''
        To be called in init function. Sets the classification button labels
        to those set in the IMAGE CLASSIFICATION constant.
        '''
        for each_butt, img_class in zip(self.class_buttons,
                                        IMAGE_CLASSIFICATIONS):
            each_butt.setText(img_class)

    def set_image_class_checkbox_labels(self):
        '''
        To be called in the init method. Sets image filtering checkbox labels
        to those found in the image classifications constant.
        '''
        for each_checkbox, im_cls in zip(self.class_checkboxs, IMAGE_CLASSIFICATIONS):
            each_checkbox.setText(im_cls)

    @property
    def run(self):
        return self.__run

    @run.setter
    def run(self, new_run):
        '''
        Setter method for __run attribute. Sets __run to `new run` and sets
        up for displaying the first image.
        '''
        self.__run = new_run
        self.ui.slideshowViewer.run = new_run
        self.display_current_image()
        self.set_time_resolved_functions()
        self.set_alt_spectrum_buttons()

    @property
    def selected_classifications(self):
        '''
        Returns image classification keywords for any image classification
        checkboxes that are checked. Used for filtering images down. If no
        image classifications are selected assume user wants images of all
        classifications and return the IMAGE_CLASSIFICATIONS constant
        '''
        selected_classes = []
        for each_checkbox in self.class_checkboxs:
            if each_checkbox.isChecked():
                selected_classes.append(each_checkbox.text())
        if not selected_classes:  # no classes selected
            selected_classes = IMAGE_CLASSIFICATIONS  # add all
        return selected_classes

    @property
    def human(self):
        '''Human image classifier boolean'''
        return self.ui.checkBox_5.isChecked()

    @property
    def marco(self):
        '''Marco image classifier boolean'''
        return self.ui.checkBox_6.isChecked()
    
    @property
    def current_image(self):
        '''Current Image object being displayed in the slideshowViewer widget'''
        return self.ui.slideshowViewer.current_image
    
    def show_image_from_well_number(self, well_number):
        self.ui.slideshowViewer.set_current_image_by_well_number(well_number)
        self.display_current_image()


    def classify_image(self, classification):
        '''
        Calls the `classify_current_image` method of the slideshowViewer
        widget and increments the carousel to the next image and displays it.
        '''
        self.ui.slideshowViewer.classify_current_image(classification)
        self.navigate_carousel(next_image=True)

    def navigate_carousel(self, next_image=False, prev_image=False):
        '''
        Method for moving between images in the current slideshow. Calls
        `carousel_controls` method of slideshowViewer widget passing
        boolean arguements as flags then displays the image.
        '''
        self.ui.slideshowViewer.carousel_controls(next_image, prev_image)
        self.display_current_image()

    def display_current_image(self):
        '''
        Displays the current image as determined by the current_image
        attribute of the slideshowViewer widget and populates any widgets
        that display current image metadata.
        '''
        self.ui.slideshowViewer.display_current_image()
        self.ui.textBrowser_2.setText(
            self.ui.slideshowViewer.get_cur_img_meta_str())
        self.ui.textBrowser.setText(
            self.ui.slideshowViewer.get_cur_img_cocktail_str()
        )
        self.set_image_name()

    def submit_filters(self):
        '''
        Passes the current user selected image filters to the slideshowViewer
        so the current slideshow contents can be adjusted to reflect the
        new filters. Displays the current image after filtering.
        '''
        self.ui.slideshowViewer.update_slides_from_filters(
            self.selected_classifications, self.human, self.marco
        )
        self.display_current_image()

    def set_alt_image(self, next_date=False, prev_date=False, alt_spec=False):
        '''
        Used boolean flags to provide alt image behavior by passing flags
        to `set_alt_image` of slideshowViewer widget. Then displays the
        current image.
        '''
        self.ui.slideshowViewer.set_alt_image(next_date, prev_date,
                                              alt_spec)
        self.display_current_image()
    
    def set_image_name(self):
        '''
        Sets the label_2 to the current image name.
        '''
        ci = self.current_image
        if ci:
            self.ui.label_2.setText(os.path.basename(str(ci.path)))
    
    def set_time_resolved_functions(self):
        '''
        Turns on / off time resolved functions depending if the __run
        attribute has been linked to another run in time.
        ''' 
        if self.__run and (self.__run.previous_run or self.__run.next_run):
            self.ui.pushButton_9.setEnabled(True)
            self.ui.pushButton_10.setEnabled(True)
        else:
            self.ui.pushButton_9.setEnabled(False)
            self.ui.pushButton_10.setEnabled(False)
    
    def set_alt_spectrum_buttons(self):
        '''
        Turns on / off alt spec functions depending on if the __run
        attribute has been linked to another spectrum.
        '''
        if self.__run and self.__run.alt_spectrum:
            self.ui.pushButton_12.setEnabled(True)
        else:
            self.ui.pushButton_12.setEnabled(False)
