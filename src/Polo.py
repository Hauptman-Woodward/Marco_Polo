#!/usr/bin/python3
import sys, traceback
import logging
import multiprocessing
import os
import sys
from pathlib import Path

import PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QFile, QTextStream
from PyQt5.QtGui import QColor, QIcon, QPalette

import astor
from polo.crystallography.run import Run, HWIRun
from polo.ui.windows.main_window import MainWindow
from polo.utils.io_utils import *
from polo import LOG_PATH, APP_ICON, make_default_logger

__version__ = '0.0.1'
# set up logging
logger = make_default_logger(__name__)

def excepthook(exec_type, exec_value, exec_tb):
    trace =  traceback.format_exception(etype=exec_type, value=exec_value, tb=exec_tb)
    trace = ' '.join([t.strip() for t in trace])


    message = '{}\nError Message: {}\nValue: {}\n Error Type: {}\n'.format(
        'Polo encountered an unexpected error.',
        trace, exec_value, exec_type
    )
    logger.critical(message)
    m = QtWidgets.QMessageBox()
    m.setIcon(QtWidgets.QMessageBox.Critical)
    m.setText(message)
    m.exec_()
    QtWidgets.QApplication.quit()

def main():

    # Run the app
    sys.excepthook = excepthook
    logger.info('Started Polo version {}'.format(__version__))
    multiprocessing.freeze_support()
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(str(APP_ICON)))
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


# called to run the app
if __name__ == "__main__":
	main()
