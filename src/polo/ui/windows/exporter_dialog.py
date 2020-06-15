import json

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QBrush, QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QGridLayout

from polo import make_default_logger
from polo.ui.designer.UI_run_exporter import Ui_ExporDialog
# from polo.utils.io_utils import make_run_html, save_run_as_json

logger = make_default_logger(__name__)

class exporterDialog(QtWidgets.QDialog):

    EXPORT_DESCRIPTORS = 'data/text/file_format_info.json'

    def __init__(self, run_to_export):
        QtWidgets.QDialog.__init__(self)
        self.ui = Ui_ExporDialog()
        self.ui.setupUi(self)
        self.export_descriptors = self.read_export_descriptors()
        self.run_to_export = run_to_export
        
        self.ui.comboBox.currentTextChanged.connect(self.handle_export_change)
        
        logger.info('Opened {} for {}'.format(self, self.run_to_export))
        self.exec_()

    def read_export_descriptors(self):
        '''
        Read descriptors for each export type from EXPORT_DESCRIPTORS file
        path and return these descriptors as a dictionary. If cannot read
        the export descriptors file returns a empty dictionary.
        '''
        try:
            with open(self.EXPORT_DESCRIPTORS) as export_descrip:
                data = json.load(export_descrip)

                # format arrays to strings
                for xport_type in data:
                    text = data[xport_type]['text']
                    data[xport_type]['text'] = ' '.join(
                        [t.strip() for t in text])

                return data

        except (FileNotFoundError, PermissionError, KeyError) as e:
            logger.warning('Caught {} attempting to read file import descriptors\
                at {}'.format(e, self.EXPORT_DESCRIPTORS))
            return {}

    def handle_export_submit(self):
        export_type = str(self.ui.combobox.currentText())
        save_file_path = QtWidgets.QFileDialog.getSaveFileName(
            self, 'Save Run')
        if save_file_path:
            if export_type == 'xtal Format':
                save_run_as_json(self.run_to_export, save_file_path)
            elif export_type == 'HTML Report':
                make_run_html(self.run_to_export, save_file_path)

    def handle_export_change(self):
        current_export = str(self.ui.comboBox.currentText())
        if current_export == 'xtal Format':
            self.ui.textBrowser.setText(
                self.export_descriptors[current_export]['text'])
        elif current_export == 'HTML Report':
            self.ui.textBrowser.setText(
                self.export_descriptors[current_export]['text'])
