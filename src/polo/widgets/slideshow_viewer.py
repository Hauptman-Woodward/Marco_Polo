import copy
import math

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QFont

from polo import IMAGE_CLASSIFICATIONS, make_default_logger
from polo.crystallography.image import Image
from polo.crystallography.run import HWIRun, Run

logger = make_default_logger(__name__)


class Slide():
    '''Holds an Image object to be shown in the current slide show. Slides are
    the nodes of the current slide show linked list. The list is navigated by
    instances of Carousel class.

    :param image: Image. Image object to be displayed for this slide.
    :param next_slide: Slide. Next image in the slideshow to be displayed.
    :param prev_slide: Slide. Previous slide in the slideshow to be displayed.
    :param slide_number: Int. Index of the slide, should be base 0.
    '''

    def __init__(self, image, next_slide=None, prev_slide=None, slide_number=None):
        '''Acts like a slide in a slideshow carousel. Holds an Image object instance
        as the contents of the slide. Forms a linked list with other slides through
        the `next_slide` and `prev_slide` attributes which act as the forwards
        and backwards pointers to other slides.

        :param image: Image that this slide will display
        :type image: Image
        :param next_slide: Next slide in the slideshow, defaults to None
        :type next_slide: Slide, optional
        :param prev_slide: Previous slide in the slideshow, defaults to None
        :type prev_slide: Slide, optional
        :param slide_number: Index of this slide in the slideshow, defaults to None
        :type slide_number: int, optional
        '''

        self.image = image  # image object holds well data
        self.next_slide = next_slide
        self.prev_slide = prev_slide
        self.slide_number = slide_number
    
    def __repr__(self):
        return '{}: {}'.format(self.image.path, self.slide_number)


class Carousel():
    '''The Carousel class handles navigation between `Slide` instances.
    '''

    # linked list class to hold the current slides in
    # the slideshow view
    def __init__(self):
        self.current_slide = None

    def add_slides(self, ordered_images, sort_function=None):
        '''Sets up linked list consisting of nodes of Slide instances. The list
        is circular and bi-directional. Sets self.current_slide to the first
        slide in the linked list. The order of the slides in the linked list
        will reflect the order of the images in the `ordered_images` argument.

        :param ordered_images: a list of Image objects to create the linked list\
            from. The order of the images will be reflected by the linked list.
        :returns: First slide in linked list
        :rtype: Slide
        '''
        if ordered_images:
            if sort_function:
                sorted_images = sort_function(ordered_images)
                if sorted_images: ordered_images = sorted_images
            first_slide = Slide(ordered_images.pop(0), slide_number=0)
            cur_slide = first_slide
            while ordered_images:
                next_slide = Slide(ordered_images.pop(0))
                cur_slide.next_slide = next_slide
                next_slide.prev_slide = cur_slide
                next_slide.slide_number = next_slide.prev_slide.slide_number + 1
                cur_slide = next_slide

            cur_slide.next_slide = first_slide
            first_slide.prev_slide = cur_slide
            self.current_slide = first_slide
            # circ the link list
            return first_slide

    @property
    def current_slide(self):
        return self._current_slide

    @current_slide.setter
    def current_slide(self, new_slide):
        '''
        Setter function for the current_slide property. 

        :param new_slide: New current slide.
        :type new_slide: Slide 
        '''
        if new_slide:
            self._current_slide = new_slide
        else:
            self._current_slide = None

    def controls(self, next_slide=False, prev_slide=False):
        '''Controls the navigation through the slides
        in the carousel. Does not control access to alternative
        images that may be available to the user.

        :param next_slide: If set to True, tells the carousel to\
             advance one Slide
        :type next_slide: bool
        :param prev_slide: If set to True, tells the carousel to\
             retreat by one Slide
        :type prev_slide: bool
        '''
        if self.current_slide:
            self.current_slide.image.delete_all_pixmap_data()
            if next_slide:
                self.current_slide = self.current_slide.next_slide
            elif prev_slide:
                self.current_slide = self.current_slide.prev_slide


