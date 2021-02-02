import os
import sys

import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

from polo import *
from polo.utils.io_utils import *
from polo.windows.run_importer_dialog import *

dirname = os.path.dirname(__file__)
app = QApplication(sys.argv)

@pytest.fixture
def full_run():
    test_run = RunDeserializer(os.path.join(
        dirname, 'test_files/xtals/test_vis.xtal'))
    test_run = test_run.xtal_to_run()
    return test_run

@pytest.fixture
def empty_HWI_run():
    return HWIRun()

@pytest.fixture
def image_dir():
    return os.path.join(dirname, 'test_files/X000015804202004011136-jpg')

@pytest.fixture
def invalid_dir():
    return dirname

@pytest.fixture
def import_dialog():
    return RunImporterDialog(current_run_names=[])

@pytest.fixture
def bartender():
    return bartender

def test_cocktail_imports(import_dialog):
    import_dialog.ui.radioButton.setChecked(True)  # membrane sceens
    for i in range(import_dialog.ui.comboBox_3.count()):
        item = import_dialog.ui.comboBox_3.itemText(i)
        get_menu = bartender.get_menu_by_basename(item)
        assert isinstance(get_menu, Menu)
        assert (isinstance(bartender.get_menu_by_basename(item), Menu)
                and os.path.basename(get_menu.path) == item
                )

def test_image_assignments(import_dialog):
    image_assignment_combobox = import_dialog.ui.comboBox_2
    for i in range(image_assignment_combobox.count()):
        item = image_assignment_combobox.itemText(i)
        assert item == IMAGE_SPECS[i]

def test_valid_hwi_image_import(image_dir, import_dialog):
    import_dialog.ui.stackedWidget.setCurrentIndex(0)
    import_dialog.validate_import(import_path=image_dir)
    assert import_dialog.current_dir_path_lineEdit.text() == image_dir
    assert import_dialog.ui.comboBox_2.currentText() == IMAGE_SPECS[0]  # visible
    assert import_dialog.current_run_name_lineEdit


def test_invalid_image_import(invalid_dir, import_dialog):
    import_dialog.ui.stackedWidget.setCurrentIndex(0)
    import_dialog.validate_import(invalid_dir)
    assert import_dialog.current_dir_path_lineEdit.text() == ''

def test_run_creation(import_dialog, image_dir):
    import_dialog.ui.stackedWidget.setCurrentIndex(0)
    # hwi run import
    import_dialog.validate_import(image_dir)
    import_dialog.create_new_run()

    assert isinstance(import_dialog.new_run, HWIRun)
    
def test_run_creation_non_hwi(import_dialog, image_dir):
    for i in range(1, 3):
        import_dialog.ui.stackedWidget.setCurrentIndex(i)
        import_dialog.validate_import(image_dir)
        import_dialog.create_new_run()

        assert isinstance(import_dialog.new_run, Run)
        assert import_dialog.new_run.run_name == import_dialog.current_run_name_lineEdit.text()
