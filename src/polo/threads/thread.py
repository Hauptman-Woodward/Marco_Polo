import os
import time

from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtGui import QBrush, QColor, QIcon, QPixmap
from PyQt5.QtWidgets import *

from polo import BLANK_IMAGE
from polo.utils.math_utils import best_aspect_ratio, get_cell_image_dims


class thread(QThread):
    '''Very basic wrapper class around :class:`QThread` class. Should be
    inherited by a more specific class and then the `run` method
    can be overwritten to provide functionality. Whatever code is in the
    :meth:`~polo.threads.thread.thread.run` method will be executed when
    :meth:`~polo.threads.thread.thread.start` is called. The
    :meth:`~polo.threads.thread.thread.run` method should not be called
    explicitly.

    :param parent: parent widget, defaults to None
    :type parent: QWidget, optional
    '''

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def __del__(self):
        self.existing = True
        self.wait()

    def run(self):
        return NotImplementedError


class QuickThread(thread):

    '''QuickThreads are very similar
    to thread objects except instead of you writing code that would be
    executed by the `run` method directly, the function that the `QuickThread`
    will execute is passed as an argument to the `__init__`. Any arguments
    that the passed function requires are passed as key word arguments. Once
    the thread finished any values returned by the passed function are stored
    in the `QuickThread`'s :attr:`polo.threads.thread.QuickThread.results`
    attribute.

    .. highlight:: python
    .. code-block:: python

        my_func = lambda x, y: x + y
        x, y = 40, 60
        my_thread = QuickThread(job_func=my_func, x=x, y=y)
        # set up the thread with my_func and the args we want to pass
        my_thread.start()
        # my_thread.result will = 100 (x + y)


    :param job_func: Function to execute on the thread
    :type job_func: func
    '''

    def __init__(self, job_func, parent=None, **kwargs):
        super().__init__(parent=parent)
        self.job_func = job_func
        self.func_args = dict(kwargs)
        self.result = None

    def __del__(self):
        self.exiting = True
        self.wait()

    def run(self):
        self.result = self.job_func(**self.func_args)


class ClassificationThread(thread):
    '''Thread that is specifically for classifying images using the MARCO
    model. This is a very CPU intensive process so it cannot be run on
    the GUI thread. 

    :param run_object: Run who's images are to be classified
    :type run_object: Run or HWIRun
    '''
    change_value = pyqtSignal(int)
    estimated_time = pyqtSignal(float, int)

    def __init__(self, run_object):
        super(ClassificationThread, self).__init__(self)
        self.classification_run = run_object

    def run(self):
        '''Method that actually does the classification work. Emits the the
        :const:`change_value` signal everytime an image is classified. This is primary
        to update the progress bar widget in the `RunOrganizer` widget to
        notify the user how many images have been classified. Additionally,
        every five images classified the :const:`estimated_time` signal is emitted
        which includes a tuple that contains as the first item the time in
        seconds it took to classify the last five images and the number
        of images that remain to be classified as the second item. This allows
        for making an estimate on about how much time remains in until the
        thread finishes.
        '''
        for i, image in enumerate(self.classification_run.images):
            if image and image.path != str(BLANK_IMAGE):
                s = time.time()
                image.classify_image()
                e = time.time()
            self.change_value.emit(i+1)
            if i % 5 == 0:
                self.estimated_time.emit(
                    e-s, len(self.classification_run.images)-(i+1))
            # emit signal so know to move progress par forward


class FTPDownloadThread(thread):
    '''Thread specific for downloading files from a remote FTP server.

    :param ftp_connection: FTP connection object to download files from
    :type ftp_connection: :class:`FTP`
    :param file_paths: List absolute filepaths on the FTP server to download
    :type file_paths: list
    :param save_dir_path: Path on the local machine to store all downloaded files in
    :type save_dir_path: str or Path
    '''
    file_downloaded = pyqtSignal(int)
    download_path = pyqtSignal(str)

    def __init__(self, ftp_connection, file_paths, save_dir_path):
        super(FTPDownloadThread, self).__init__(self)
        self.ftp = ftp_connection
        self.file_paths = file_paths
        self.save_dir_path = save_dir_path

    def run(self):
        for i, remote_file_path in enumerate(self.file_paths):
            if self.ftp:
                local_file_path = os.path.join(
                    str(self.save_dir_path),
                    os.path.basename(str(remote_file_path))
                )
                with open(local_file_path, 'wb') as local_file:
                    cmd = 'RETR {}'.format(remote_file_path)
                    status = self.ftp.retrbinary(cmd, local_file.write)
            self.file_downloaded.emit(i)
            self.download_path.emit(local_file_path)
