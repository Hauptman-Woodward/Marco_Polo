import pytest
from polo.utils.io_utils import *
from datetime import datetime
from polo import IMAGE_SPECS
from polo.crystallography.run import *
from pyqt5 import QtWidgets

dirname = Path(os.path.dirname(__file__))


@pytest.fixture
def image_dir():
    return os.path.join(dirname, 'test_files/X000015804202004011136-jpg')

def test_parse_metadata(image_dir):
    keys = ['image_spectrum', 'plate_id', 'date', 'run_name']
    parse_result = RunImporter.parse_hwi_dir_metadata(image_dir)
    assert parse_result
    assert isinstance(parse_result, dict)
    for k in keys:
        assert k in parse_result
    
    assert isinstance(parse_result[keys[2]], datetime)  # data
    assert parse_result[keys[0]] in IMAGE_SPECS

def test_directory_validator(image_dir):
    pass

def test_crack_open_a_rar_one(rar_dir):
    pass
# test to make sure unrar is working
# must have unrar install ready to go

def test_import_hwi_run(image_dir):
    import_result = RunImporter.import_hwi_run(image_dir)
    assert isinstance(import_result, HWIRun)
    assert not RunImporter.import_hei_run(dirname)

def test_import_general_run(image_dir):
    assert isinstance(RunImporter.import_general_run(image_dir), Run)
    assert not RunImporter.import_general_run(dirname)


def test_make_xtal_file_dialog():
    dlg = RunImporter.make_xtal_file_dialog()
    assert dlg
    assert isinstance(dlg, QtWidgets.QFileDialog)
