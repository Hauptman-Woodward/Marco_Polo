import copy
import os

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBitmap, QBrush, QColor, QIcon, QPainter, QPixmap
from PyQt5.QtWidgets import QGraphicsColorizeEffect, QGraphicsScene

from polo import ALLOWED_IMAGE_COUNTS, COLORS, ICON_DICT, IMAGE_CLASSIFICATIONS
from polo.crystallography.run import HWIRun, Run
from polo.designer.UI_table_inspector import Ui_Form
from polo.widgets.slideshow_viewer import PhotoViewer
from polo.utils.math_utils import *
from polo import make_default_logger

logger = make_default_logger(__name__)

class TableInspector(QtWidgets.QWidget):

    def __init__(self, parent=None, run=None):
        self.run = run
        super(TableInspector, self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.image_type_checks = [
            self.ui.checkBox_7, self.ui.checkBox_8,
            self.ui.checkBox_9, self.ui.checkBox_10]

        self.assign_checkboxes_to_class()
        self.ui.pushButton.clicked.connect(self.update_table_view)

    def assign_checkboxes_to_class(self):
        for i, checkBox in enumerate(self.image_type_checks):
            checkBox.setText(IMAGE_CLASSIFICATIONS[i])

    @property
    def run(self):
        return self.__run

    @property
    def selected_headers(self):
        checked_col_names = set([])
        for index in range(self.ui.listWidget.count()):
            if self.ui.listWidget.item(index).checkState() == Qt.Checked:
                checked_col_names.add(self.ui.listWidget.item(index).text())
        return checked_col_names

    @property
    def selected_classifications(self):
        image_types = set([])
        for checkBox in self.image_type_checks:
            if checkBox.isChecked():
                image_types.add(checkBox.text())
        return image_types

    @run.setter
    def run(self, new_run):
        self.__run = new_run
        if self.run:
            self.ui.tableViewer.run = new_run
            self.set_column_options()

    def set_column_options(self):
        if self.run:
            for fieldname in self.ui.tableViewer.fieldnames:
                item = QtWidgets.QListWidgetItem(self.ui.listWidget)
                item.setText(fieldname)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked)
                self.ui.listWidget.addItem(item)

    def update_table_view(self):
        if self.run:
            self.ui.tableViewer.selected_headers = self.selected_headers
            self.ui.tableViewer.populate_table(
                self.selected_classifications,
                self.ui.checkBox_12.isChecked(),
                self.ui.checkBox_11.isChecked())

    # parse the filters and the checked headers
