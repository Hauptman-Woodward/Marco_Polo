import math

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBitmap, QBrush, QColor, QIcon, QPainter, QPixmap
from PyQt5.QtWidgets import QGraphicsColorizeEffect, QGraphicsScene

from polo import ALLOWED_IMAGE_COUNTS, COLORS, IMAGE_CLASSIFICATIONS
from polo.crystallography.run import HWIRun, Run
from polo.ui.widgets.slideshow_viewer import PhotoViewer
from polo.ui.windows.image_pop_dialog import ImagePopDialog
from polo.utils.math_utils import *


class graphicsWell(QtWidgets.QGraphicsPixmapItem):

    def __init__(self, parent=None, image=None):
        QtWidgets.QGraphicsPixmapItem.__init__(self, parent=parent)
        self.image = image  # image object
        # self.setPixmap()
        self.setToolTip()
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)

    def width(self):
        return self.pixmap().width()

    def height(self):
        return self.pixmap().height()

    def setToolTip(self):
        if self.image:
            return super(graphicsWell, self).setToolTip(self.image.get_tool_tip())

    def setPixmap(self, pixmap=None):
        if pixmap:
            return super(graphicsWell, self).setPixmap(pixmap)
        elif self.image:
            return super(graphicsWell, self).setPixmap(self.image.get_pixel_map())

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


class plateViewer(QtWidgets.QGraphicsView):

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
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

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
    def visible_wells(self):
        if self.run and self.images_per_page and self.current_page:
            s = self.images_per_page * self.current_page - self.images_per_page
            e = s + self.images_per_page
            for i in range(s, e):
                self.__graphics_wells[i].setPixmap()
                yield self.__graphics_wells[i]

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

    def fitInView(self, scene, preserve_aspect=False):
        if preserve_aspect:
            super(plateViewer, self).fitInView(scene.itemsBoundingRect(),
                                               Qt.KeepAspectRatio)
        else:
            super(plateViewer, self).fitInView(scene.itemsBoundingRect())

    def tile_graphics_wells(self, overwrite_cache=False, next_date=False, prev_date=False, alt_spec=False):
        # check if scene has already been cached

        # if overwrite_cache and self.__cache.check_for_current_scene():
        # want to overwrite the cache and the cache exists
        #   self.__cache.erase_current_scene()
        #   print('OVERWROTE THE CACHE')
        QtWidgets.QApplication.setOverrideCursor(Qt.WaitCursor)
        self.__scene = QtWidgets.QGraphicsScene(self)
        visible_wells = list(self.visible_wells)
        cur_x, cur_y = 0, 0  # current pixel positions to place image
        w, h = self.aspect_ratio
        for i in range(0, w):
            max_h = 0
            for j in range(0, h):
                cur_graphics_well = visible_wells.pop(0)
                cur_graphics_well.get_alt_image(next_date, prev_date, alt_spec)
                self.__scene.addItem(cur_graphics_well)
                cur_graphics_well.setPos(cur_x, cur_y)
                cur_graphics_well.setSelected(False)
                cgw_w, cgw_h = (
                    cur_graphics_well.width(),
                    cur_graphics_well.height()
                )
                if cgw_h > max_h:
                    max_h = cgw_h
                cur_x += cgw_w
            cur_y += max_h
            cur_x = 0
        self.__scene.selectionChanged.connect(self.pop_out_selected_well)
        self.setScene(self.__scene)
        self.fitInView(self.__scene, self.preserve_aspect)
        QtWidgets.QApplication.restoreOverrideCursor()

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
