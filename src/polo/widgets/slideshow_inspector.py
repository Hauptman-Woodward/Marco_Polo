from polo import COLORS, IMAGE_CLASSIFICATIONS, ALLOWED_IMAGE_COUNTS
from polo.crystallography.run import Run, HWIRun
from polo.utils.math_utils import *
import os
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsColorizeEffect, QGraphicsScene
from PyQt5.QtGui import QBrush, QColor, QIcon, QPixmap, QColor, QBitmap, QPainter
from polo.widgets.slideshow_viewer import PhotoViewer
from polo.utils.dialog_utils import make_message_box
from polo.designer.UI_slideshow_inspector import Ui_slideshowInspector
from polo.utils.io_utils import SceneExporter, RunSerializer
import copy
from polo import ICON_DICT, make_default_logger

logger = make_default_logger(__name__)


class slideshowInspector(QtWidgets.QWidget):
    '''The slideshowInspector widget is a primary run interface that allows
    users to view their screening images in a standard slideshow format. If
    multiple imaging runs of the sample sample exist it also allows the user to
    navigate between or simultaneously view these images.

    :param parent: Parent widget
    :type parent: QtWidget
    :param run: Run to show to the user, defaults to None
    :type run: Run or HWIRun, optional

    '''
    def __init__(self, parent, run=None):

        super(slideshowInspector, self).__init__(parent)
        self.ui = Ui_slideshowInspector()
        self.ui.setupUi(self)
        self._run = run

        self.class_buttons = [self.ui.pushButton, self.ui.pushButton_2,
                              self.ui.pushButton_5, self.ui.pushButton_3]
        self.class_checkboxs = [self.ui.checkBox, self.ui.checkBox_2,
                                self.ui.checkBox_3, self.ui.checkBox_4]

        self.ui.spinBox.valueChanged.connect(
            self._show_image_from_well_number
        )
        self._set_classification_button_labels()
        self._set_image_class_checkbox_labels()

        self.class_buttons[0].clicked.connect(
            lambda: self._classify_image(self.class_buttons[0].text())
        )
        self.class_buttons[1].clicked.connect(
            lambda: self._classify_image(self.class_buttons[1].text())
        )
        self.class_buttons[2].clicked.connect(
            lambda: self._classify_image(self.class_buttons[2].text())
        )
        self.class_buttons[3].clicked.connect(
            lambda: self._classify_image(self.class_buttons[3].text())
        )

        self.ui.pushButton_6.clicked.connect(
            lambda: self._navigate_carousel(next_image=True))
        self.ui.pushButton_7.clicked.connect(self.export_current_view)
        self.ui.pushButton_4.clicked.connect(
            lambda: self._navigate_carousel(prev_image=True))
        self.ui.pushButton_11.clicked.connect(self._submit_filters)

        self.ui.pushButton_10.clicked.connect(
            lambda: self._set_alt_image(next_date=True))
        self.ui.pushButton_9.clicked.connect(
            lambda: self._set_alt_image(prev_date=True)
        )
        self.ui.pushButton_12.clicked.connect(
            lambda: self._set_alt_image(alt_spec=True)
        )
        self.ui.checkBox_7.stateChanged.connect(
            self._mark_current_image_as_favorite
        )
        self.ui.checkBox_9.stateChanged.connect(
            lambda x: self._set_slideshow_mode(show_all_dates=x)
        )
        self.ui.checkBox_10.stateChanged.connect(
            lambda x: self._set_slideshow_mode(show_all_specs=x)
        )

    @staticmethod
    def sort_images_by_marco_confidence(images):
        '''Helper method to sort a collection of images by their MARCO
        classification confidence. Does not descriminate based on
        image classification.

        :param images: List of images to sort
        :type images: list
        :return: List of images sorted by prediction confidence
        :rtype: list
        '''
        try:
            return sorted(
                images,
                key=lambda i: float(i.prediction_dict[i.machine_class]),
                reverse=True
            )
        except Exception as e:
            logger.error('Caught {} while calling {}'.format(
                            e, slideshowInspector.sort_images_by_marco_confidence))
            return False

    @staticmethod
    def sort_images_by_cocktail_number(images):
        '''Helper method that sorts a collection of images by their
        cocktail number. Returns False if the images cannot be sorted
        by this parameter.

        :param images: List of images to be sorted
        :type images: list
        :return: List of images sorted by cocktail number, False if cannot be sorted
        :rtype: list, bool
        '''
        try:
            return sorted(
                images,
                key=lambda i: i.cocktail.number
            )
        except Exception as e:
            logger.error('Caught {} while calling {}'.format(
                            e, slideshowInspector.sort_images_by_cocktail_number))
            return False

    @staticmethod
    def sort_images_by_well_number(images):
        '''Helper method to sort a collection of images by their well number.
        If images cannot be sorted by well number (which in theory shouldn't happen)
        returns False

        :param images: List of images to be sorted
        :type images: list
        :return: List os images sorted by well number
        :rtype: list
        '''
        try:
            return sorted(
                images,
                key=lambda i: i.well_number
            )
        except Exception as e:
            logger.error('Caught {} while calling {}'.format(
                            e, slideshowInspector.sort_images_by_well_number))
            return False
    
    @staticmethod
    def sort_images_by_fastest_to_crystalize(images):
        # images must have at least one other date
        # sort more likely to return false because of this
        # could add to time res buttons enabled
        # only sorting options that could include some filtering
        def key(image):
            dates = image.get_linked_images_by_date()
            dates = sorted(dates, key=lambda i: i.date)
            for i, each_date in enumerate(dates):
                if dates[i].human_class == IMAGE_CLASSIFICATIONS[0]:
                    return i
            return len(dates)
        try:
            return sorted(images, key=key)
        except Exception as e:
            logger.error('Caught {} while calling {}'.format(
                e, SlideshowInspector.sort_images_by_fastest_to_crystallize
            ))
            return False
        
    @property
    def run(self):
        return self._run

    @run.setter
    def run(self, new_run):
        '''Setter method for `_run` attribute. Sets `_run` to `new run` and
        sets up the interface for displaying images.
        '''
        self._run = new_run
        self.ui.slideshowViewer.run = new_run
        self._display_current_image()
        self._set_time_resolved_functions()
        self._set_alt_spectrum_buttons()
        logger.info('Opened new run: {}'.format(self._run))

    @property
    def selected_classifications(self):
        '''Returns image classification keywords for any image classification
        :class:`QCheckBox` instances that are checked.

        :return: List of selected images classifications
        :rtype: list
        '''

        selected_classes = []
        for each_checkbox in self.class_checkboxs:
            if each_checkbox.isChecked():
                selected_classes.append(each_checkbox.text())
        return selected_classes

    @property
    def human(self):
        '''State of the human classifier :class:`QCheckBox`. If True, assume the user
        wants their selected image classifications to be in reference to image's
        human classification.

        :return: State of the :class:`QCheckBox`
        :rtype: bool
        '''
        return self.ui.checkBox_5.isChecked()

    @property
    def favorites(self):
        '''Returns the state of the favorite :class:`QCheckBox`.

        :return: Favorite :class:`QCheckBox` state
        :rtype: bool
        '''
        return self.ui.checkBox_8.isChecked()

    @property
    def marco(self):
        '''State of the MARCO classifier :class:`QCheckBox`. If True, assume the user
        wants their selected image classifications to be in reference to image's
        MARCO classification.

        :return: State of the :class:`QCheckBox`
        :rtype: bool
        '''
        return self.ui.checkBox_6.isChecked()

    @property
    def current_image(self):
        '''Current :class:`~polo.crystallography.image.Image` object being displayed in the `slideshowViewer`
        widget.

        :return: The current image 
        :rtype: Image
        '''
        return self.ui.slideshowViewer.current_image

    @property
    def current_sort_function(self):
        '''Return a function to use for image sorting based on current user
        radiobutton sort selections.

        :return: Sort function
        :rtype: func
        '''
        if self.ui.radioButton.isChecked():
            return slideshowInspector.sort_images_by_marco_confidence
        elif self.ui.radioButton_2.isChecked():
            return slideshowInspector.sort_images_by_cocktail_number
        elif self.ui.radioButton_3.isChecked():
            return slideshowInspector.sort_images_by_well_number
        elif self.ui.radioButton_4.isChecked():
            return slideshowInspector.sort_images_by_fastest_to_crystalize
        else:
            return None

    def _set_slideshow_mode(self, show_all_dates=False, show_all_specs=False):
        '''Private method to set the slideshowViewer mode. Either to display
        a single image, all dates or all spectrums.

        :param show_all_dates: If True sets slideshowViewer to show all
                               dates, defaults to False
        :type show_all_dates: bool, optional
        :param show_all_specs: If True sets slideshowViewer to show all
                               spectrums, defaults to False
        :type show_all_specs: bool, optional
        '''
        if show_all_dates:
            self.ui.checkBox_10.setChecked(False)
            self.ui.slideshowViewer.show_all_dates = True
            if self.run:
                self._display_current_image()
            logger.debug('Set slideshow mode to all dates')
        else:
            self.ui.slideshowViewer.show_all_dates = False
        if show_all_specs:
            self.ui.checkBox_9.setChecked(False)
            self.ui.slideshowViewer.show_all_specs = True
            if self.run:
                self._display_current_image()
            logger.debug('Set slideshow mode to all spectrums')
        else:
            self.ui.slideshowViewer.show_all_specs = False

    def _set_classification_button_labels(self):
        '''Private method that sets the labels of image classification
        buttons based on the :const:`IMAGE_CLASSIFICATIONS` constant. Should be called
        in the `__init__` method.
        '''

        for each_butt, img_class in zip(self.class_buttons,
                                        IMAGE_CLASSIFICATIONS):
            each_butt.setText(img_class)

    def _set_image_class_checkbox_labels(self):
        '''Private method to the :class:`QCheckBox` labels for imaging filtering
        from the `IMAGE_CLASSIFICATIONS` constant. Should be called in
        the `__init__` method.
        '''
        for each_checkbox, im_cls in zip(self.class_checkboxs, IMAGE_CLASSIFICATIONS):
            each_checkbox.setText(im_cls)

    def _show_image_from_well_number(self, well_number):
        '''Private method to display an image by well number.

        :param well_number: Well number of image to display
        :type well_number: int
        '''
        self.ui.slideshowViewer.set_current_image_by_well_number(well_number)
        self._display_current_image()

    def _set_favorite_checkbox(self):
        '''Private method that sets the value of the favorite :class:`QCheckBox` based
        on whether the current image is marked as a favorite or not.
        Should be used when loading an image into the view.

        An image is considered a favorite if it's `favorite` attribute ==
        True.
        '''
        if self.current_image and self.current_image.favorite:
            self.ui.checkBox_7.setChecked(True)
        else:
            self.ui.checkBox_7.setChecked(False)

    def _mark_current_image_as_favorite(self):
        '''Private method that sets the favorite label on the current
        image to the current value of the favorite :class:`QCheckBox`.

        :param favorite_status: Whether this image is a favorite or not
        :type favorite_status: bool
        '''
        if self.current_image:
            self.current_image.favorite = self.ui.checkBox_7.isChecked()
    
    def _set_slide_number_label(self):
        try:
            label = 'Image {} of {}'.format(
                self.ui.slideshowViewer.current_slide_number,
                self.ui.slideshowViewer.total_slides
                )
            self.ui.groupBox.setTitle(label)
        except Exception as e:
            raise e
            logger.error('Caught {} at {}'.format(e, self._set_slide_number_label))


    def _classify_image(self, classification):
        '''Private method to change the human classification of the current
        image.

        :param classification: Image classification
        :type classification: str
        '''

        self.ui.slideshowViewer.classify_current_image(classification)
        self._navigate_carousel(next_image=True)

    def _navigate_carousel(self, next_image=False, prev_image=False):
        '''Private method to control the carousel using boolean flags. Calls 
        :meth:`~polo.widgets.slideshow_inspector.SlideshowViewer.carousel_controls`.

        :param next_image: If True navigates to next image in carousel, 
                           defaults to False
        :type next_image: bool, optional
        :param prev_image: If True navigates to previous image in carousel,
                           defaults to False
        :type prev_image: bool, optional
        '''

        self.ui.slideshowViewer.carousel_controls(next_image, prev_image)
        self._display_current_image()

    def _display_current_image(self):
        '''Private method that displays the current image as 
        determined by the `current_image` attribute of the `slideshowViewer`
        widget and populates any widgets that display current image metadata.
        '''
        try:
            self.ui.slideshowViewer.display_current_image()

            # NOTE: User on Mac Mojave OS reported issue with meta data text
            # not updating but no errors related in the log file
            # comparison below is to get more info on this issue

            cur_cocktail_string = self.ui.textBrowser.toPlainText()
            cur_image_string = self.ui.textBrowser_2.toPlainText()

            self.ui.textBrowser_2.setText(
                self.ui.slideshowViewer.get_cur_img_meta_str())
            self.ui.textBrowser.setText(
                self.ui.slideshowViewer.get_cur_img_cocktail_str()
            )

            if isinstance(self._run, HWIRun):
                if self.ui.textBrowser_2.toPlainText() == cur_image_string:
                    logger.error('Image data display did not update')
                if self.ui.textBrowser.toPlainText() == cur_cocktail_string:
                    logger.error('Cocktail data display did not update')

            self._set_image_name()
            self._set_favorite_checkbox()
            self._set_time_resolved_functions()
            self._set_alt_spectrum_buttons()
            self._set_slide_number_label()
        except Exception as e:
            logger.error('Caught {} at {}'.format(e, self._display_current_image))
            make_message_box(
                parent=self,
                message='Failed to display current image {}'.format(e)
            ).exec_()

    def _submit_filters(self):
        '''Private method that passes the current user selected
        image filters to the slideshowViewer so the current
        slideshow contents can be adjusted to reflect the
        new filters. Displays the current image after filtering.
        '''
        self.ui.slideshowViewer.update_slides_from_filters(
            self.selected_classifications, self.human, self.marco, self.favorites,
            self.current_sort_function
        )
        logger.info(
            'Submit image filters {} Marco = {} Human = {} Favorite = {} Sort = {}'.format(
                self.selected_classifications, self.marco, self.human,
                self.favorites, self.current_sort_function
            ))
        self._display_current_image()

    def _set_alt_image(self, next_date=False, prev_date=False, alt_spec=False):
        '''Display an image linked to the current image based on
        boolean flags.

        :param next_date: If True show the current image's next
                          image by date, defaults to False
        :type next_date: bool, optional
        :param prev_date: If True, show the current image's previous
                          image by date, defaults to False
        :type prev_date: bool, optional
        :param alt_spec: If True, show the current image's alt
                         spectrum image, defaults to False
        :type alt_spec: bool, optional
        '''

        self.ui.slideshowViewer.set_alt_image(next_date, prev_date,
                                              alt_spec)
        self._display_current_image()

    def _set_image_name(self):
        '''Private method that sets current image label to the
        image's filepath basename.
        '''

        ci = self.current_image
        if ci:
            self.ui.label_2.setText(os.path.basename(str(ci.path)))

    def _set_time_resolved_functions(self):
        '''Private method that turns time resolved functions on or off 
        depending on contents of the `Run` instance referenced by 
        the `run` attribute. Time resolved functions are enabled 
        when the `run` is part of a time resolved linked list. 
        This means another `Run` instance is referenced by 
        it's `next_run` and / or `previous_run` attributes.
        '''

        if self.current_image:
            if self.current_image.next_image:
                self.ui.pushButton_10.setEnabled(True)
            else:
                self.ui.pushButton_10.setEnabled(False)
            if self.current_image.previous_image:
                self.ui.pushButton_9.setEnabled(True)
            else:
                self.ui.pushButton_9.setEnabled(False)

        else:
            self.ui.pushButton_9.setEnabled(False)
            self.ui.pushButton_10.setEnabled(False)

    def _set_alt_spectrum_buttons(self):
        '''Turns alt spectrum functions on or off depending on contents
        of the `Run` instance referenced by the `run` attribute.
        Alt spectrum buttons will be enabled if the `run` is a part
        of an alt spectrum linked list. This means another `Run`
        instance is referenced by it's `alt_spectrum` attribute.
        '''

        if self.current_image and self.current_image.alt_image:
            self.ui.pushButton_12.setEnabled(True)
        else:
            self.ui.pushButton_12.setEnabled(False)

    def export_current_view(self):
        '''Export the current view to a png file. Show the user a message box
        to tell them if the export succeeded or failed.
        '''
        try:
            save_path = QtWidgets.QFileDialog.getSaveFileName(
                self, 'Save View'
            )[0]
            if save_path:
                save_path = RunSerializer.path_suffix_checker(save_path, '.png')
            write_result = SceneExporter.write_image(
                self.ui.slideshowViewer.scene, save_path)

            if isinstance(write_result, str):
                message = 'View saved to {}'.format(write_result)
            else:
                message = 'Write to {} failed with error {}'.format(
                    save_path, write_result
                )
            make_message_box(parent=self, message=message).exec_()
        except Exception as e:
            logger.error('Caught {} at {}'.format(e, self.export_current_view))
            make_message_box(
                parent=self,
                message='Failed to export current view {}'.format(e)
            ).exec_()
