from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBitmap, QBrush, QColor, QIcon, QPainter, QPixmap
from PyQt5.QtWidgets import QGraphicsColorizeEffect, QGraphicsScene
from PyQt5.QtCore import Qt, pyqtSignal
from polo import (ALLOWED_IMAGE_COUNTS, COLORS, IMAGE_CLASSIFICATIONS)
from polo.crystallography.cocktail import UnitValue
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
        of pre-set numbers of images from 24 to 96 images at a time.

        :param parent: Parent widget
        :type parent: QWidget
        :param run: Run to display, defaults to None
        :type run: Run, optional
        '''
        super(PlateInspectorWidget, self).__init__(parent)
        self.ui = Ui_PlateInspector()
        self.ui.setupUi(self)
        self.run = run
        self.ui.plateViewer.run = self._run

        self._set_color_comboboxs()
        self._set_color_options()
        self._set_image_count_options()

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

        self.ui.comboBox_7.currentIndexChanged.connect(self._set_images_per_page)

        self.ui.plateViewer.changed_images_per_page_signal.connect(
        self.ui.plateVis.setup_view
        )
        self.ui.plateViewer.changed_page_signal.connect(
            self.ui.plateVis.set_selected_block)


        self.ui.spinBox.setRange(1, 1)
        self.ui.spinBox.valueChanged.connect(self._set_current_page)

        self._set_time_resolved_buttons()
        self._set_alt_spectrum_buttons()
    
    @property
    def selected_classifications(self):
        '''Returns a list that includes only image classifications that are
        selected via the image filtering checkboxes. Also see
        `image_type_checkboxes` property.

        :return: List of currently selected image classifications. Images of
                whos classification is in this list should be shown / 
                emphasized to the user.
        :rtype: list

        '''
        return [k for k in self.image_type_checkboxes 
                if self.image_type_checkboxes[k].isChecked()]
    
    @property
    def human(self):
        '''Status of human image classification checkbox
        
        :return: State of the human filter checkbox
        :rtype: bool
        '''
        return self.ui.checkBox_21.isChecked()
    
    @property
    def marco(self):
        '''Status of marco image classification checkbox

        :return: State of the marco filter checkbox
        :rtype: bool
        '''

        return self.ui.checkBox_22.isChecked()
    
    @property
    def favorite(self):
        '''Status of the `favorite` checkbox filter.

        :return: State of the favorite checkbox
        :rtype: bool
        '''
        return self.ui.checkBox_6.isChecked()
    
    @property
    def color_mapping(self):
        '''Creates a color mapping dictionary from the current selections of the
        color selector comboboxes. Each image classification maps to a color
        or the string "none" to tell the plateViewer to not color that
        image type.
        '''
        mapping = {}
        for each_combo_box, img_class in zip(self.color_combos,
                                             IMAGE_CLASSIFICATIONS):
            mapping[img_class] = COLORS[each_combo_box.currentText()]
        return mapping
    
    @property
    def run(self):
        return self._run
    
    @run.setter
    def run(self, new_run):
        '''Sets run attribute to the given run. Setting the run also sets the
        run for the `plateViewer` widget and checks if time resolved and
        spectrum navigation should be enabled by calling 
        :func:`~polo.widgets.plate_inspector_widget.PlateInspector._set_time_resolved_buttons`
        and :func:`~polo.widgets.plate_inspector_widget.PlateInspector._set_alt_spectrum_buttons`.
        '''
        if new_run:
            self._run = new_run
            self.ui.plateViewer.run = new_run
        else:
            self._run = None
            self.ui.plateViewer.run = None

        self._set_time_resolved_buttons()
        self._set_alt_spectrum_buttons()
    
    def _set_images_per_page(self):
        '''Private method that tells the `plateViewer` widget to set 
        its `images_per_page` atttribute to the value specified in the 
        images per page comboBox.
        '''
        self.ui.plateViewer.images_per_page = self.images_per_page[
                self.ui.comboBox_7.currentIndex()]
    
    def _set_color_comboboxs(self):
        '''Private method that sets the label text associated with each color
        selector combobox. Should be called in the `__init__` method before
        the widget is shown to the user.
        '''
        self.color_combos = [
            self.ui.comboBox_3, self.ui.comboBox,
            self.ui.comboBox_5, self.ui.comboBox_4
            ]
        labels = [
            self.ui.label_19, self.ui.label_4,
            self.ui.label_21, self.ui.label_20
            ]
        for each_label, each_class in zip(labels, IMAGE_CLASSIFICATIONS):
            each_label.setText(each_class)
    
    def _set_image_count_options(self):
        '''Private Helper method to be called in `__init__` that sets the options
        for number of images per view.
        '''
        self.ui.comboBox_7.clear()
        self.ui.comboBox_7.addItems([str(i) for i in self.images_per_page])
        self.ui.comboBox_7.setCurrentIndex(0)

    def _set_color_options(self):
        '''
        Private methods that uses the `COLORS` constant to set the color options 
        for each color selector combobox in the image coloring tab.
        '''
        colors, i  = list(COLORS.keys()), 0
        for each_combobox in self.color_combos:
            each_combobox.addItems(colors)
            if colors[i] == 'none':
                i+=1
            each_combobox.setCurrentIndex(i)
            i += 1

    def _parse_label_checkboxes(self):
        '''Private method that reads values from checkboxes related to image filtering.
        Returns a dictionary where keys are the labels of the checkboxes
        which should also be the possible image classifications and values
        are the state of the checkbox (True or False).

        Returned dictionary will have following structure.

        .. code-block:: python

            {
            'Crystals': True,
            'Clear': False,
            'Precipitate': True,
            'Other': False
            }

        :return: Dict of checkbox states.
        :rtype: dict
        '''
        boxes = [
                 self.ui.checkBox, self.ui.checkBox_2, self.ui.checkBox_3,
                 self.ui.checkBox_4, self.ui.checkBox_5
                ]
        return {b.text(): b.isChecked() for b in boxes}

    def _set_plate_label(self):
        '''
        Private method to change the plate label to tell the user what view or 
        "page" they are currently looking at.
        '''
        self.ui.label_18.setText(
            'Page {} of {}'.format(
            self.ui.plateViewer.current_page,
            self.ui.plateViewer.total_pages)
        )
    
    def _apply_color_mapping(self):
        '''Applies the current color mapping to displayed images. Images
        are colored based on either their human or marco classification.
        '''
        human = self.ui.radioButton_2.isChecked()
        self.ui.plateViewer.set_scene_colors_from_filters(
            self.color_mapping, self.ui.horizontalSlider.value() / 100,
            human
        )

    def _apply_image_filters(self):
        '''Wrapper function around `plateViewer`
        :func:`~polo.widgets.plate_viewer.plateViewer.deemphasize_filtered_images`
        which changes the opacity of currently displayed images based on
        their classifications.
        '''
        self.ui.plateViewer.set_scene_opacity_from_filters(
            self.selected_classifications, self.human, self.marco, 
            self.favorite
        )
    def _set_time_resolved_buttons(self):
        '''Private helper function that determines if navigation buttons 
        that display alt spectrum images, previous and next date images 
        can be used.
        '''
        if self._run:
            if self._run.next_run:
                self.ui.pushButton_21.setEnabled(True)
            else:
                self.ui.pushButton_21.setEnabled(False)
            if self._run.previous_run:
                self.ui.pushButton_20.setEnabled(True)
            else:
                self.ui.pushButton_20.setEnabled(False)
        else:
            self.ui.pushButton_20.setEnabled(False)
            self.ui.pushButton_21.setEnabled(False)

    def _set_alt_spectrum_buttons(self):
        '''Private helper function similar to 
        :func:`~polo.widgets.plate_viewer.plateViewer._set_time_resolved_buttons`
        that determines if the navigation button that allows users to view 
        alt spectrum images should be enabled. If conditions are not met then 
        the button is disabled.
        '''
        if self._run and self._run.alt_spectrum:
            self.ui.pushButton_22.setEnabled(True)
        else:
            self.ui.pushButton_22.setEnabled(False)
    
    def _set_spin_box_range(self):
        '''Set the allowed range for the page navigation spinbox.
        '''
        self.ui.spinBox.setRange(1, self.ui.plateViewer.total_pages)
    
    def _set_current_page(self, page_number):
        '''Set the current page number and show the view for that page by
        calling :func:`~polo.widgets.plate_inspector_widget.PlateInspector.show_current_page`

        :param page_number: The new page number
        :type page_number: int
        '''
        self.ui.plateViewer.current_page = page_number
        self.show_current_plate()

    def set_aspect_ratio_mode(self):
        '''Sets the `preserve_aspect` attribute based on the status of
        the preserve aspect ratio checkbox available to the user. Preserving
        aspect ratio results in displaying undistorted crystallization images 
        but utilizes available display space less efficiently.
        '''
        self.ui.plateViewer.preserve_aspect = self.ui.checkBox_29.isChecked()
    
    def reset_all(self):
        '''Method to un-check all user selected settings.
        '''
        for widget in self.ui.groupBox_26.children():
            if isinstance(widget, QtWidgets.QCheckBox):
                widget.setChecked(False)
        self.apply_plate_settings()
    
    def apply_plate_settings(self):
        '''Parses checkboxes in the Plate View tab to determine what behavior
        for the plateViewer widget is requested by the user.
        '''
        if self._run:
            self.ui.plateViewer.images_per_page = self.images_per_page[
                self.ui.comboBox_7.currentIndex()]
            if self.ui.checkBox_27.isChecked():
                self._apply_image_filters()
            else:
                self.ui.plateViewer.emphasize_all_images()
            if self.ui.checkBox_28.isChecked():
                self._apply_color_mapping()
            else:
                self.ui.plateViewer.decolor_all_images()
    
    def show_current_plate(self, next_view=False, prev_view=False,
                           next_date=False, prev_date=False,
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

        if next_date and self._run.next_run:
            self.run = self._run.next_run
        elif prev_date and self._run.previous_run:
            self.run = self._run.previous_run
        elif alt_spec and self._run.alt_spectrum:
            self.run = self._run.alt_spectrum
        
        if next_view:
            self.ui.plateViewer.current_page += 1
            
        elif prev_view:
            self.ui.plateViewer.current_page -= 1

        label_dict = self._parse_label_checkboxes()
        self.ui.plateViewer.tile_images_onto_scene(label_dict=label_dict)
        self.apply_plate_settings()
        self._set_plate_label()
        self._set_time_resolved_buttons()
        self._set_alt_spectrum_buttons()
        self._set_spin_box_range()