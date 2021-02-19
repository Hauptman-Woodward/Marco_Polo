from polo.designer.UI_cite import Ui_CitePolo
from polo.utils.dialog_utils import make_message_box
import webbrowser
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from polo import (MARCO_ARTICLE, POLO_ARTICLE, POLO_CITATION, 
                  MARCO_CITATION, make_default_logger)

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
        self._display_citation_text()
        logger.debug("Created {}".format(self))
    
    @property
    def citation_display_text(self):
        return '''
        <h1>If you found Polo useful for your work, please consider citing:</h1>
        <br><br>
        1. {}
        <br><br>
        2. {}
        <br>
        <p>Thank you for using Polo!</p>
        '''.format(POLO_CITATION, MARCO_CITATION)
    
    def _display_citation_text(self):
        self.ui.PoloCite.setText(self.citation_display_text)
    
    def _open_polo_article(self):
        logger.debug('Opened Polo article link')
        webbrowser.open(POLO_ARTICLE)
        pass

    def _open_marco_article(self):
        logger.debug('Opened MARCO article link')
        webbrowser.open(MARCO_ARTICLE)
    
