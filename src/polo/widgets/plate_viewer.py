import math

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBitmap, QBrush, QColor, QIcon, QPainter, QPixmap
from PyQt5.QtWidgets import QGraphicsColorizeEffect, QGraphicsScene

from polo import ALLOWED_IMAGE_COUNTS, COLORS, IMAGE_CLASSIFICATIONS
from polo.crystallography.run import HWIRun, Run
from polo.widgets.slideshow_viewer import PhotoViewer
from polo.windows.image_pop_dialog import ImagePopDialog
from polo.utils.math_utils import *


class graphicsWell(QtWidgets.QGraphicsPixmapItem):
    

    def __init__(self, parent=None, image=None):
        QtWidgets.QGraphicsPixmapItem.__init__(self, parent=parent)
        self.image = image  # image object
        # self.setPixmap()
        self.setToolTip()
        self.last_pixmap = None
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)

    def width(self):
        return self.pixmap().width()

    def height(self):
        return self.pixmap().height()

    def setToolTip(self):
        if self.image:
            return super(graphicsWell, self).setToolTip(self.image.get_tool_tip())

    def setPixmap(self):
            return super(graphicsWell, self).setPixmap(self.image.pixmap)


    def resetOpacity(self):
        return super(graphicsWell, self).setOpacity(1)

    def setOpacity(self, filtered_opacity, image_types, human=False, marco=False):
        set_visible = False
        if self.image:
            if image_types:  # otherwise no images specified
                if human and self.image.human_class in image_types:
                    set_visible = True
                elif marco and self.image.machine_class in image_types:
                    set_visible = True
            else:
                if human and self.image.human_class:
                    set_visible = True
                elif marco and self.image.machine_class:
                    set_visible = True
        if set_visible:
            filtered_opacity = 1  # image has met filtering requirements
        super(graphicsWell, self).setOpacity(filtered_opacity)

    def set_color(self, color_mapping, strength=0.5, by_human_class=False):
        effect = None
        color = None
        if self.image:
            if color_mapping:
                if by_human_class and self.image.human_class:
                    color = color_mapping[self.image.human_class]
                elif not by_human_class and self.image.machine_class:
                    color = color_mapping[self.image.machine_class]
                if color:
                    effect = QGraphicsColorizeEffect()
                    effect.setColor(color)
                    effect.setStrength(strength)
            self.setGraphicsEffect(effect)

    def get_alt_image(self, next_date=False,
                      previous_date=False, alt_spec=False):
        if self.image:
            if next_date and self.image.next_image:
                self.image = self.image.next_image
            elif previous_date and self.image.previous_image:
                self.image = self.image.previous_image
            elif alt_spec and self.image.alt_image:
                self.image = self.image.alt_image
            self.setPixmap()
    
    # def pre_load_alt_images(self):
    #     image_keywords = ['alt_image', 'next_image', 'previous_image']
    #     image_dict = 
    #     for keyword in image_keywords:
            



# class PlateCache():

#     def __init__(self, plateViewer):
#         self.plateViewer = plateViewer
#         self.cache = {}

#     @property
#     def run(self):
#         if self.plateViewer:
#             return self.plateViewer.run

#     @property
#     def current_page(self):
#         if self.plateViewer:
#             return self.plateViewer.current_page

#     @property
#     def images_per_page(self):
#         if self.plateViewer:
#             return self.plateViewer.images_per_page

#     @property
#     def scene(self):
#         if self.plateViewer:
#             return self.plateViewer.scene

#     def add_scene(self, num_images, page_num):
#         pass

#     def cache_current_scene(self):

#         run_name = self.run.run_name
#         self.add_to_cache(self.run, self.current_page,
#                           self.images_per_page, self.scene)

#     def erase_current_scene(self):
#         try:
#             self.cache[self.run.run_name][self.current_page][self.images_per_page] = None
#         except KeyError as e:
#             return False

#     def add_to_cache(self, run=None, current_page=None, images_per_page=None, scene=None):
#         try:
#             self.cache[run.run_name][current_page][images_per_page] = scene
#         except KeyError:
#             if run:
#                 if run.run_name not in self.cache:
#                     self.cache[run.run_name] = {}
#                 if current_page:
#                     if current_page not in self.cache[run.run_name]:
#                         self.cache[run.run_name][current_page] = {}
#                     if images_per_page:
#                         if images_per_page not in self.cache[run.run_name][current_page]:
#                             self.cache[run.run_name][current_page][images_per_page] = scene

    # def check_for_current_scene(self):
    #     try:
    #         return self.cache[self.run.run_name][self.current_page][self.images_per_page]
    #     except KeyError as e:
    #         return False







