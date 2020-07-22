import math

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import (QBitmap, QBrush, QColor, QFont, QIcon, QPainter,
                         QPixmap, QPixmapCache)
from PyQt5.QtWidgets import QGraphicsColorizeEffect, QGraphicsScene

from polo import ALLOWED_IMAGE_COUNTS, COLORS, IMAGE_CLASSIFICATIONS
from polo.crystallography.run import HWIRun, Run
from polo.threads.thread import QuickThread
from polo.utils.dialog_utils import make_message_box
from polo.utils.io_utils import RunSerializer, SceneExporter
from polo.utils.math_utils import *
from polo.widgets.slideshow_viewer import PhotoViewer
from polo.windows.image_pop_dialog import ImagePopDialog


class PlateGraphicsItem(QtWidgets.QGraphicsPixmapItem):

    def __init__(self, pixmap, parent=None):
        super(PlateGraphicsItem, self).__init__(pixmap, parent)
    
    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)


class plateViewer(QtWidgets.QGraphicsView):

    subgrid_dict = {16: (4, 4), 64: (8, 8), 96: (8, 12), 1536: (32, 48)}
    changed_page_signal = pyqtSignal(int)
    changed_images_per_page_signal = pyqtSignal(tuple)

    def __init__(self, parent, run=None, images_per_page=24):
        super(plateViewer, self).__init__(parent)
        self.preserve_aspect = False  # how to fit images in scene
        self._images_per_page = images_per_page
        self._graphics_wells = None
        self._current_page = 1
        self._scene = QtWidgets.QGraphicsScene(self)
        self._scene.selectionChanged.connect(self.pop_out_selected_well)
        self._zoom = 0
        self._scene_map = {}
        self._view_cache = {}
        self.setInteractive(True)
        self.setScene(self._scene)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(self.AnchorUnderMouse)

        self.run = run  # run init last since depends on existence of other attributes

    @staticmethod
    def well_index_to_subgrid(i, c_r, c_c, p_r, p_c):
        '''Find the linear index of the subgrid that a particular index belongs to
        within a larger grid. For example, ou are given a list of length 16.
        The list is reshaped into a 4 x 4
        2D list. We divide the new grid into 4 quadrants each 2 X 2 and label them
        with an index (0, 1, 2, 3). Given an index of the original list we want to
        find the subgrid it belongs to. 

        :param i: Index of point to locate in the 1D list
        :type i: int
        :param c_r: Number of rows in each subgrid
        :type c_r: int
        :param c_c: Number of columns in each subgrid
        :type c_c: int
        :param p_r: Number or rows in the entire grid
        :type p_r: int
        :param p_c: Number of columns in the entire grid
        :type p_c: int
        :return: Index of the subgrid the index `i` belongs to
        :rtype: int
        '''
        def cord_finder():
            row = math.floor(i / p_c)
            col = i - (p_c * row)
            return row, col

        r, c = cord_finder()
        # chunk_rows = int(p_r / c_r)
        chunk_cols = int((p_c / c_c))
        c_x, c_y = math.floor(r / c_r), math.floor(c / c_c)
        return c_x * chunk_cols + c_y

    @property
    def images_per_page(self):
        '''Number of images in the current page.

        :return: Number of images
        :rtype: int
        '''
        return self._images_per_page

    @images_per_page.setter
    def images_per_page(self, new_num):
        if new_num != self._images_per_page:
            self._images_per_page = new_num
            self._current_page = 1

    @property
    def total_pages(self):
        '''Total number of pages based on the number of images per page
        and the number of images in the current run.

        :return: Number of pages
        :rtype: int
        '''
        if self.run and self.images_per_page:
            return math.ceil(len(self.run) / self.images_per_page)
        else:
            return 0

    @property
    def view_dims(self):
        '''Current view dimensions in pixels.

        :return: Width and height of the view
        :rtype: tuple
        '''
        return self.width(), self.height()

    @property
    def aspect_ratio(self):
        '''Current "best" aspect ratio for the view given the size of the
        view and the number of images that need to be fit into the view.

        :return: Dimensions of the image grid, in images
        :rtype: tuple
        '''
        if self.run and self.images_per_page:
            view_w, view_h = self.view_dims
            return best_aspect_ratio(view_w, view_h, self.images_per_page)
        else:
            return 0, 0

    @property
    def current_page(self):
        '''Current page

        :return: Current page
        :rtype: int
        '''
        return self._current_page

    @current_page.setter
    def current_page(self, new_page_number):
        if new_page_number > self.total_pages:
            new_page_number = 1
        elif new_page_number < 1:
            new_page_number = self.total_pages
        self._current_page = new_page_number

    @property
    def run(self):
        '''The current run being displayed.

        :return: The current run
        :rtype: HWIRun
        '''
        return self._run

    @run.setter
    def run(self, new_run):
        self._run = new_run
        self._scene.clear()
        QPixmapCache.clear()

    def _get_visible_wells(self, page=None):
        '''Return indices of images that should be shown in the
        current page. A page is equivalent to a subsection of a
        larger screening plate.

        :param page: Page number to find images for, defaults to None
        :type page: int, optional
        :yield: image index
        :rtype: int
        '''
        if not page:
            page = self.current_page

        r, c = self.subgrid_dict[self.images_per_page]
        # dims of grid to show
        p_r, p_c = self.subgrid_dict[len(self.run)]
        # dims of entire plate
        for i in range(0, len(self.run)):  # size of plate
            plate_index = plateViewer.well_index_to_subgrid(i, r, c, p_r, p_c)
            plate_index += 1
            if plate_index == page:
                yield i

    def _make_image_label(self, image, label_dict, font_size=35):
        '''Private helper method for creating label strings to overlay onto
        each image in the view.

        :param image: Image to create label from
        :type image: Image
        :param label_dict: Dictionary of image attributes to include in the label
        :type label_dict: dict
        :param font_size: Font size for the label, defaults to 35
        :type font_size: int, optional
        :return: QGraphicsTextItem with label text set
        :rtype: QGraphicsTextItem
        '''
        template, text = '{}: {}', []
        if label_dict:
            for k in sorted(label_dict.keys()):
                if k == 'Well' and label_dict[k]:
                    text.append(template.format(k, image.well_number))
                elif k == 'Date' and label_dict[k]:
                    text.append(template.format(k, image.formated_date))
                elif k == 'Cocktail Number' and label_dict[k] and image.cocktail:
                    text.append(template.format(k, image.cocktail.number))
                elif k == 'Human Classification' and label_dict[k]:
                    text.append(template.format(k, image.human_class))
                elif k == 'MARCO Classification' and label_dict[k]:
                    text.append(template.format(k, image.machine_class))

            t = QtWidgets.QGraphicsTextItem()
            t.setPlainText('\n'.join(text))
            f = QFont()
            f.setPointSize(font_size)
            t.setFont(f)

            return t

    def _set_prerender_info(self, item, image):
        '''Private helper method that sets flags and the tooltip for
        GraphicsItems before they are added to the GraphicsScene.

        :param item: GraphicsItem that is to be added to the scene
        :type item: QGraphicsItem
        :param image: Image who's data will be used to label the GraphicsItem
        :type image: Image
        :return: QGraphicsItem
        :rtype: QGraphicsItem
        '''
        item.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        item.setToolTip(image.get_tool_tip())  # pixmap is Image

        return item

    def tile_images_onto_scene(self, label_dict={}):
        '''Calculates images that should be shown based on the current page
        and the number of images per page. Then tiles these images into a grid,
        adding them to `_scene` attribute. 

        :param label_dict: Dictionary of Image attributes to pass along to
                           :func:`~polo.widgets.plate_viewer.plateViewer._make_image_label`
                           to create image labels, defaults to {}
        :type label_dict: dict, optional
        '''
        if self.run:
            QtWidgets.QApplication.setOverrideCursor(Qt.WaitCursor)
            [item.data(0).delete_all_pixmap_data() for item in self._scene.items()
             if isinstance(item, QtWidgets.QGraphicsPixmapItem)]
            # for now delete all previous pixmap data from ram

            _, stride = self.subgrid_dict[self.images_per_page]
            cur_x_pos, cur_y_pos = 0, 0  # position to place image in pixels
            row_height = 0  # height of tallest image in a given row of images

            images = [self.run.images[i] for i in self._get_visible_wells()]
            _, stride = self.subgrid_dict[self.images_per_page]
            self._scene.clear()

            for i, image in enumerate(images):
                if i % stride == 0 and i != 0:
                    cur_y_pos += row_height
                    row_height, cur_x_pos, = 0, 0  # reset row height for next row

                if image.isNull():
                    image.setPixmap()

                item = self._scene.addPixmap(image)
                item.setPos(cur_x_pos, cur_y_pos)
                label = self._make_image_label(image, label_dict)
                if label:
                    self._scene.addItem(label)
                    label.setPos(cur_x_pos, cur_y_pos)
                item.setData(0, image)
                self._set_prerender_info(item, image)
                if image.height() > row_height:
                    row_height = image.height()
                cur_x_pos += image.width()

            self._scene.selectionChanged.connect(self.pop_out_selected_well)

            self.setScene(self._scene)
            self.fitInView(self._scene, self.preserve_aspect)
            QtWidgets.QApplication.restoreOverrideCursor()
            self.changed_images_per_page_signal.emit(
                self.subgrid_dict[self._images_per_page]
            )
            self.changed_page_signal.emit(self._current_page)

    def set_scene_opacity_from_filters(self, image_types, human=False,
                                       marco=False, favorite=False,
                                       filtered_opacity=0.2):
        '''Sets the opacity of all items in the current scene (`_scene` attribute)
        based on image filtering criteria. Allows for highlighting images that
        meet specific qualifications such has having a MARCO classification of
        crystals. Images that do not meet the set filter requirements will have
        their opacity set to the value specificed by the `filtered_opacity`
        argument.

        :param image_types: Image classifications to select for.
        :type image_types: set of list
        :param human: If True, use human classification to determine image
                      classification, defaults to False
        :type human: bool, optional
        :param marco: If True, use MARCO classification to determine image
                      classification , defaults to False
        :type marco: bool, optional
        :param favorite: If True, image must be favorited to be
                         selected, defaults to False
        :type favorite: bool, optional
        :param filtered_opacity: Set the opacity for images that do not need the
                                 filtering requirements, defaults to 0.2
        :type filtered_opacity: float, optional
        '''
        for item in self._scene.items():
            if isinstance(item, QtWidgets.QGraphicsPixmapItem):
                image = item.data(0)
                if image.standard_filter(image_types, human, marco, favorite):
                    item.setOpacity(1)
                else:
                    # did not meet the filtered criteria
                    item.setOpacity(filtered_opacity)

    def set_scene_colors_from_filters(self, color_mapping, strength=0.5, human=False):
        '''Set the color of images based on their current classifications. Very similar
        to :func:`~polo.widgets.plate_viewer.plateViewer.set_opacity_from_filters`.
        Images can be colored by their MARCO or human classification.

        :param color_mapping: Dictionary that maps image classifications to QColors
        :type color_mapping: dict
        :param strength: Image color strength, defaults to 0.5
        :type strength: float, optional
        :param human: If True, use the human classification to color images,
                      defaults to False
        :type human: bool, optional
        '''
        for item in self._scene.items():
            effect = None
            if isinstance(item, QtWidgets.QGraphicsPixmapItem):
                image, color = item.data(0), None
                if human:
                    if image.human_class in color_mapping:
                        color = color_mapping[image.human_class]
                elif image.machine_class in color_mapping:
                    color = color_mapping[image.machine_class]
                if color:
                    effect = QGraphicsColorizeEffect()
                    effect.setColor(color)
                    effect.setStrength(strength)
                item.setGraphicsEffect(effect)

    def fitInView(self, scene, preserve_aspect=False):
        '''Fit items added to `_scene` attribute into the available
        display space.

        :param scene: QGraphicsScene to fit
        :type scene: QGraphicsScene
        :param preserve_aspect: If True, preserves the aspect ratio of
                                item is the scene, defaults to False
        :type preserve_aspect: bool, optional
        '''
        self.setSceneRect(scene.itemsBoundingRect())
        if preserve_aspect:
            super(plateViewer, self).fitInView(scene.itemsBoundingRect(),
                                               Qt.KeepAspectRatio)
        else:
            super(plateViewer, self).fitInView(scene.itemsBoundingRect())

    def wheelEvent(self, event):
        '''Handle Qt wheelEvents by setting the `_zoom` attribute. Allows users
        to zoom in and out of the current view.

        :param event: event
        :type event: QEvent
        '''
        if event:
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView(self._scene, self.preserve_aspect)
            else:
                self._zoom = 0

    def pop_out_selected_well(self):
        '''Helper method to handle image selection and open an ImagePopDialog
        that displays the selected image in a pop out view.
        '''
        selection = self._scene.selectedItems()
        if selection:
            image = selection[0].data(0)
            pop_out = ImagePopDialog(image, parent=self)
            pop_out.setWindowModality(Qt.ApplicationModal)
            pop_out.show()
            self._scene.clearSelection()

    def emphasize_all_images(self):
        '''Returns the opacity of all images in the `_scene` attribute
        to 1, or fully opaque.
        '''
        for each_gw in self._scene.items():
            if isinstance(each_gw, QtWidgets.QGraphicsPixmapItem):
                each_gw.setOpacity(1)

    def decolor_all_images(self):
        '''Removes all coloring from images in the `_scene` attribute.
        '''
        for each_item in self._scene.items():
            if isinstance(each_item, QtWidgets.QGraphicsPixmapItem):
                each_item.setGraphicsEffect(None)

    def export_current_view(self, save_path=None):
        '''Exports the current content of the QGraphicsScene `_scene` attribute
        to a png file.

        :param save_path: Path to save the image to, defaults to None. If kept 
                          as None opens a QFileDialog to get a save file path.
        :type save_path: str or Path, optional
        '''
        if self._scene:
            if not save_path:
                save_path = QtWidgets.QFileDialog.getSaveFileName(
                    self, 'Save View')[0]
        if save_path:
            save_path = RunSerializer.path_suffix_checker(save_path, '.png')
            self.export_thread = QuickThread(SceneExporter.write_image,
                                             scene=self._scene, file_path=save_path)

            def finished_write():
                write_result = self.export_thread.result
                if isinstance(write_result, str):
                    message = 'View saved to {}'.format(write_result)
                else:
                    message = 'Write to {} failed with error {}'.format(
                        save_path, write_result
                    )
                make_message_box(parent=self, message=message).exec_()

            self.export_thread.finished.connect(finished_write)
            self.export_thread.start()
