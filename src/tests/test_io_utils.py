import os
import pytest
from datetime import datetime
from polo.utils.io_utils import *
from polo.crystallography.run import Run, HWIRun
from polo.crystallography.image import Image
from polo.crystallography.cocktail import *
# ============================================================================
# all imports below here


cocktail_metadata = '../data/cocktail_data/cocktail_meta.csv'
cocktail_dir = '../data/cocktail_data/'


@pytest.fixture
def xtal_test_files():
    xtal_files = 'tests/data/test_xtals'
    return [os.path.join(xtal_files, f) for f in os.listdir(xtal_files)]


@pytest.fixture
def run_deserializers(xtal_test_files):
    return [RunDeserializer(xtal_file) for xtal_file in xtal_test_files]


@pytest.fixture
def default_bartender():
    return BarTender(cocktail_meta=cocktail_metadata, cocktail_dir=cocktail_dir)


def test_deserializer_creation(xtal_test_files):
    for xtal_file in xtal_test_files:
        assert isinstance(RunDeserializer(xtal_file), RunDeserializer)


def test_xtal_to_run(run_deserializers):
    for rd in run_deserializers:
        run = rd.xtal_to_run()
        assert isinstance(run, (Run, HWIRun))
        for image in run.images:
            assert isinstance(image, Image)
            if image.cocktail:
                assert isinstance(image.cocktail, Cocktail)

        if run.cocktail_dict:
            for cocktail in run.cocktail_dict.values():
                assert isinstance(cocktail, Cocktail)
        


def test_bartender_init(default_bartender):
    assert isinstance(default_bartender, BarTender)


def test_bartender_menu_creation(default_bartender):
    assert default_bartender.menus

    for path, menu in default_bartender.menus.items():
        assert isinstance(path, str)
        assert isinstance(menu, Menu)


def test_bartender_menu_contents(default_bartender):
    for path, menu in default_bartender.menus.items():
        assert isinstance(path, str)
        assert isinstance(menu.start_date, datetime)
        assert (menu.type_ == 's' or menu.type_ == 'm')
        assert menu.cocktails
        assert isinstance(menu.path, str)


def test_bartender_get_menu_by_path(default_bartender):
    for path, menu in default_bartender.menus.items():
        assert default_bartender.get_menu_by_path(path).path == path


def test_cocktail_menu_reader(default_bartender):
    for path in default_bartender.menus:
        assert os.path.exists(path)
        menu_reader = CocktailMenuReader(path)
        for cocktail in menu_reader:
            assert isinstance(cocktail, Cocktail)
            for reagent in cocktail.reagents:
                assert isinstance(reagent, Reagent)

