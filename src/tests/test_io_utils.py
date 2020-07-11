import os
import sys
from pathlib import Path
from molmass import Formula
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

dirname = os.path.dirname(__file__)

@pytest.fixture
def run():
    test_run = RunDeserializer(os.path.join(
        dirname, 'test_files/xtals/test_vis.xtal'))
    test_run = test_run.xtal_to_run()
    return test_run


@pytest.fixture
def main_window():
    return MainWindow()


@pytest.fixture
def plate_inspector():
    return PlateInspectorWidget(parent=None)


@pytest.fixture
def plate_inspec_run(plate_inspector, run):
    plate_inspector.run = run
    return plate_inspector


@pytest.fixture
def run_html_path():
    return os.path.join(dirname, 'test_files/write_bin/html.html')


@pytest.fixture
def xtal_write_path():
    return os.path.join(dirname, 'test_files/write_bin/test_xtal.xtal')


@pytest.fixture
def all_xtal_files():
    xtal_dir = os.path.join(dirname, 'test_files/xtals')
    return [os.path.join(xtal_dir, x) for x in os.listdir(xtal_dir)]


@pytest.fixture
def run_linker(all_xtal_files):
    runs = [RunDeserializer(p).xtal_to_run() for p in all_xtal_files]
    for r in runs:
        assert isinstance(r, HWIRun)
    return RunLinker(runs)


def test_cocktail_reading():
    '''Test cocktail reading by creating a bartender instance. 
    '''
    tender = BarTender(COCKTAIL_DATA_PATH, COCKTAIL_META_DATA)
    assert isinstance(tender, BarTender)

    tender.add_menus_from_metadata()
    assert tender.menus  # added menus

    for menu_path, menu in tender.menus.items():
        assert os.path.exists(menu_path)
        assert isinstance(menu, Menu)
        assert menu.path == menu_path

        for well, cocktail in menu.cocktails.items():
            assert well == cocktail.well_assignment
            assert isinstance(cocktail, Cocktail)
            assert isinstance(cocktail.number, str)
            assert hasattr(cocktail, 'reagents')

            for reagent in cocktail.reagents:
                assert isinstance(reagent, Reagent)
                assert reagent.chemical_additive  # has an additive

                if reagent.chemical_formula:  # not all have formulas
                    assert isinstance(reagent.chemical_formula,  Formula)


def test_run_deserializer(run):
    '''Slightly more extensive test for creating runs

    :param run: Hwi run instance
    :type run: HWIRun
    '''
    assert isinstance(run, HWIRun)
    for image in run.images:
        assert isinstance(image, Image)

    assert isinstance(run.cocktail_menu, Menu)


def test_xtal_writer(run, main_window, xtal_write_path):
    if os.path.exists(xtal_write_path):
        os.remove(xtal_write_path)

    writer = XtalWriter(run, main_window)
    result = writer.write_xtal_file(xtal_write_path)
    assert isinstance(result, str)
    assert os.path.isfile(result)
    assert XtalWriter.file_ext in result

    # test the contents of the xtal file and make sure it can be read
    # if os.path.isfile(result):
    #     with open(result) as xtal_file:
    #         line = xtal_file.readline()
    #         while isinstance(line, str) and '===' not in line:
    #             assert XtalWriter.header_flag in line

    os.remove(xtal_write_path)

        # header has been written correctly
        # attempt to read the xtal and compare it against the original run

        # reader = RunDeserializer(result)
        # test_run = reader.xtal_to_run()
        # assert isinstance(test_run, HWIRun)
        # assert test_run.run_name == run.run_name
        # for test_image, standard_image in zip(test_run.images, run.images):
        #     assert test_image.human_class == standard_image.human_class
        #     assert test_image.machine_class == standard_image.machine_class
        #     assert test_image.path == standard_image.path
        #     assert test_image.date == standard_image.date
        #     assert test_image.spectrum == standard_image.spectrum
        #     assert test_image.favorite == standard_image.favorite
        #     assert test_image.prediction_dict == standard_image.prediction_dict

def test_run_linker_init(run_linker):
    assert isinstance(run_linker, RunLinker)

def test_link_run_by_date(run_linker):
    run_linker.link_runs_by_date()
    for run in run_linker.loaded_runs:
        if run.image_spectrum == IMAGE_SPECS[0]:  # visible
            assert (
                (isinstance(run.next_run, HWIRun)
                 and run.next_run.run_name != run.run_name)
                or (
                    isinstance(run.previous_run, HWIRun)
                    and run.previous_run.run_name != run.run_name
                )
            )
            # if spectrum is visible assert that after linking by date
            # that the run is either linked to a next run or previous run
            # that is not itself

def test_link_run_by_spectrum(run_linker):
    run_linker.link_runs_by_spectrum()
    for run in run_linker.loaded_runs:
        if run.image_spectrum != IMAGE_SPECS[0]:  # not visible
            assert isinstance(run.alt_spectrum, HWIRun)
            assert run.alt_spectrum.image_spectrum != IMAGE_SPECS[0]
            assert run.alt_spectrum.run_name != run.run_name



