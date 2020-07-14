import pytest
from polo.crystallography.run import Run, HWIRun
import os
from polo.utils.io_utils import RunDeserializer

dirname = os.path.dirname(__file__)

@pytest.fixture
def full_run():
    test_run = RunDeserializer(os.path.join(
        dirname, 'test_files/xtals/test_vis.xtal'))
    test_run = test_run.xtal_to_run()
    return test_run

@pytest.fixture
def empty_HWI_run():
    return HWIRun()

@pytest.fixture
def image_dir():
    return os.path.join(dirname, 'test_files/X000015804202004011136-jpg')


def test_make_run_from_dir(image_dir):
    pass



