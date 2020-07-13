from PyQt5 import QtCore, QtGui, QtWidgets 
class MapBox(QtWidgets.QComboBox):

    def __init(self, parent=None, mapping={}, sorter=lambda x: len(str(x))):
        super(MapBox, self).__init__(parent)
        self.mapping = mapping
        self.sorter = sorter  # function to sort keys by
    
    @property
    def mapping(self):
        return self.__mapping
    
    @mapping.setter
    def mapping(self, new_mapping):
        if isinstance(new_mapping, dict):
            self.__mapping = mapping
            self.clear()
            if new_mapping and self.sorter:
                self.addItems(sorted(new_mapping.keys(), key=self.sorter))
    
    def current_value(self):
        current_text = self.currentText()
        if current_text in self.mapping:
            return self.mapping[current_text]
    


