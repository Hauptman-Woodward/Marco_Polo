import pytest
import os
from polo.crystallography.image import Image
from polo.utils.io_utils import *
from random import randint

dirname = os.path.dirname(__file__)

@pytest.fixture
def run():
    test_run = RunDeserializer(os.path.join(
        dirname, 'test_files/xtals/test_vis.xtal'))
    test_run = test_run.xtal_to_run()
    return test_run


@pytest.fixture
def image_dir():
    return os.path.join(dirname, 'test_files/X000015804202004011136-jpg')


@pytest.fixture
def image_objects(image_dir):
    paths = list_dir_abs(image_dir, allowed=True)
    return [Image(path=p) for p in paths]
    # return abs paths to only images


def test_make_images(image_objects):
    for i in range(0, 100):
        rand_img = image_objects[randint(0, len(image_objects))]
        assert isinstance(rand_img, Image)


def test_classify_images(image_objects):
    for i in range(0, 100):
        rand_img = image_objects[randint(0, len(image_objects))]
        rand_img.classify_image()
        assert rand_img.prediction_dict
        assert isinstance(rand_img.prediction_dict, dict)
        assert rand_img.machine_class
        assert rand_img.machine_class in IMAGE_CLASSIFICATIONS

def test_make_delete_pixmaps(image_objects):
    for i in range(0, 20):
        rand_img = image_objects[randint(0, len(image_objects))]
        rand_img.classify_image()
        rand_img.setPixmap()
        assert not rand_img.isNull()
        rand_img.delete_pixmap_data()
        assert rand_img.isNull()


def test_make_base64(image_objects):
    for i in range(0, 20):
        rand_img = image_objects[randint(0, len(image_objects))]
        assert rand_img.bites
        assert isinstance(rand_img.bites, bytes)
        # all paths should exist


        


    