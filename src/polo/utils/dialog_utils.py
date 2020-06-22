from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QPoint, Qt
from polo import make_default_logger

logger = make_default_logger(__name__)

def make_message_box(message, parent=None, icon=QtWidgets.QMessageBox.Information,
                        buttons=QtWidgets.QMessageBox.Ok,
                        connected_function=None):
    msg = QtWidgets.QMessageBox(parent)
    msg.setIcon(icon)
    msg.setText(message)
    msg.setStandardButtons(buttons)
    if connected_function:
        msg.buttonClicked.connect(connected_function)

    logger.info('Made message box with message "{}"'.format(message))
    return msg