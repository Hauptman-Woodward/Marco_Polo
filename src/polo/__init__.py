import logging
import os
import re
from pathlib import Path
import sys
import platform

import tensorflow as tf


from PyQt5.QtGui import QBrush, QColor, QIcon, QPixmap
from PyQt5 import QtWidgets
#from tensorflow.contrib.predictor import from_saved_model


polo_version = '0.2.0'  # should be int.int.int format
dirname = Path(os.path.dirname(__file__)).parent


# CONSTANT FILE PATHS
# =============================================================================

LOG_PATH = Path('polo.log')  # always in same dir as Polo main file
RECENT_FILES = Path('recents.txt')
DATA_DIR = dirname.joinpath('data')
APP_ICON = DATA_DIR.joinpath('images/logos/polo.png')
UNRAR = dirname.joinpath('unrar')
TEMP_DIR = dirname.joinpath('.tmp')

BACKUP_DIR = Path(os.getcwd()).joinpath('.polo_backups')

if not TEMP_DIR.is_dir():
    os.makedirs(str(TEMP_DIR))

if not BACKUP_DIR.is_dir():
    os.makedirs(str(BACKUP_DIR))

if not RECENT_FILES.is_file():
    f = open(str(RECENT_FILES), 'w')
    f.close()
    

COCKTAIL_DATA_PATH = DATA_DIR.joinpath('cocktail_data')
COCKTAIL_META_DATA = COCKTAIL_DATA_PATH.joinpath('cocktail_meta.csv')
# cocktail meta data csv stores info about each of the cocktail menus. Stuff
# like when each menu was used and what type of screen it is (Soluble or 
# membrane screens)

# images to show when missing images or no image found 
DEFAULT_IMAGE_PATH, BLANK_IMAGE = (
    DATA_DIR.joinpath('images/default_images/default_image.jpg'),
    DATA_DIR.joinpath('images/default_images/blank_image.png')
)

# path to tensorflow marco model
MODEL_PATH = DATA_DIR.joinpath('savedmodel')

SESSION = tf.Session(graph=tf.Graph())
LOADED_MODEL = tf.saved_model.loader.load(
    SESSION, [tf.saved_model.tag_constants.SERVING], str(MODEL_PATH)
    )


# HTML jinja2 templates
RUN_HTML_TEMPLATE = dirname.joinpath('templates/exportRunTemplate.html')
SCREEN_HTML_TEMPLATE = dirname.joinpath('templates/exportPlatesTemplate.html')
BLANK_IMAGE = Path('data/images/default_images/blank_image.png')

# icons for tabs and buttons of the GUI

ICONS = DATA_DIR.joinpath('images/icons')
ICON_DICT = {Path(icon).stem: ICONS.joinpath(icon)
             for icon in os.listdir(str(ICONS))}


# DATA
# =============================================================================


ALLOWED_IMAGE_TYPES = {'.jpeg', '.png', '.jpg'}

IMAGE_CLASSIFICATIONS = [
    'Crystals', 'Clear', 'Precipitate', 'Other'
]

COLORS = {
    'red': QColor(199, 40, 58), 'blue': QColor(40, 133, 199),
    'green': QColor(95, 199, 40), 'orange': QColor(199, 127, 40),
    'yellow': QColor(199, 196, 40), 'grey': QColor(145, 145, 138),
    'purple': QColor(195, 24, 204), 'none': None
}

ALLOWED_IMAGE_COUNTS = [24, 96, 192, 384, 786, 1536]

IMAGE_SPECS = ['Visible', 'UV-TPEF', 'SHG', 'Other']
SPEC_KEYS = dict(zip(['jpg', 'uvt', 'shg', ''], IMAGE_SPECS))

MSO_DICT = {  # translate between marco encodings and mso encodings
    IMAGE_CLASSIFICATIONS[0]: 90,  # xtal
    #IMAGE_CLASSIFICATIONS[3]: 60,  # skin
    IMAGE_CLASSIFICATIONS[2]: 50,  # precipitate
    #IMAGE_CLASSIFICATIONS[2]: 25,  # phase
    IMAGE_CLASSIFICATIONS[1]: 10,  # clear
    #IMAGE_CLASSIFICATIONS[3]: 5,   # garbage
    IMAGE_CLASSIFICATIONS[3]: 0    # unsure
}
REV_MSO_DICT = {
    90: IMAGE_CLASSIFICATIONS[0],  # xtal
    60: IMAGE_CLASSIFICATIONS[3], # skin
    50: IMAGE_CLASSIFICATIONS[2],  # precipitate
    25: IMAGE_CLASSIFICATIONS[2],  # phase
    10: IMAGE_CLASSIFICATIONS[1],  # clear
    5: IMAGE_CLASSIFICATIONS[3],   # garbage
    0: IMAGE_CLASSIFICATIONS[3]   # unsure
}

