from PyQt5 import QtCore, QtGui, QtWidgets
from polo import IMAGE_CLASSIFICATIONS
from polo.crystallography.image import Image
from polo.crystallography.run import Run, HWIRun
from PyQt5.QtGui import QBitmap, QBrush, QColor, QIcon, QPainter, QPixmap
from PyQt5.QtWidgets import QGraphicsColorizeEffect, QGraphicsScene

from polo import ALLOWED_IMAGE_COUNTS, COLORS, IMAGE_CLASSIFICATIONS





class graphicsWell(QtWidgets.QGraphicsPixmapItem):

    def __init__(self, pixmap, parent=None, **kwargs):
        QtWidgets.QGraphicsPixmapItem.__init__(self, parent=parent)
        
        # self.setPixmap()
        self.setToolTip()
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
    
    def delete_pixmap(self):
        super(graphicsWell, self).setPixmap(QPixmap())
    
    def width(self):
        return self.pixmap().width()

    def height(self):
        return self.pixmap().height()

    def setToolTip(self):
        if self.image:
            super(graphicsWell, self).setToolTip(self.image.get_tool_tip())

    def setPixmap(self):
        super(graphicsWell, self).setPixmap(self.image.pixmap)

    def resetOpacity(self):
        super(graphicsWell, self).setOpacity(1)

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