class PhotoViewer(QtWidgets.QGraphicsView):
    photoClicked = QtCore.pyqtSignal(QtCore.QPoint)
    '''
    Wrapper class around QGraphicsView and displays image to the user
    in the slideshow viewer tab of the mainwindow.

    :param run: Current run whose images are to be shown by the viewer.
    :type run: Run
    :param parent: Parent Widget of this instance.
    :type parent: QWidget
    :param current_image: Image that is currently displayed by the viewer.
    :type current_image: Image
    :param __carousel: Carousel instance to control image navigation.
    :type __carousel: Carousel 
    '''

    def __init__(self, parent):
        super(PhotoViewer, self).__init__(parent)
        self.show_all_dates = False
        self.show_all_specs = False
        self._zoom = 0
        self._empty = True
        self.scene = QtWidgets.QGraphicsScene(self)
        #  self._photo = QtWidgets.QGraphicsPixmapItem()  attempting to remove photo and just use via scenes
        self.setScene(self.scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    # current image will be an actual image to show to the screen
    # slideshow images are images in the que that are ready to go
    # self.set_image(self._photo)  need to use scene here

    def hasPhoto(self):
        return not self._empty

    def fitInView(self, scale=True):
        rect = self.scene.itemsBoundingRect()
        #rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self._empty = False
            self.setSceneRect(rect)
            self.setScene(self.scene)  # possibly do this instead or in addition to line above
            if self.hasPhoto():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0
        else:
            self._empty = True
    
    def add_pixmap(self, pixmap):
        self.scene.addPixmap(pixmap)


    def wheelEvent(self, event):
        '''Handles mouse wheel events to allow for scaling for zooming in and
        out of the currently displayed image.

        :param event: Mouse scroll wheel event
        :type event: QEvent
        '''
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def toggleDragMode(self):
        '''Turns drag mode on and off.
        '''
        if self.dragMode() == QtWidgets.QGraphicsView.ScrollHandDrag:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    def mousePressEvent(self, event):
        '''Handles mouse press events.

        :param event: Mouse press event
        :type event: QEvent
        '''
        # if self.scene.isUnderMouse():
        self.photoClicked.emit(self.mapToScene(event.pos()).toPoint())
        super(PhotoViewer, self).mousePressEvent(event)


class SlideshowViewer(PhotoViewer):
    photoClicked = QtCore.pyqtSignal(QtCore.QPoint)
    '''Wrapper class around QGraphicsView and displays image to the user
    in the slideshow viewer tab of the main window.

    :param run: Current run whose images are to be shown by the viewer.
    :type run: Run
    :param parent: Parent Widget of this instance.
    :type parent: QWidget
    :param current_image: Image that is currently displayed by the viewer.
    :type current_image: Image
    :param __carousel: Carousel instance to control image navigation.
    :type __carousel: Carousel 
    '''

    def __init__(self, parent, run=None, current_image=None):
        super(SlideshowViewer, self).__init__(parent)
        self.run = run
        self.current_image = current_image
        self._carousel = Carousel()
        logger.info('Made {}'.format(self))

    @property
    def run(self):
        return self._run

    @run.setter
    def run(self, new_run):
        '''
        Setter function for the run attribute. Updates the current slides
        by calling update_slides_from_filters with arguements that ensure
        all images in the run are included. Effectively resets the images in
        the slideshow to reflect the new run.

        :param new_run: The run to replace the current run.
        :type new_run: Run
        '''
        if isinstance(new_run, Run) or isinstance(new_run, HWIRun):
            self._run = new_run
            logger.info(
                'Run attribute of {} set to {}'.format(self, self._run))
            self.update_slides_from_filters(
                image_types=set([]), human=False, marco=False
            )
            logger.info('Opened new run {} with name {}'.format(
                new_run, new_run.run_name
            ))
        else:  # if run is none then interpret as request to delete current run
            self._run = None
            self._carousel = Carousel()
            self.scene.clear()
            self.current_image = None

    def _set_all_dates_scene(self, image):
        '''Private method that creates a time resolved view from the Image passed
        to the `image` argument by traversing the date based
        linked list the passed image may be a node in. 

        :param image: Image to create time resolved view from
        :type image: Image
        '''
        if isinstance(image, Image):
            all_dates = image.get_linked_images_by_date()
            self.scene.clear()
            self.arrange_multi_image_scene(all_dates, render_date=True)
            self.fitInView()
    
    def _set_all_spectrums_scene(self, image):
        '''Private method that creates a view that includes all alt spectrums the Image
        passed via the `image` argument is linked to.

        :param image: Image to create the view from
        :type image: Image
        '''
        if isinstance(image, Image):
            all_specs = image.get_linked_images_by_spectrum()
            self.scene.clear()
            self.arrange_multi_image_scene(all_specs)
            self.fitInView()
            
    def _set_single_image_scene(self, image):
        '''Private method that creates a standard single image view from the image
        passed to the `image` argument.

        :param image: Image to display
        :type image: Image
        '''
        if isinstance(image, Image):
            if image.isNull():
                image.setPixmap()
            self.scene.clear()
            self.scene.addPixmap(image)
            self.fitInView()
            
    def __add_text_to_scene(self, text, x, y, size=40):
        '''Private method to add text on top of an image.

        :param text: Text to add to image
        :type text: str
        :param x: X cordinate of text
        :type x: int
        :param y: Y cordinate of text
        :type y: int
        :param size: Size of text, defaults to 40
        :type size: int, optional
        '''
        t = QtWidgets.QGraphicsTextItem()
        t.setPlainText(text)
        f = QFont()
        f.setPointSize(size)
        t.setFont(f)
        self.scene.addItem(t)
        t.setPos(x, y)

    def set_current_image_by_well_number(self, well_number):
        if self.run:
            try:
                self.current_image = self.run.images[well_number-1]
            except IndexError:
                logger.warning(
                    'Attempted to set current image to non-existant well number')

    def carousel_controls(self, next_image=False, previous_image=False):
        '''Wrapper around the :func:`~polo.widgets.slideshow_viewer.Carousel.controls`
        method. 

        :param next_image: If True, tells carousel to advance by one slide.
        :param previous_image: If True, tells carousel to retreat by one slide.

        :returns The current image.
        :rtype Image
        '''
        if isinstance(self._carousel, Carousel) and self._carousel.current_slide:
            if next_image:
                self._carousel.controls(next_slide=True)
            elif previous_image:
                self._carousel.controls(prev_slide=True)

            self.current_image = self._carousel.current_slide.image
            return self.current_image

            # self.display_current_image()

    def update_slides_from_filters(self, image_types, human, marco, favorite=False, sort_function=None):
        '''Creates new Carousel slides based on selected image filters.
        Sets the current_image attribute to the image contained at
        the current slide of __carousel attribute.

        :param image_types: Set of image classifications to include in results.
        :type image_types: set
        :param human: If True, `image_types` refers to human classification of the image.
        :type human: bool
        :param marco: If True, `image_types` refers to the machine (MARCO) classification
            of the image.
        :type marco: bool
        '''
        if self.run:
            images = list(self.run.image_filter_query(
                image_types, human, marco, favorite))
            self._carousel.add_slides(images, sort_function)
            self.current_image = self._carousel.current_slide.image

    def arrange_multi_image_scene(self, image_list, render_date=False):
        '''Helper method to arrange multiple images into the same
        view.

        :param image_list: List of images to add to the view
        :type image_list: list
        :param render_date: If True adds a date label to each image, defaults to False
        :type render_date: bool, optional
        '''
        x, y = 0, 0  # set starting cords
        for item in image_list:
            if isinstance(item, (list, tuple)):  # 2D list
                pass
                list_midpoint = math.floor(len(item) / 2)
                for sub_item in item:
                    if isinstance(item, Image):
                        pass
            elif isinstance(item, Image):
                if item.isNull():
                    item.setPixmap()
                scene_item = self.scene.addPixmap(item)
                scene_item.setToolTip(item.get_tool_tip())
                scene_item.setPos(x, y)
                if render_date and item.date:
                    self._add_text_to_scene(item.formated_date, x, y)

                x += item.width()

    def display_current_image(self):
        '''Renders the Image instance currently stored in the `current_image`
        attribute.
        '''
        cur_img = self.current_image
        if isinstance(cur_img, Image):
            # parse the flags on how to display the image here
            if self.show_all_dates:
                self._set_all_dates_scene(cur_img)
            elif self.show_all_specs:
                self._set_all_spectrums_scene(cur_img)
            else:
                self._set_single_image_scene(cur_img)

    def get_cur_img_cocktail_str(self):
        '''Retruns the `current_image` cocktail information
        as a string.

        :return: Cocktail information string
        :rtype: str
        '''
        if isinstance(self.current_image, Image):
            return str(self.current_image.cocktail)

    def get_cur_img_meta_str(self):
        '''Returns the `current_image` metadata as a string.

        :return: Metadata string
        :rtype: str
        '''
        if isinstance(self.current_image, Image):
            return str(self.current_image)

    def set_alt_image(self, next_date=False, prev_date=False, alt_spec=False):
        '''Sets the `current_image` attribute to a linked image specified by
        one of the tree boolean flags.

        :param next_date: If True, sets the `current_image`
                          to the next image by date
        :param prev_date: If True, sets the `current_image`
                          to the previous image by date
        :param alt_spec: If True, sets the `current_image`
                         to an alt spectrum image
        '''
        cur_img = self.current_image
        if next_date and cur_img.next_image:
            self.current_image = cur_img.next_image
        elif prev_date and cur_img.previous_image:
            self.current_image = cur_img.previous_image
        elif alt_spec and cur_img.alt_image:
            self.current_image = cur_img.alt_image

    def classify_current_image(self, classification):
        '''
        Changes the human classification of the current image.
        '''
        if isinstance(self.current_image, Image):
            self.current_image.human_class = classification
    

