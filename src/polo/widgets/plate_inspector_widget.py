from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBitmap, QBrush, QColor, QIcon, QPainter, QPixmap
from PyQt5.QtWidgets import QGraphicsColorizeEffect, QGraphicsScene
from PyQt5.QtCore import Qt, pyqtSignal
from polo import (ALLOWED_IMAGE_COUNTS, COLORS, IMAGE_CLASSIFICATIONS)
from polo.crystallography.cocktail import SignedValue
from polo.crystallography.image import Image
from polo.crystallography.run import HWIRun, Run
from polo.designer.UI_plate_inspector_widget import Ui_PlateInspector
from polo.utils.io_utils import write_screen_html
from polo.plots.plots import StaticCanvas
from polo import make_default_logger

logger = make_default_logger(__name__)

class PlateInspectorWidget(QtWidgets.QWidget):

    images_per_page = [16, 64, 96]


    def __init__(self, parent, run=None):
        '''The PlateInspectorWidget is a primary run interface widget and is
        designed to emulate the MarcoScopeJ image viewer with extended
        functionality. It allows users to view their screening images in grids
        of pre-set numbers of images from 24 to an entire 1536 well plate. 

        :param parent: Parent widget
        :type parent: QWidget
        :param run: Run to display, defaults to None
        :type run: Run, optional
        '''
        super(PlateInspectorWidget, self).__init__(parent)
        self.ui = Ui_PlateInspector()
        self.ui.setupUi(self)
        self.run = run
        self.ui.plateViewer.run = self.__run

        self.set_color_comboboxs()
        self.set_color_options()
        self.set_image_count_options()

        self.ui.pushButton_18.clicked.connect(
            lambda: self.show_current_plate(next_view=True)
        )
        self.ui.pushButton_17.clicked.connect(
            lambda: self.show_current_plate(prev_view=True)
        )
        self.image_type_checkboxes = dict(zip(IMAGE_CLASSIFICATIONS,
        [self.ui.checkBox_23, self.ui.checkBox_24, self.ui.checkBox_25,
        self.ui.checkBox_26]))  # define checkboxes that determine image
        # classification filters and zip with the image classifications
        # doesnt matter what is assigned to what as long as order in
        # image classificaions list does not change


        self.ui.pushButton_19.clicked.connect(self.apply_plate_settings)
        self.ui.plateViewer.preserve_aspect = self.ui.checkBox_29.isChecked()
        self.ui.checkBox_29.stateChanged.connect(self.set_aspect_ratio_mode)
        # self.ui.pushButton_24.clicked.connect(self.reset_all)
        self.ui.pushButton_23.clicked.connect(self.show_current_plate)
        self.ui.pushButton_21.clicked.connect(
            lambda: self.show_current_plate(next_date=True))
        self.ui.pushButton_20.clicked.connect(
            lambda: self.show_current_plate(prev_date=True)
        )
        self.ui.pushButton_22.clicked.connect(
            lambda: self.show_current_plate(alt_spec=True)
        )
        self.ui.plateViewer.images_per_page = self.images_per_page[0]

        self.ui.comboBox_7.currentIndexChanged.connect(self.set_images_per_page)

        self.ui.plateViewer.changed_images_per_page_signal.connect(
        self.ui.plateVis.setup_view
        )
        self.ui.plateViewer.changed_page_signal.connect(
            self.ui.plateVis.set_selected_block)


        self.ui.spinBox.setRange(1, 1)
        self.ui.spinBox.valueChanged.connect(self.set_current_page)

        self.set_time_resolved_buttons()
        self.set_alt_spectrum_buttons()

        
    

    def set_images_per_page(self):
        self.ui.plateViewer.images_per_page = self.images_per_page[
                self.ui.comboBox_7.currentIndex()]


    def set_image_count_options(self):
        '''Helper method to be called in `__init__` that sets the options
        for number of images per view.
        '''
        self.ui.comboBox_7.clear()
        self.ui.comboBox_7.addItems([str(i) for i in self.images_per_page])
        self.ui.comboBox_7.setCurrentIndex(0)
        logger.info('Set image count options to {}'.format(self.images_per_page))

    
    def set_aspect_ratio_mode(self):
        '''Sets the `preserve_aspect` attribute based on the status of
        the preserve aspect ratio checkbox available to the user. Preserving
        aspect ratio results in displaying undistorted crystallization images 
        but utilizes available display space less efficiently.
        '''
        self.ui.plateViewer.preserve_aspect = self.ui.checkBox_29.isChecked()

    def set_color_comboboxs(self):
        '''
        Create a dictionary that maps color selector comboboxes to the
        image classification they assign their current color to and label
        each combobox with that classification.
        '''
        self.color_combos = [self.ui.comboBox_3, self.ui.comboBox, self.ui.comboBox_5, self.ui.comboBox_4]
        labels = [self.ui.label_19, self.ui.label_4, self.ui.label_21, self.ui.label_20]
        #self.color_combos_assignments = dict(zip(combos, IMAGE_CLASSIFICATIONS))
        for each_label, each_class in zip(labels, IMAGE_CLASSIFICATIONS):
            each_label.setText(each_class)

    def set_color_options(self):
        '''
        Uses the COLORS constant to set the color options for each 
        colorselector combobox in the image coloring tab.
        '''
        colors, i  = list(COLORS.keys()), 0
        for each_combobox in self.color_combos:
            each_combobox.addItems(colors)
            if colors[i] == 'none':
                i+=1
            each_combobox.setCurrentIndex(i)
            i += 1
    
    @property
    def run(self):
        return self.__run
    
    @run.setter
    def run(self, new_run):
        '''
        Sets run attribute to the given run. Setting the run also sets the
        run for the plateViewer widget and checks if time resolved and
        spectrum navigation should be enabled.
        '''
        if new_run:
            self.__run = new_run
            self.ui.plateViewer.run = new_run
        else:
            self.__run = None
            self.ui.plateViewer.run = None

        self.set_time_resolved_buttons()
        self.set_alt_spectrum_buttons()

    @property
    def selected_classifications(self):
        '''
        Returns a list that includes only image classifications that are
        selected via the image filtering checkboxes. Also see
        `image_type_checkboxes` property.
        '''
        return [k for k in self.image_type_checkboxes if self.image_type_checkboxes[k].isChecked()]
    
    @property
    def human(self):
        '''Status of human image classification checkbox'''
        return self.ui.checkBox_21.isChecked()
    
    @property
    def marco(self):
        '''Status of marco image classification checkbox'''
        return self.ui.checkBox_22.isChecked()
    
    @property
    def favorite(self):
        return self.ui.checkBox_6.isChecked()
    
    @property
    def color_mapping(self):
        '''
        Creates a color mapping dictionary from the current selections of the
        color selector comboboxes. Each image classification maps to a color
        or the string "none" to tell the plateViewer to not color that
        image type.
        '''
        mapping = {}
        for each_combo_box, img_class in zip(self.color_combos,
                                             IMAGE_CLASSIFICATIONS):
            mapping[img_class] = COLORS[each_combo_box.currentText()]
        return mapping
    

    def parse_label_checkboxes(self):
        boxes = [
                 self.ui.checkBox, self.ui.checkBox_2, self.ui.checkBox_3,
                 self.ui.checkBox_4, self.ui.checkBox_5
                ]
        return {b.text(): b.isChecked() for b in boxes}


    def navigate_plateview(self, next_page=False, prev_page=False,
                           alt_image=False, next_date=False, prev_date=False):
        '''
        Helper function that moves the view forward, backward or to an alt
        view using boolean flags. Buttons that actually should preform these
        functions should be connected using a lambda function that passes
        True to whatever functionality is desired from this function.
        '''
        if next_page:
            self.ui.plateViewer.current_page += 1
        elif prev_page:
            self.ui.plateViewer.current_page -= 1
        self.set_plate_label()
        self.ui.plateViewer.tile_graphics_wells()
    
    def reset_all(self):
        '''
        Method to uncheck all user selected settings
        '''
        for widget in self.ui.groupBox_26.children():
            if isinstance(widget, QtWidgets.QCheckBox):
                widget.setChecked(False)
        self.apply_plate_settings()
    

    def set_plate_label(self):
        '''
        Changed the plate label to tell the user what view they are on out
        of total number of views. Number of views is dependent on the number
        of images per view.
        '''
        self.ui.label_18.setText(
            'Page {} of {}'.format(
            self.ui.plateViewer.current_page,
            self.ui.plateViewer.total_pages)
        )
    
    def apply_plate_settings(self):
        '''
        Parses checkboxes in the Plate View tab to determine what behavior
        for the plateViewer widget is requested by the user.
        '''
        if self.__run:
            self.ui.plateViewer.images_per_page = self.images_per_page[
                self.ui.comboBox_7.currentIndex()]
            if self.ui.checkBox_27.isChecked():
                self.apply_image_filters()
            else:
                self.ui.plateViewer.emphasize_all_images()
            if self.ui.checkBox_28.isChecked():
                self.apply_color_mapping()
            else:
                self.ui.plateViewer.decolor_all_images()
    
    def show_current_plate(self, next_view=False, prev_view=False, next_date=False, prev_date=False,
                           alt_spec=False):
        '''Show the images belonging to the current plate view to the user.

        :param next_date: Flag, if True show equivalent images from future 
                          date, defaults to False
        :type next_date: bool, optional
        :param prev_date: Flag, if True shows equivalent images from past
                          date, defaults to False
        :type prev_date: bool, optional
        :param alt_spec: Flag if True shows equivalent images in alternative
                         imaging spectrum, defaults to False
        :type alt_spec: bool, optional
        '''     

        if next_date and self.__run.next_run:
            self.run = self.__run.next_run
        elif prev_date and self.__run.previous_run:
            self.run = self.__run.previous_run
        elif alt_spec and self.__run.alt_spectrum:
            self.run = self.__run.alt_spectrum
        
        if next_view:
            self.ui.plateViewer.current_page += 1
            
        elif prev_view:
            self.ui.plateViewer.current_page -= 1

        label_dict = self.parse_label_checkboxes()
        added_wells = self.ui.plateViewer.tile_graphics_wells(
            next_date = next_date, prev_date=prev_date, alt_spec=alt_spec,
            label_dict=label_dict
        )
        self.apply_plate_settings()
        self.set_plate_label()
        self.set_time_resolved_buttons()
        self.set_alt_spectrum_buttons()
        self.set_spin_box_range()
            
    
    def apply_image_filters(self):
        '''Wrapper function around plateViewer `deemphasize_filtered_images`
        which changes the opacity of currently displayed images based on if
        their labels meet the currently selected image filter checkboxes.
        '''
        self.ui.plateViewer.set_scene_opacity_from_filters(
            self.selected_classifications, self.human, self.marco, 
            self.favorite
        )
        
    
    def apply_color_mapping(self):
        '''Applies the current color mapping to images. Changes the color of
        images based on their classifications. The color mapping is altered by
        the user by using the color combo boxes to select a color for each
        image classification (Crystal, Clear, ...). The user can also select
        what classifier the image classifications should be in reference to;
        either Marco or human classifications. 
        '''
        human = self.ui.radioButton_2.isChecked()
        self.ui.plateViewer.set_scene_colors_from_filters(
            self.color_mapping, self.ui.horizontalSlider.value() / 100,
            human
        )

    def set_time_resolved_buttons(self):
        if self.__run:
            if self.__run.next_run:
                self.ui.pushButton_21.setEnabled(True)
            else:
                self.ui.pushButton_21.setEnabled(False)
            if self.__run.previous_run:
                self.ui.pushButton_20.setEnabled(True)
            else:
                self.ui.pushButton_20.setEnabled(False)
        else:
            self.ui.pushButton_20.setEnabled(False)
            self.ui.pushButton_21.setEnabled(False)

    def set_alt_spectrum_buttons(self):
        if self.__run and self.__run.alt_spectrum:
            self.ui.pushButton_22.setEnabled(True)
        else:
            self.ui.pushButton_22.setEnabled(False)


    
    def set_spin_box_range(self):
        '''Set the allowed range for the page navigation spinbox.
        '''
        self.ui.spinBox.setRange(1, self.ui.plateViewer.total_pages)
    
    def set_current_page(self, page_number):
        '''Set the current page number

        :param page_number: The new page number
        :type page_number: int
        '''
        self.ui.plateViewer.current_page = page_number
        self.show_current_plate()
