import logging
import os
import re
from pathlib import Path
import sys


from PyQt5.QtGui import QBrush, QColor, QIcon, QPixmap
from PyQt5 import QtWidgets
from tensorflow.contrib.predictor import from_saved_model

__version__ = '0.0.2'

# CONSTANT FILE PATHS
# =============================================================================

LOG_PATH = Path('polo.log')  # always in same dir as Polo main file
APP_ICON = Path('polo.png')

# When packaged with pyinstaller Polo main is run from same directory
# as data is stored in. This is not the case when running from
# a non-exe file

if os.path.isdir('./data'):  # data is in same dir as __main__
    data_prefix = 'data'
else:
    data_prefix = '/home/ethan/Documents/github/Polo_Builder/data'
    #data_prefix = '../data/'
    # above is temp for spinx only
    # os.path.abspath('../data')  # running as python script
COCKTAIL_DATA_PATH = Path(os.path.join(data_prefix, 'cocktail_data/'))
COCKTAIL_META_DATA = Path(os.path.join(
    data_prefix, 'cocktail_data/cocktail_meta.csv'))
DEFAULT_IMAGE_PATH = Path(os.path.join(
    data_prefix, 'images/default_images/default_image.jpg'))
MODEL_PATH = Path(os.path.join(data_prefix, 'savedmodel'))
BLANK_IMAGE = Path(os.path.join(data_prefix), 'images/default_images/blank_image.png')

# HTML jinja2 templates
RUN_HTML_TEMPLATE = Path('polo/templates/exportRunTemplate.html')
SCREEN_HTML_TEMPLATE = Path('polo/templates/exportPlatesTemplate.html')
BLANK_IMAGE = Path('../data/images/default_images/blank_image.png')
# templates are not found when Polo not run from src directory

# image icons

ICONS = Path(os.path.join(data_prefix, 'images/icons'))

ICON_DICT = {Path(icon).stem: ICONS.joinpath(icon)
             for icon in os.listdir(str(ICONS))}


# DATA
# =============================================================================

MODEL = from_saved_model(str(MODEL_PATH))
ALLOWED_IMAGE_TYPES = {'.jpeg', '.png', '.jpg'}
HWI_IMAGE_NAMING_SCHEMA = [
    'Plate_name',
    'Well_number',
    'Date',
    'Other'
]
IMAGE_CLASSIFICATIONS = [
    'Crystals', 'Clear', 'Precipitate', 'Other'
]

DEFAULT_TABLE_HEADERS = [
    'path', 'well_number', 'date', 'machine_class', 'human_class', 'spectrum'
]

COLORS = {
    'red': QColor(199, 40, 58), 'blue': QColor(40, 133, 199),
    'green': QColor(95, 199, 40), 'orange': QColor(199, 127, 40),
    'yellow': QColor(199, 196, 40), 'grey': QColor(145, 145, 138),
    'purple': QColor(195, 24, 204), 'none': None
}

ALLOWED_IMAGE_COUNTS = [24, 96, 192, 384, 786, 1536]

# REGEX
# =============================================================================
num_regex = re.compile('[-+]?([0-9]*\.[0-9]+|[0-9]+)')
peg_regex = re.compile('[0-9]+')
unit_regex = re.compile('v/v|w/v|M|L', re.I)
water_regex = re.compile('\*[0-9]*h2o', re.I)


# FUNCTIONS
# =============================================================================

def make_default_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(levelname)s:%(asctime)s:%(name)s:%(lineno)d:%(message)s')
    file_handler = logging.FileHandler(str(LOG_PATH))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# classes have imports from __init__ so need to follow initialization
# of all constants




# URLS
# =============================================================================
ABOUT = 'https://ethanholleman.github.io/Marco_Polo/about.html'
QUICKSTART = 'https://ethanholleman.github.io/Marco_Polo/Quickstart.html'
FAQS = 'https://ethanholleman.github.io/Marco_Polo/FAQS.html'
USER_GUIDE = 'https://ethanholleman.github.io/Marco_Polo/user_guide.html'
DOCS = 'https://ethanholleman.github.io/Marco_Polo/polo.html'
BETA = 'https://ethanholleman.github.io/Marco_Polo/beta_testers.html'

from polo.crystallography.cocktail import Cocktail, Reagent, SignedValue
from polo.threads import thread
from polo.utils.io_utils import BarTender
from polo.crystallography.image import Image
from polo.crystallography.run import HWIRun, Run


# best bartender at Cunneen's bar in Rodger's Park
tim = BarTender(str(COCKTAIL_DATA_PATH), str(COCKTAIL_META_DATA))
