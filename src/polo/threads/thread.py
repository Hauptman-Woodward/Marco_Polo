from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import time

# from polo.utils.io_utils import save_run_as_json
import os
from polo import BLANK_IMAGE

from PyQt5.QtGui import QBrush, QColor, QIcon, QPixmap
from polo.utils.math_utils import get_cell_image_dims, best_aspect_ratio
from PyQt5 import QtWidgets
# from polo.utils.io_utils import load_run_object
# from polo.ui.widgets.plate_viewer import graphicsWell


class thread(QThread):
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)
    
    def __del__(self):
        self.existing=True
        self.wait()
    
    def run(self):
        return NotImplementedError

class QuickThread(thread):

    def __init__(self, job_func, parent=None, **kwargs):
        super().__init__(parent=parent)
        self.job_func = job_func
        self.func_args = dict(kwargs)
        self.result = None

    def __del__(self):
        self.exiting = True
        self.wait()

    def run(self):
        self.result = self.job_func(**self.func_args)

class ClassificationThread(thread):
    change_value = pyqtSignal(int)
    estimated_time = pyqtSignal(float, int)

    def __init__(self, run_object):
        thread.__init__(self)
        self.classification_run = run_object

    def run(self):
        for i, image in enumerate(self.classification_run.images):
            if image and image.path != str(BLANK_IMAGE):
                s = time.time()
                image.classify_image()
                e = time.time()
            self.change_value.emit(i+1)
            if i % 5 == 0:
                self.estimated_time.emit(e-s, len(self.classification_run.images)-(i+1))

            # emit signal so know to move progress par forward

class FTPDownloadThread(thread):
    file_downloaded = pyqtSignal(int)
    
    def __init__(self, ftp_connection, file_paths, save_dir_path):
        thread.__init__(self)
        self.ftp = ftp_connection
        self.file_paths = file_paths
        self.save_dir_path = save_dir_path
    
    def run(self):
        for i, remote_file_path in enumerate(self.file_paths):
            print('downloading', remote_file_path)
            if self.ftp:
                local_file_path = os.path.join(
                    str(self.save_dir_path),
                    os.path.basename(str(remote_file_path)) 
                )
                with open(local_file_path, 'wb') as local_file:
                    cmd = 'RETR {}'.format(remote_file_path)
                    status = self.ftp.retrbinary(cmd, local_file.write)
            print('downloaded file ', remote_file_path)
            self.file_downloaded.emit(i)
            




class GraphThread(thread):

    def __init__(self, run_object):
        thread.__init__(self)
        self.classification_run = run_object
    # probably want this for making plots


class SaveThread(thread):

    def __init__(self, run_to_save, output_path):
        thread.__init__(self)
        self.run_to_save = run_to_save
        self.output_path = output_path

    def run(self):
        save_run_as_json(self.run_to_save, self.output_path)


class PlateThread(thread):

    def __init__(self, run, image_types, marco, human, start_index, end_index, graphics_view_dims):
        thread.__init__(self)
        self.run = run
        self.image_types = image_types
        self.marco = marco
        self.human = human
        self.start = start_index
        self.end = end_index
        self.empty_map = QPixmap('/home/ethan/Pictures/polo.png')
        self.graphics_view_dims = graphics_view_dims
        self.scene = None

    def run(self):
        images = self.retrieve_images()
        self.scene = tile_images_in_scene(images)
        return scene

    def retrieve_images(self):
        indices = set(self.run.image_filter_query(
            self.image_types, self.human, self.marco))
        images = []
        for i in range(self.start, self.end):
            if i in indices:
                images.append(self.current_run[i])
            else:
                images.append(None)
        return images

    def tile_images_in_scene(self, images):
        scene = QtWidgets.QGraphicsScene()
        w, h = self.graphics_view_dims
        a_w, a_h = best_aspect_ratio(w, h, len(images))
        for i in range(1, a_h+1):
            for j in range(1, a_w+1):
                image = images.pop(0)
                if image:
                    pixel_map = image.get_pixel_map()
                else:
                    pixel_map = self.empty_map
                    x, y = (
                        pixel_map.size().width() * j,
                        pixel_map.size().height() * i
                    )
                    self.place_image_in_scene(
                        scene, image, pixel_map, x, y
                    )
        return scene  # scene now inludes all images

    def place_image_in_scene(self, scene, image, pixel_map, x, y):
        item = QtWidgets.QGraphicsItem(pixel_map)
        item.setFlat(QtWidgets.QGraphicsItem.ItemIsSelectable)
        if image:
            item.setData(0, image)  # store image object in data
            item.setToolTip(image.get_tool_tip())
        self.scene.addItem(item)
        item.setPos(x, y)
