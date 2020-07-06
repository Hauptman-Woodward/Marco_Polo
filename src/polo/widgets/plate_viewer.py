import math

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBitmap, QBrush, QColor, QIcon, QPainter, QPixmap, QPixmapCache
from PyQt5.QtWidgets import QGraphicsColorizeEffect, QGraphicsScene

from polo import ALLOWED_IMAGE_COUNTS, COLORS, IMAGE_CLASSIFICATIONS
from polo.crystallography.run import HWIRun, Run
from polo.windows.image_pop_dialog import ImagePopDialog
from polo.utils.math_utils import *
from polo.widgets.slideshow_viewer import PhotoViewer
from polo.widgets.graphics_well import graphicsWell


    

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
        self.__scene_map = {}
        self.__view_cache = {}
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
            self.__scene.clear()
            QPixmapCache.clear()

    @current_page.setter
    def current_page(self, new_page_number):
        if new_page_number > self.total_pages:
            new_page_number = 1
        elif new_page_number < 1:
            new_page_number = self.total_pages
        self.__current_page = new_page_number

    def get_visible_wells(self, page=None):
# return just the indices of the wells and then create the graphics wells
# and delete the scene afterwards 
        current_images = []
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
    
    def tile_graphics_wells(self, overwrite_cache=False, next_date=False,
                            prev_date=False, alt_spec=False):
        QtWidgets.QApplication.setOverrideCursor(Qt.WaitCursor)

        [item.data(0).recursive_delete_pixmap_data() for item in self.scene.items()]


        visible_wells = self.get_visible_wells()
        _, stride = self.subgrid_dict[self.images_per_page]
        cur_x_pos, cur_y_pos = 0, 0  # position to place image in pixels
        row_height = 0  # height of tallest image in a given row of images


        images = [self.run.images[i] for i in self.get_visible_wells()]
        _, stride = self.subgrid_dict[self.images_per_page]

        self.__scene.clear()

        for i, image in enumerate(images):
            if i % stride == 0 and i != 0:
                cur_y_pos += row_height
                row_height, cur_x_pos, = 0, 0  # reset row height for next row
            
            if image.isNull():
                image.setPixmap()
            
            item = self.__scene.addPixmap(image)
            item.setPos(cur_x_pos, cur_y_pos)
            item.setData(0, image)
            self.set_prerender_info(item, image)
            #self.apply_scene_settings(item)  # TODO apply the settings here
            if image.height() > row_height:
                row_height = image.height()
            cur_x_pos += image.width() 
        
        self.__scene.selectionChanged.connect(self.pop_out_selected_well)
        self.setScene(self.__scene)
        self.fitInView(self.__scene, self.preserve_aspect)
        QtWidgets.QApplication.restoreOverrideCursor()
            
    
    # modifies the scene item before it is displayed


    def set_prerender_info(self, item, image):
        item.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        item.setToolTip(image.get_tool_tip())  # pixmap is Image
        
        return item
    
    def set_scene_opacity_from_filters(self, image_types, human=False, marco=False, filtered_opacity=0.2):
        for item in self.__scene.items():
            image = item.data(0)
            print(image_types, image.machine_class)
            if image.standard_filter(image_types, human, marco):
                item.setOpacity(1)
                print('set opacity to 1')
            else:
                # did not meet the filtered criteria
                item.setOpacity(filtered_opacity)
                print('set opacity to filtered opacity', filtered_opacity)
    
    def set_scene_colors_from_filters(self, color_mapping, strength=0.5, human=False):
        for item in self.__scene.items():
            image, color = item.data(0), None
            if human and image.human_class in color_mapping:
                color = color_mapping[image.human_class]
            elif image.machine_class in color_mapping:
                color = color_mapping[image.machine_class]
            if color:
                effect = QGraphicsColorizeEffect()
                effect.setColor(color)
                effect.setStrength(strength)
            item.setGraphicsEffect(effect)
            

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
            image = selection[0].data(0)
            pop_out = ImagePopDialog(image)
            pop_out.setWindowModality(Qt.ApplicationModal)
            pop_out.show()
            self.__scene.clearSelection()
            

    # def demphasize_filtered_images(self, image_types, human, marco):
    #     for each_gw in self.__scene.items():
    #         if each_gw:
    #             each_gw.setOpacity(0.25, image_types=image_types,
    #                                human=human, marco=marco)

    # def color_images(self, color_mapping, strength=0.5, human=False):
    #     for each_gw in self.__scene.items():
    #         if each_gw:
    #             each_gw.set_color(color_mapping, strength=strength,
    #                               by_human_class=human)

    def emphasize_all_images(self):
        for each_gw in self.__scene.items():
            if each_gw:
                each_gw.setOpacity(1)

    def decolor_all_images(self):
        for each_gw in self.__scene.items():
            if each_gw:
                each_gw.setGraphicsEffect(None)
    
    def export_current_view(self):
        if self.__scene:
            export_path = QtWidgets.QFileDialog.getSaveFile()
            # something like that to get save file
            if export_path:
                image = QImage(self.__scene.rect(), Format_ARGB32_Premultiplied)
                painter = QPainter(image)
                self.__scene.render(painter, image.rect(), self.__scene.rect())
                painter.end()
                image.save(export_path)
        # TODO Needs testing no idea if this will work
