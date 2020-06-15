from polo import *
import os


def check_for_missing_data():
    # make list of filepaths not in another data structure
    # only check for critical data (not icons and that kind of thing)
    paths = [COCKTAIL_META_DATA, COCKTAIL_DATA_PATH, DEFAULT_IMAGE_PATH,
            MODEL_PATH, RUN_HTML_TEMPLATE, SCREEN_HTML_TEMPLATE]
    try:
        for p in paths:
            assert os.path.exists(p)
        return True
    except AssertionError as e:
        return e


