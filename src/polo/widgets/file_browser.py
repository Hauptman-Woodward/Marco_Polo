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
        '''Extension of the QTreeWidget specifically designed as the file
        interface for the FTP Dialog. Allows the user to browse files stored
        on an FTP server and select files for download.

        :param parent: Parent Widget, defaults to None
        :type parent: QWidget, optional
        '''
        super(fileBrowser, self).__init__(parent)

    def grow_tree_using_mlsd(self, ftp, home_dir, set_checkable=True):
        '''Rescursively add child nodes to the fileBrowser tree by traversing
        a user's home directory of an ftp server using mlsd formating.  

        :param ftp: FTP object with valid connection
        :type ftp: FTP
        :param home_dir: Path to the user's home directory
        :type home_dir: str or Path
        :param set_checkable: Set files and dirs to checkable, defaults to True
        :type set_checkable: bool, optional
        '''
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

    # def grow_tree_local(self, home_dir):

    #     def recursive_add(cwd, tree):
    #         pass
    #     pass

    def get_checked_files(self, home_dir):
        '''Traverse the file tree and return the full paths to files that have
        been selected by the user. 

        :param home_dir: User's home directory. This path is the parent of all
                         returned files.
        :type home_dir: str or Path
        :return: List of checked Paths
        :rtype: list
        '''
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

