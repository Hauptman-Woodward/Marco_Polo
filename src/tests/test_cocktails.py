import pytest
from random import randint

#from cockatoo import screen
from polo.crystallography.cocktail import Cocktail

from polo import tim  # import the bartender
import logging

@pytest.fixture
def bartender():
    return tim

@pytest.fixture
def random_cocktail(bartender):
    menu = bartender.menus[list(bartender.menus.keys()).pop()]
    return menu[randint(1, len(menu)-1)]

# def test_compute_distance(bartender):
#     evaluated = False
#     for _ in range(10):
#         menu = bartender.menus[list(bartender.menus.keys()).pop()]
#         c_1 = menu[randint(1, len(menu)-1)]
#         c_2 = menu[randint(1, len(menu)-1)]
        
#         d_1 = c_1.compute_distance(c_2)
#         d_2 = c_1.compute_distance(c_1)

#         if d_1 != False:  # false means could not calc
#             evaluated = True
#             assert d_1 > 0
#             assert d_1 < 1
        
#         if d_2 != False:
#             evaluated = True
#             assert d_2 > 0
#             assert d_2 < 1
        
#         if d_1 and d_2:
#             evaluated = True
#             assert d_1 == d_2
#     assert evaluated

# def test_cockatoo_conversion(random_cocktail):
#     cockatoo_convert = random_cocktail.to_cockatoo_cocktail()
#     assert isinstance(cockatoo_convert, screen.Cocktail)




