# tests for variables and functions in the polo __init__ file
import pytest
from polo import *
import logging
import pathlib
import tensorflow
from polo.utils.io_utils import BarTender, Menu
from polo.crystallography.cocktail import Cocktail


def test_logger():
    assert isinstance(make_default_logger(__name__), logging.Logger)

def test_icon_dict():
    for key, value in ICON_DICT.items():
        assert isinstance(key, str)
        assert isinstance(value, Path) 
        assert value.exists()

def test_model_creation():
    assert MODEL  # find out what type this should be 

def test_bartender_creation():
    assert isinstance(bartender, BarTender)
    assert bartender.menus
    for path, menu in bartender.menus.items():
        assert isinstance(path, str)
        assert isinstance(menu, Menu)
        for well_assignment, cocktail in menu.cocktails.items():
            assert isinstance(well_assignment, int)
            assert well_assignment > 0 and well_assignment <= 1537
            assert isinstance(cocktail, Cocktail)

