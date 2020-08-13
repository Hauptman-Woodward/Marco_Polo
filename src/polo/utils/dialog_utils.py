from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QPoint, Qt
from polo import make_default_logger

logger = make_default_logger(__name__)

def make_message_box(message,
                    parent=None,
                    icon=QtWidgets.QMessageBox.Information,
                    buttons=QtWidgets.QMessageBox.Ok,
                    connected_function=None):
    '''General helper function to create popup message box dialogs to convey
    situational information to the user.

    :param message: The message to display to the user.
    :type message: str
    :param parent: Parent dialog, defaults to None
    :type parent: QDialog, optional
    :param icon: QMessageBox icon to display along with the message,
                 defaults to QtWidgets.QMessageBox.Information
    :type icon: int, optional
    :param buttons: Buttons to include in the message box,
                    defaults to QtWidgets.QMessageBox.Ok
    :type buttons: set, optional
    :param connected_function: Function to connect to
                               buttonClicked event, defaults to None
    :type connected_function: func, optional
    :return: The message box.
    :rtype: QMessageBox
    '''
    msg = QtWidgets.QMessageBox(parent)
    msg.setIcon(icon)
    msg.setText(message)
    msg.setStandardButtons(buttons)
    if connected_function:
        msg.buttonClicked.connect(connected_function)

    logger.debug('Made message box with message "{}"'.format(message))
    return msg