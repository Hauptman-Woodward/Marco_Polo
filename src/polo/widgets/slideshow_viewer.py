from PyQt5 import QtCore, QtGui, QtWidgets
from polo import IMAGE_CLASSIFICATIONS
from polo.crystallography.image import Image
from polo.crystallography.run import Run, HWIRun
from polo import make_default_logger
import copy

logger = make_default_logger(__name__)


class Slide():
    '''
    Holds an Image object to be shown in the current slide show. Slides are
    the nodes of the current slide show linked list. The list is navigated by
    instances of Carousel class.

    :param image: Image. Image object to be displayed for this slide.
    :param next_slide: Slide. Next image in the slideshow to be displayed.
    :param prev_slide: Slidee. Previous slide in the slideshow to be displayed.
    :param slide_number: Int. Index of the slide, should be base 0.
    '''

    def __init__(self, image, next_slide=None, prev_slide=None, slide_number=None):
        
        self.image = image  # image object holds well data
        self.next_slide = next_slide
        self.prev_slide = prev_slide
        self.slide_number = slide_number


class Carousel():
    '''
    Carousel class instance control how individual slides are
    displayed and handles navigation between slides. It acts as the
    interface and constructor for liked list formed of a series of
    connected slides.

    :param current_slide: Slide. The current slide in the carousel.
    '''

    # linked list class to hold the current slides in
    # the slideshow view
    def __init__(self):
        self.current_slide = None

    def add_slides(self, ordered_images):
        '''
        Sets up linked list consisting of nodes of Slide instances. The list
        is circular and bi-directional. Sets self.current_slide to the first
        slide in the linked list.

        :param ordered_images: a list of Image objects to create the linked list\
            from. The order of the images will be reflected by the linked list.
        :returns: First slide in linked list
        :rtype: Slide
        '''
        if ordered_images:
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

            logger.info('Added {} new slides to {}'.format(
                len(ordered_images), self
            ))
            return first_slide

    @property
    def current_slide(self):
        return self.__current_slide

    @current_slide.setter
    def current_slide(self, new_slide):
        '''
        Setter function for the current_slide property. 

        :param new_slide: New current slide.
        :type new_slide: Slide 
        '''
        if new_slide:
            self.__current_slide = new_slide
        else:
            self.__current_slide = None

    def controls(self, next_slide=False, prev_slide=False):
        '''
        Function that controls the navigation through the slides
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
        self.__zoom = 0
        self.__empty = True
        self.__scene = QtWidgets.QGraphicsScene(self)
        self.__photo = QtWidgets.QGraphicsPixmapItem()
        self.__scene.addItem(self.__photo)
        self.setScene(self.__scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

    # current image will be an actual image to show to the screen
    # slideshow images are images in the que that are ready to go

    def display_current_image(self):
        '''
        Renders the Image instance currently stored in the current_image\
            attribute.

        :returns: None
        '''
        self.__empty = False
        self.set_image(self.__photo)

    def hasPhoto(self):
        return not self.__empty

    def fitInView(self, scale=True):
        rect = QtCore.QRectF(self.__photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self.__zoom = 0

    def set_image(self, pixmap=None):
        '''Sets a pixelmap as the current photo and fits into view.

        :param pixmap: Pixelmap to display, defaults to None
        :type pixmap: Pixmap, optional
        '''
        self.__zoom = 0
        if pixmap:
            self.__empty = False
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self.__photo.setPixmap(pixmap)
        else:
            self.__empty = True
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self.__photo.setPixmap(QtGui.QPixmap())
        self.fitInView()

    def wheelEvent(self, event):
        '''Handles mouse wheel events to allow for scaling for zooming in and
        out of the currently displayed image.

        :param event: Mouse scroll wheel event
        :type event: QEvent
        '''
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self.__zoom += 1
            else:
                factor = 0.8
                self.__zoom -= 1
            if self.__zoom > 0:
                self.scale(factor, factor)
            elif self.__zoom == 0:
                self.fitInView()
            else:
                self.__zoom = 0

    def toggleDragMode(self):
        '''Turns drag mode on and off.
        '''
        if self.dragMode() == QtWidgets.QGraphicsView.ScrollHandDrag:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        elif not self.__photo.pixmap().isNull():
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    def mousePressEvent(self, event):
        '''Handles mouse press events.

        :param event: Mouse press event
        :type event: QEvent
        '''
        if self.__photo.isUnderMouse():
            self.photoClicked.emit(self.mapToScene(event.pos()).toPoint())
        super(PhotoViewer, self).mousePressEvent(event)
    

class SlideshowViewer(PhotoViewer):
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

    def __init__(self, parent, run=None, current_image=None):
        super(SlideshowViewer, self).__init__(parent)
        self.run = run
        self.current_image = current_image
        self.__carousel = Carousel()
        logger.info('Made {}'.format(self))
        
    @property
    def run(self):
        return self.__run

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
            self.__run = new_run
            logger.info(
                'Run attribute of {} set to {}'.format(self, self.__run))
            self.update_slides_from_filters(
                image_types=set(IMAGE_CLASSIFICATIONS), human=False, marco=False
            )
        else:
            logger.info('Failed to set {} as __run attribute of {}'.format(
                new_run, self
            ))
    def set_current_image_by_well_number(self, well_number):
        if self.run:
            try:
                self.current_image = self.run.images[well_number-1]
            except IndexError:
                logger.warning('Attempted to set current image to non-existant well number')

    def carousel_controls(self, next_image=False, previous_image=False):
        '''
        Wrapper around the method `controls` in Carousel class. Sets the
        current_image attribute to the image contained in __carousel
        current slide after the advance or retreat operation is applied to
        the Carousel instance.

        :param next_image: If True, tells carousel to advance by one slide.
        :param previous_image: If True, tells carousel to retreat by one slide.

        :returns The current image.
        :rtype Image
        '''
        if isinstance(self.__carousel, Carousel) and self.__carousel.current_slide:
            if next_image:
                self.__carousel.controls(next_slide=True)
            elif previous_image:
                self.__carousel.controls(prev_slide=True)

            self.current_image = self.__carousel.current_slide.image
            return self.current_image

            # self.display_current_image()

    def update_slides_from_filters(self, image_types, human, marco, favorite=False):
        '''
        Creates new Carousel slides based on selected image filters.
        Sets the current_image attribute to the image contained at
        the current slide of __carousel attribute.

        :param image_types: Set of image classifications to include in results.
        :type image_types: set
        :param human: If True, image_types refers to human classifcation of the image.
        :type human: bool
        :param marco: If True, image_types referes to the machine (MARCO) classificatio\
            of the image.
        :type marco: bool
        '''
        if self.run:
            images = list(self.run.image_filter_query(
                image_types, human, marco))
            if favorite:  # probably move this to image filter query soon
                images = [i for i in images if i.favorite]
            
            self.__carousel.add_slides(images)
            self.current_image = self.__carousel.current_slide.image
            logger.info('Applied filters {} human: {} marco: {} to {}'.format(
                image_types, human, marco, self
            ))

    def display_current_image(self):
        '''
        Renders the Image instance currently stored in the current_image\
            attribute.

        :returns: None
        '''
        cur_img = self.current_image
        cur_img.alt_image
        if isinstance(cur_img, Image):
            pixmap = cur_img.get_pixel_map()
            self.set_image(pixmap)
        else:
            logger.warning('Failed to set current image to {} at {}'.format(
                self.current_image, self
            ))

    def get_cur_img_cocktail_str(self):
        '''
        Checks if current image is of type Image and if True returns\
            the current image's cocktail info as a string.

        :returns: Current image cocktail string
        :rtype: String
        '''
        if isinstance(self.current_image, Image):
            return str(self.current_image.cocktail)

    def get_cur_img_meta_str(self):
        if isinstance(self.current_image, Image):
            return str(self.current_image)

    def set_alt_image(self, next_date=False, prev_date=False, alt_spec=False):
        '''
        Sets the current_image attribute to an alternative image\
            based on user selection.
        :param next_date: If True, set current image to the current_image's\
            next image date.
        :type next_date: bool
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