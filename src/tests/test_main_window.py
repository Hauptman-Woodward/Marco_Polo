import os
import sys

import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication
from pathlib import Path

from polo import *
from polo.utils.io_utils import *
from polo.windows.run_importer_dialog import *

from polo.windows.main_window import MainWindow

dirname = os.path.dirname(__file__)
app = QApplication(sys.argv)

@pytest.fixture
def main_window():
    return MainWindow()

@pytest.fixture
def run():
    run = RunDeserializer(os.path.join(
    dirname, 'test_files/xtals/test_vis.xtal'))
    run = run.xtal_to_run()
    return run

@pytest.fixture
def dummy_save_path():
    return os.path.join(dirname, 'test_files/write_bin/')

@pytest.fixture
def image_dir():
    return os.path.join(dirname, 'test_files/X000015804202004011136-jpg')

def test_image_import(main_window):
    import_actions = [
        main_window.actionFrom_FTP,
        main_window.actionFrom_Saved_Run_3,
        main_window.actionFrom_Directory
    ]
    for action in import_actions:
        assert not main_window.handle_image_import(action)

def test_set_current_run(main_window, run):
    assert isinstance(run, HWIRun)
    main_window.current_run = run
    assert isinstance(main_window.current_run, HWIRun)


def test_opening_hwi_run(main_window, run):

    main_window.handle_opening_run([run])

    assert main_window.current_run.run_name == run.run_name
    assert main_window.slideshoeInspector.run.run_name == run.run_name
    assert main_window.table_inspector.run.run_name == run.run_name
    assert main_window.optimizeWidget.run == run.run_name
    assert main_window.slideshowInspector.run == run.run_name

# def test_handle_export(main_window, run, dummy_save_path):
#     save_file_name = os.path.join(dummy_save_path, 'test_export')
#     if os.path.exists(save_file_name): os.remove(save_file_name)
#     export_actions = [
#         main_window.actionAs_HTML,
#         main_window.actionAs_CSV,
#         main_window.actionAs_MSO
#     ]
#     main_window.handle_opening_run([run])

#     dummy_path = Path(save_file_name)
#     for action in export_actions:
#         main_window.handle_export(action, export_path=save_file_name)
#         files = [os.path.join() for f in os.listdir(str(dummy_path.parent))]
#         # save file path will not have the suffix of the saved file
#         # since it is append on based on file type that is written
#         assert len(files) == 1
#         exported_file = files.pop()
#         assert os.path.isfile(str(exported_file))
#         assert dummy_path.name in str(exported_file)

# def test_handle_file_menu(main_window, run):
#     main_window.handle_opening_run([run])
#     assert isinstance(main_window.current_run, (Run, HWIRun))

#     file_menu_actions = [

#     ]

#     for action in file_menu_actions:
#         main_window.handle_file_menu(action)


    


        













