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
    '''The PlateVisualizer is a small widget to assist users understand
    what part of the screening plate they are currently viewing. It renders
    a grid of rectangles (blocks) that each represent one view (page) in the
    `PlateInspector` widget. The page that is currently being viewed is 
    highlighted to show the user what part of the plate they are looking at. 

    :param parent: Parent widget, defaults to None
    :type parent: QWidget, optional
    '''

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
        '''Helper method to calculate the size of plate section
        blocks

        :param plate_x: Number of wells plate has on its x axis
        :type plate_x: int
        :param plate_y: Number of wells plate has on it s y axis
        :type plate_y: int
        :param grid_x: Number of wells in the subgrid on its x axis
        :type grid_x: int
        :param grid_y: Number of wells in the subgrid on its y axis
        :type grid_y: int
        :return: tuple, first item being length of x axis in
                 blocks and second being length of y axis in blocks
        :rtype: tuple
        ''' 
        return plate_x / grid_x, plate_y / grid_y

    def _block_size(self, x, y):
        '''Private method to calculate the size of individual blocks
        to render in the QGraphicsView. 

        :param x: Length of x-axis in blocks
        :type x: int
        :param y: Length of y-axis in blocks
        :type y: int
        :return: tuple, length of block x-axis in pixels,
                 length of block y-axis in pixels
        :rtype: tuple
        ''' 
        total_width, total_height = (
            self.frameGeometry().width(),
            self.frameGeometry().height()
        )
        return x / total_width, y / total_height

    def _handle_block_selection(self):
        '''Private helper method to handle when a user selects a block.
        In theory should open the view that the selected block corresponds
        to but currently having some issues with this causing segmentation
        faults so it is disabled for now.
        '''
        if self.scene.selectedItems():
            block = self.scene.selectedItems().pop()
            self._highlight_block(block)
            self.plate_view_requested.emit(block.data(0))

    def set_selected_block(self, block_id):
        '''Sets the currently selected block based on its ID.

        :param block_id: Block ID
        :type block_id: int
        '''
        for block in self.scene.items():
            if block.data(0) == block_id:
                self._highlight_block(block)

    def _highlight_block(self, block):
        '''Private method that highlights a block in the
        QGraphicsScene.

        :param block: Block to highlight
        :type block: QGraphicsRectItem
        '''
        for item in self.scene.items():
            item.setBrush(self.default_brush)
        block.setBrush(self.selected_brush)

    def setup_view(self, grid_cords, plate_size=None):
        '''set up the intail view based on the current plate
        size (normally 32 * 48 wells for 1536 well plate) and
        the subgrid size in wells.

        :param grid_cords: Subgrid size tuple (x, y) in wells
        :type grid_cords: tuple
        :param plate_size: Size of entire plate (x, y) in wells, defaults to None.
                            If None used the default 1536 well plate size of
                            32 * 48.
        :type plate_size: tuple, optional
        '''
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