# UNRAR EXE
# =============================================================================

unrar_versions = set([OS for OS in os.listdir(str(UNRAR))])
platform = platform.system()
if platform in unrar_versions:
    UNRAR_DIR = Path(os.path.join(str(UNRAR), platform))
else:
    UNRAR_DIR = False

if UNRAR_DIR:
    if platform == 'Windows':
        # get bits
        if sys.maxsize > 2**32:  # is 64 bit version
            UNRAR_DIR = UNRAR_DIR.joinpath('Win64')
        else:
            UNRAR_DIR = UNRAR_DIR.joinpath('Win32')
    UNRAR_EXE = [UNRAR_DIR.joinpath(f) for f in os.listdir(
        str(UNRAR_DIR)) if 'unrar' in f].pop()
else:
    UNRAR_EXE = Path('unrar')  # pray they have it installed and in their PATH
    
# REGEX
# =============================================================================
num_regex = re.compile('[-+]?([0-9]*\.[0-9]+|[0-9]+)')
peg_regex = re.compile('[0-9]+')
unit_regex = re.compile('v/v|w/v|M|L|ml|ul', re.I)
water_regex = re.compile('\*[0-9]*h2o', re.I)


# FUNCTIONS
# =============================================================================

def make_default_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(levelname)s\t%(asctime)s\t%(name)s\t%(lineno)d\t%(message)s')
    file_handler = logging.FileHandler(str(LOG_PATH))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


# URLS
# =============================================================================

# link to the documentation site 
HOST_PREFIX = 'https://hauptman-woodward.github.io/'

ABOUT = HOST_PREFIX + 'Marco_Polo/about.html'
QUICKSTART = HOST_PREFIX + 'Marco_Polo/Quickstart.html'
FAQS = HOST_PREFIX + 'Marco_Polo/FAQS.html'
USER_GUIDE = HOST_PREFIX + 'Marco_Polo/user_guide.html'
DOCS = HOST_PREFIX + 'Marco_Polo/polo.html'
BETA = HOST_PREFIX + 'Marco_Polo/beta_testers.html'
REPORTS = HOST_PREFIX + 'Marco_Polo/reports.html'

RELEASES = 'https://github.com/Hauptman-Woodward/Marco_Polo/tags'

MARCO_ARTICLE = 'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0198883'
POLO_ARTICLE = 'https://journals.iucr.org/j/issues/2021/02/00/ei5066/index.html'
POLO_CITATION = '''
Holleman, E.T., Duguid, E., Keefe, L.J. & Bowman, S.E.J. (2021). J. Appl. Cryst. 54, https://doi.org/10.1107/S1600576721000108
'''
MARCO_CITATION = '''
Bruno AE, Charbonneau P, Newman J, Snell EH, So DR, et al. (2018) Classification of crystallization outcomes using deep convolutional neural networks. PLOS ONE 13(6): e0198883. https://doi.org/10.1371/journal.pone.0198883
'''

# RUN_TYPES = sorted(
#             [types[-1] for types in 
#             inspect.getmembers(sys.modules['polo.crystallography.run'], inspect.isclass)
#             if issubclass(types[-1], Run)],
#             key=lambda c: c.import_priority,
#             reverse=True)


# get all classes in the Run module that are subclassed from Run this is
# used for imports. Sort th


# logger = make_default_logger(__name__)

# logger.debug('Detected OS: {}'.format(platform))
# logger.debug('Working directory: {}'.format(os.getcwd()))
# logger.debug('Polo directory: {}'.format(dirname))

critical_paths = [
    MODEL_PATH, COCKTAIL_DATA_PATH, COCKTAIL_META_DATA, BACKUP_DIR,
    TEMP_DIR, DATA_DIR
]

# for path in critical_paths:
#     if path.exists():
#         logger.debug('Critical path {} checked'.format(path))
#     else:
#         logger.critical('Critical path {} does not exist!'.format(path))

from polo.utils.io_utils import BarTender, Menu
bartender = BarTender(str(COCKTAIL_DATA_PATH), str(COCKTAIL_META_DATA))

from polo.crystallography.image import *
from polo.crystallography.cocktail import *
from polo.crystallography.run import *
from polo.threads import *

