from polo.designer.UI_cite import Ui_CitePolo
from polo.utils.dialog_utils import make_message_box
import webbrowser
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from polo import MARCO_ARTICLE, POLO_ARTICLE, make_default_logger

logger = make_default_logger(__name__)

class CiteDialog(QtWidgets.QDialog):
    '''Small dialog for displaying the contents of the Polo log file.
    '''

    def __init__(self, parent=None):
        super(CiteDialog, self).__init__(parent)
        self.ui = Ui_CitePolo()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self._open_polo_article)
        self.ui.pushButton_2.clicked.connect(self._open_marco_article)
        logger.debug("Created {}".format(self))
    
    def _open_polo_article(self):
        logger.debug('Opened Polo article link')
        pass

    def _open_marco_article(self):
        logger.debug('Opened MARCO article link')
        webbrowser.open(MARCO_ARTICLE)
    
