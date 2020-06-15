from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QBrush, QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QGridLayout
import os
from polo import ICON_DICT
import ftplib
from pathlib import PurePosixPath
from PyQt5.QtWidgets import QApplication



class fileBrowser(QtWidgets.QTreeWidget):

    DATA_INDEX = 5
    FILE_ICON = str(ICON_DICT['file'])
    DIR_ICON = str(ICON_DICT['dir'])

    def __init__(self, parent=None):
        super(fileBrowser, self).__init__(parent)

    def grow_tree_using_mlsd(self, ftp, home_dir, set_checkable=True):
        home_dir = PurePosixPath(str(home_dir))

        def recursive_add(cwd, tree):
            mlsd = [i for i in ftp.mlsd(cwd) if i[0][-1] != '.']
            for item, d in mlsd:
                parent_item = QtWidgets.QTreeWidgetItem(tree)
                parent_item.setText(0, item)
                if d['type'] == 'dir':
                    recursive_add(cwd.joinpath(item), parent_item)
                    parent_item.setIcon(0, QIcon(self.DIR_ICON))
                    if set_checkable:
                        parent_item.setFlags(
                            parent_item.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
                else:  # is a file
                    parent_item.setIcon(0, QIcon(self.FILE_ICON))
                    if set_checkable:
                        parent_item.setFlags(
                            parent_item.flags() | Qt.ItemIsUserCheckable)
                        parent_item.setCheckState(0, Qt.Unchecked)
                    parent_item.setData(0, self.DATA_INDEX, cwd.joinpath(item))

        recursive_add(home_dir, self)

    def grow_tree_local(self, home_dir):

        def recursive_add(cwd, tree):
            pass
        pass

    def get_checked_files(self, home_dir):
        checked_items = []
        home_dir = PurePosixPath(str(home_dir))
        def recurse(parent_item, path):
            for i in range(parent_item.childCount()):
                child = parent_item.child(i)
                grand_children = child.childCount()
                if grand_children > 0:
                    path = path.joinpath(child.text(0))
                    recurse(child, path)
                else:
                    if child.checkState(0) == Qt.Checked:
                        checked_items.append(PurePosixPath(child.data(0, self.DATA_INDEX)))
        recurse(self.invisibleRootItem(), home_dir)
        return checked_items