# since going from set plate sizes in the view could have it run in the
# background caching as many views as it can while the number of images in
# the view are still the same
import time
class plateViewer(QtWidgets.QGraphicsView):

    subgrid_dict = {16: (4, 4), 64: (8, 8), 96: (8, 12), 1536: (32, 48)}

    def __init__(self, parent, run=None, images_per_page=24):
        super(plateViewer, self).__init__(parent)
        self.run = run
        self.preserve_aspect = False  # how to fit images in scene
        self.__images_per_page = images_per_page
        self.__graphics_wells = None
        self.__current_page = 1
        self.__scene = QtWidgets.QGraphicsScene(self)
        # self.__cache = PlateCache(self)
        self.setScene(self.__scene)
        self.__scene.selectionChanged.connect(self.pop_out_selected_well)
        self.__zoom = 0
        self.setInteractive(True)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(self.AnchorUnderMouse)

    @staticmethod
    def well_index_to_subgrid(i, c_r, c_c, p_r, p_c):
        '''Find the linear index of the subgrid that a particular index belongs to
        within a larger grid. For example, ou are given a list of length 16. The list is reshaped into a 4 x 4
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
        chunk_rows = int(p_r / c_r)
        chunk_cols = int((p_c / c_c))
        c_x, c_y = math.floor(r / c_r), math.floor(c / c_c)
        return c_x * chunk_cols + c_y

    @property
    def images_per_page(self):
        return self.__images_per_page

    @images_per_page.setter
    def images_per_page(self, new_num):
        if new_num != self.__images_per_page:
            self.__images_per_page = new_num
            self.__current_page = 1

    @property
    def scene(self):
        return self.__scene

    @property
    def total_pages(self):
        if self.run and self.images_per_page:
            return math.ceil(len(self.run) / self.images_per_page)
        else:
            return 0

    @property
    def view_dims(self):
        return self.width(), self.height()

    @property
    def aspect_ratio(self):
        if self.run and self.images_per_page:
            view_w, view_h = self.view_dims
            return best_aspect_ratio(view_w, view_h, self.images_per_page)
        else:
            return 0, 0

    @property
    def current_page(self):
        return self.__current_page

    @property
    def run(self):
        return self.__run

    @run.setter
    def run(self, new_run):
        self.__run = new_run
        if isinstance(new_run, Run) or isinstance(new_run, HWIRun):
            self.__graphics_wells = [graphicsWell(
                image=im) for im in self.__run.images]

    @current_page.setter
    def current_page(self, new_page_number):
        if new_page_number > self.total_pages:
            new_page_number = 1
        elif new_page_number < 1:
            new_page_number = self.total_pages
        self.__current_page = new_page_number

    def get_visible_wells(self):
        current_images = []
        if self.__graphics_wells:
            # need to know the plate size starting with want page we are on
            r, c = self.subgrid_dict[self.images_per_page]
            # dims of grid to show
            p_r, p_c = self.subgrid_dict[len(self.__graphics_wells)]
            # dims of entire plate
            for i in range(0, len(self.__graphics_wells)):  # size of plate
                plate_index = plateViewer.well_index_to_subgrid(i, r, c, p_r, p_c)
                plate_index += 1
            
                if plate_index == self.current_page:
                    self.__graphics_wells[i].setPixmap()
                    current_images.append(self.__graphics_wells[i])
            return current_images

    def tile_graphics_wells(self, overwrite_cache=False, next_date=False,
                            prev_date=False, alt_spec=False):
        QtWidgets.QApplication.setOverrideCursor(Qt.WaitCursor)
        self.__scene = QtWidgets.QGraphicsScene(self)  # new scene\
        s = time.time()
        self.visible_wells = self.get_visible_wells()
        _, stride = self.subgrid_dict[self.images_per_page]
        cur_x_pos, cur_y_pos = 0, 0  # position to place image in pixels
        row_height = 0  # height of tallest image in a given row of images

        if next_date or prev_date or alt_spec:
            [well.get_alt_image(next_date, prev_date, alt_spec) for well in self.visible_wells]

        if self.visible_wells:  # make sure wells is not empty (no run loaded)
            for i in range(len(self.visible_wells)):
                if i % stride == 0 and i != 0:  # time for a ew row of images
                    cur_y_pos += row_height
                    row_height, cur_x_pos, = 0, 0  # reset row height for next row
                    # return x position back to origin
                self.__scene.addItem(self.visible_wells[i])
                self.visible_wells[i].setPos(cur_x_pos, cur_y_pos)
                cur_x_pos += self.visible_wells[i].width()
                if self.visible_wells[i].height() > row_height:
                    row_height = self.visible_wells[i].height()
            self.__scene.selectionChanged.connect(self.pop_out_selected_well)
            self.setScene(self.__scene)   # actually set the scene
            # cram in into the current view
            self.fitInView(self.__scene, self.preserve_aspect)
        QtWidgets.QApplication.restoreOverrideCursor()

    def fitInView(self, scene, preserve_aspect=False):
        if preserve_aspect:
            super(plateViewer, self).fitInView(scene.itemsBoundingRect(),
                                               Qt.KeepAspectRatio)
        else:
            super(plateViewer, self).fitInView(scene.itemsBoundingRect())

    def wheelEvent(self, event):
        if event:
            if event.angleDelta().y() > 0:
                factor = 1.25
                self.__zoom += 1
            else:
                factor = 0.8
                self.__zoom -= 1
            if self.__zoom > 0:
                self.scale(factor, factor)
            elif self.__zoom == 0:
                self.fitInView(self.__scene, self.preserve_aspect)
            else:
                self.__zoom = 0

    def pop_out_selected_well(self):
        selection = self.__scene.selectedItems()
        if selection:
            pop_out = ImagePopDialog(selection[0].image)
            pop_out.setWindowModality(Qt.ApplicationModal)
            pop_out.show()
            self.__scene.clearSelection()
            

    def demphasize_filtered_images(self, image_types, human, marco):
        for each_gw in self.__graphics_wells:
            if each_gw:
                each_gw.setOpacity(0.25, image_types=image_types,
                                   human=human, marco=marco)

    def color_images(self, color_mapping, strength=0.5, human=False):
        for each_gw in self.__graphics_wells:
            if each_gw:
                each_gw.set_color(color_mapping, strength=strength,
                                  by_human_class=human)

    def emphasize_all_images(self):
        for each_gw in self.__graphics_wells:
            if each_gw:
                each_gw.resetOpacity()

    def decolor_all_images(self):
        for each_gw in self.__graphics_wells:
            if each_gw:
                each_gw.set_color(None)
