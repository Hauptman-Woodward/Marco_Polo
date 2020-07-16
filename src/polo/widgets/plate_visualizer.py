import copy
import math

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtGui import *
from polo import IMAGE_CLASSIFICATIONS, make_default_logger
from polo.crystallography.image import Image
from polo.crystallography.run import HWIRun, Run


class PlateVisualizer(QtWidgets.QGraphicsView):

    plate_view_requested = pyqtSignal(int)
    default_brush = QBrush(QColor(66, 155, 245))
    selected_brush = QBrush(QColor(245, 66, 66))
    default_pen = QPen(QColor(0, 0, 0), 1.0, Qt.SolidLine)
    default_pen.setWidth(2)
    plate_size = (32, 48)

    def __init__(self, parent=None):
        super(PlateVisualizer, self).__init__(parent)
        self.scene = QtWidgets.QGraphicsScene(self)
        # self.setInteractive(True)
        self.setScene(self.scene)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # self.scene.selectionChanged.connect(self._handle_block_selection)

    @staticmethod
    def block_dims(plate_x, plate_y, grid_x, grid_y):
        return plate_x / grid_x, plate_y / grid_y

    def _block_size(self, x, y):
        total_width, total_height = (
            self.frameGeometry().width(),
            self.frameGeometry().height()
        )
        return x / total_width, y / total_height

    def _handle_block_selection(self):
        if self.scene.selectedItems():
            block = self.scene.selectedItems().pop()
            self._highlight_block(block)
            self.plate_view_requested.emit(block.data(0))

    def set_selected_block(self, block_id):
        for block in self.scene.items():
            if block.data(0) == block_id:
                self._highlight_block(block)

    def _highlight_block(self, block):
        for item in self.scene.items():
            item.setBrush(self.default_brush)
        block.setBrush(self.selected_brush)

    def setup_view(self, grid_cords, plate_size=None):
        try:
            self.scene.clear()
            g_x, g_y = grid_cords
            if not plate_size:  # assume full size plate
                p_x, p_y = self.plate_size
            x, y = (p_x / g_x), (p_y / g_y)  # block layout
            try:
                x = int(x)
                y = int(y)
            except Exception:
                return
            # if cannot be based to int there is a problem
            w, h = self.frameGeometry().width(), self.frameGeometry().height()
            w = w / x
            h = h / y
            view_id, cur_x, cur_y = 0, 0, 0

            for i in range(x):
                for j in range(y):
                    view_id += 1
                    rect = self.scene.addRect(
                        cur_x, cur_y, w, h, self.default_pen,
                        self.default_brush)
                    rect.setData(0, view_id)
                    cur_x += w
                cur_y += h
                cur_x = 0
            self.fitInView(self.scene.itemsBoundingRect())
        except Exception:
            return
            # not worth throwing an error if something goes wrong but a crash
            # just don't render the visualizer
