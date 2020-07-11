import os
import sys
import pytest
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

from polo import *
from polo.crystallography.run import HWIRun, Run
from polo.crystallography.cocktail import Cocktail, Reagent
from polo.crystallography.image import Image
from polo.utils.io_utils import *
from polo.widgets.plate_inspector_widget import PlateInspectorWidget
from polo.windows.main_window import MainWindow
from random import randint
from polo.windows.run_importer_dialog import RunImporter

dirname = Path(os.path.dirname(__file__))
app = QApplication(sys.argv)
from tests import get_random_unicode

@pytest.fixture
def image_dirs():
    return list_dir_abs(str(dirname.joinpath('test_files/image_dirs')))

@pytest.fixture
def runs_from_image_dirs(image_dirs):
    runs = []
    for p in image_dirs:
        runs.append(RunImporter.import_run_from_directory(p))
    return runs

@pytest.fixture
def write_bin():
    return dirname.joinpath('test_files/write_bin')

@pytest.fixture
def dummy_pptx_path(write_bin):
    return write_bin.joinpath('dummy.pptx')

@pytest.fixture
def dummy_dead_pptx_path(write_bin):
    return write_bin.joinpath('dummy_dead.pptx')

@pytest.fixture
def sample_path(write_bin):
    return write_bin.joinpath('dummy_sample.pptx')

@pytest.fixture
def run():
    run_path = str(dirname.joinpath('test_files/xtals/test_vis.xtal'))
    run_maker = RunDeserializer(run_path)
    run = run_maker.xtal_to_run()
    return run

@pytest.fixture
def all_xtal_files():
    xtal_dir = os.path.join(str(dirname), 'test_files/xtals')
    return [os.path.join(xtal_dir, x) for x in os.listdir(xtal_dir)]

@pytest.fixture
def all_runs(all_xtal_files):
    runs = []
    for run in all_xtal_files:
        deserial = RunDeserializer(run)
        runs.append(deserial.xtal_to_run())
    return runs

@pytest.fixture
def dead_run():
    run_path =  str(dirname.joinpath('test_files/xtals/uvt_dead_paths.xtal'))
    run_maker = RunDeserializer(run_path)
    run = run_maker.xtal_to_run()
    return run

@pytest.fixture
def writer(dummy_pptx_path):
    return PptxWriter(
        dummy_pptx_path, image_types=IMAGE_CLASSIFICATIONS[0], marco=True)

def test_pptx_init(writer):
    assert isinstance(writer, PptxWriter)

def test_run_init(run):
    assert isinstance(run, (Run, HWIRun))

def test_make_single_run_presentation(writer, run, dead_run, dummy_dead_pptx_path):
    writer.make_single_run_presentation(
        run, 'Test Title', subtitle='Test Subtitle')
    assert os.path.isfile(writer.output_path)

    writer.output_path = str(dummy_dead_pptx_path)
    assert run.run_name != dead_run.run_name

    writer.delete_presentation()
    writer.marco, writer.human = False, True

    writer.make_single_run_presentation(
        dead_run, 'Test Dead Paths', subtitle='Dead paths'
    )
    assert os.path.isfile(writer.output_path)


def test_runs_from_image_dirs(runs_from_image_dirs):
    for r in runs_from_image_dirs:
        assert isinstance(r, (HWIRun, Run))
        
def test_make_sample_presentation(writer, runs_from_image_dirs, sample_path):
    writer.output_path = sample_path
    writer.make_sample_presentation(
        sample_name=get_random_unicode(20),
        runs=runs_from_image_dirs,
        title=get_random_unicode(20),
        subtitle=get_random_unicode(20),
        )
    assert os.path.isfile(str(writer.output_path))

# def test_make_sample_presentation_one_visible(all_runs, sample_path):
#     writer.output_path = sample_path
#     for 

    


