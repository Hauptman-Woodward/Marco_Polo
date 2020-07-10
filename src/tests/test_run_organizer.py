import os
import sys

import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication
from pathlib import Path
import time

from polo.widgets.run_organizer import RunOrganizer
from polo.utils.io_utils import *

dirname = os.path.dirname(__file__)
app = QApplication(sys.argv)

@pytest.fixture
def all_xtal_files():
    xtal_dir = os.path.join(dirname, 'test_files/xtals')
    return [os.path.join(xtal_dir, x) for x in os.listdir(xtal_dir)]

@pytest.fixture
def all_runs(all_xtal_files):
    for run in all_xtal_files:
        deserial = RunDeserializer(run)
        yield deserial.xtal_to_run()

@pytest.fixture
def run_org():
    return RunOrganizer()

@pytest.fixture
def run_tree(run_org):
    return run_org.ui.runTree

def test_run_addition(all_xtal_files, run_organizer):
    for xtal_file in all_xtal_files:
        assert not run_org.add_from_saved_run(xtal_file)

def test_run_tree_addition(all_runs, run_tree):
    for run in all_runs:
        assert isinstance(run, (HWIRun, Run))
        run_tree.add_run_to_tree(run)
        assert run.run_name in run_tree.all_runs

def test_run_linking(all_xtal_files, run_org):
    for xtal_file in all_xtal_files:
        assert os.path.isfile(xtal_file)
        run_org.add_from_saved_run(xtal_file)
    
    assert run_org.ui.runTree.all_runs
    for run in run_org.ui.runTree.all_runs.items():
        if run.image_spectrum == IMAGE_SPECS[0]:  # visible
            assert (isinstance(run.next_run, (HWIRun, Run)) 
                   or isinstance(run.previous_run, (Run, HWIRun))
                )
        else:
            assert isinstance(run.alt_spectrum, (Run, HWIRun))
    
    # xtal dir should have four files all of the same sample two visible
    # spectrum runs and two non visible spectrum runs

def test_classification_thread_opening(all_xtal_files, run_org):
    xtal_file = all_xtal_files.pop()
    assert os.path.isfile(xtal_file)
    run_org.import_from_saved_run(xtal_file)

    assert run_org.ui.runTree.all_runs

    all_runs = run_org.ui.run_tree.all_runs  # should just be one
    
    for run_name, run in all_runs.items():
        run_org.open_classification_thread(run)
        assert hasattr(run_org, 'classification_thread')
        assert run_org.classification_thread.isRunning()
        break
    
    # let the classification progress for 10 seconds
    start_timer = time.time()
    start_progress_value = run_org.ui.progressBar.value()
    while time.time() - start_timer < 10:
        continue
    assert run_org.ui.progressBar.value() > start_progress_value
    # assert that the progress bar as incremeneted
    
    if run_org.classification_thread.isRunning():
        run_org.classification_thread.end()  # or stop need to find out the command
    
    # test to make sure at least some of the images where classified

    assert sum([1 for image in run.images
                  if image.machine_class in IMAGE_CLASSIFICATIONS]) >= 1
    

    

    



    
    

            









        




