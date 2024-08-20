#!/usr/bin/python3
import sys, traceback
import logging
import multiprocessing
import os
import sys
from pathlib import Path


if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
    sys.path.insert(0, application_path)

import PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QFile, QTextStream
from PyQt5.QtGui import QColor, QIcon, QPalette

import astor
from polo.windows.main_window import MainWindow
from polo import *



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

def preflight_checks():
    logger.debug('Detected OS: {}'.format(platform))
    logger.debug('Working directory: {}'.format(os.getcwd()))
    logger.debug('Polo directory: {}'.format(dirname))

    number_checks, passed = len(critical_paths), 0
    for path in critical_paths:
        if path.exists():
            logger.debug('Exists: {}'.format(path))
            passed += 1
        else:
            logger.critical('{} does not exist!'.format(path))
    
    if passed == number_checks:
        logger.debug('All preflight checks passed {} == {}'.format(
            passed, number_checks))


def main():

    # Run the app
    sys.excepthook = excepthook
    preflight_checks()

    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):  # magic call to make high-res scaling work
        PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    
    app = QtWidgets.QApplication(sys.argv)
    
    multiprocessing.freeze_support()  # prevent threads continuing after program closed
    logger.debug('App icon location: {}'.format(APP_ICON))
    app.setWindowIcon(QtGui.QIcon(str(APP_ICON)))
    main = MainWindow()
    main.show()
    logger.debug('Launched main window')
    sys.exit(app.exec_())


# called to run the app
if __name__ == "__main__":
	main()
