import sys
import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from pathlib import Path

import os

from polo.widgets.plate_inspector_widget import PlateInspectorWidget
from polo.crystallography.run import Run, HWIRun
from polo import IMAGE_CLASSIFICATIONS
from polo.utils.io_utils import RunDeserializer


dirname = os.path.dirname(__file__)
app = QApplication(sys.argv)


# helper functions
def scene_pixmaps(plate_viewer):
    return [item for item in plate_viewer.ui.plateViewer.scene.items()
            if isinstance(item, QtWidgets.QGraphicsPixmapItem)]


@pytest.fixture
def run():
    test_run = RunDeserializer(os.path.join(
        dirname, 'test_files/xtals/test_vis.xtal'))
    test_run = test_run.xtal_to_run()
    return test_run


@pytest.fixture
def plate_inspector():
    return PlateInspectorWidget(parent=None)


@pytest.fixture
def plate_inspec_run(plate_inspector, run):
    plate_inspector.run = run
    return plate_inspector


@pytest.fixture
def image_save_path():
    return os.path.join(dirname, 'test_files/write_bin/dummy.png')


def test_loading_run(plate_inspec_run, plate_inspector, run):
    plate_inspector.run = run
    assert isinstance(plate_inspector.run, HWIRun)
    assert isinstance(plate_inspec_run.run, HWIRun)


def test_reload_view(plate_inspec_run):
    try:
        plate_inspec_run.show_current_plate()
    except Exception:
        raise AssertionError  # raise assertion error


def test_navigation(plate_inspec_run):
    current_page = plate_inspec_run.ui.plateViewer.current_page
    plate_inspec_run.show_current_plate(next_view=True)
    assert current_page + 1 == plate_inspec_run.ui.plateViewer.current_page
    assert current_page < plate_inspec_run.ui.plateViewer.total_pages
    assert plate_inspec_run.ui.plateViewer.scene.items()

    current_page = plate_inspec_run.ui.plateViewer.current_page
    plate_inspec_run.show_current_plate(prev_view=True)
    assert current_page - 1 == plate_inspec_run.ui.plateViewer.current_page
    assert plate_inspec_run.ui.plateViewer.scene.items()


def test_filtering(plate_inspec_run):

    plate_inspec_run.ui.checkBox_27.setChecked(True)  # turn on filtering
    plate_inspec_run.show_current_plate()
    plate_inspec_run.ui.checkBox_21.setChecked(True)
    plate_inspec_run.apply_plate_settings()
    # test human classified images highlighted
    for item in scene_pixmaps(plate_inspec_run):
        if item.data(0).human_class:
            assert int(item.opacity()) == 1
        else:
            assert item.opacity() < 1
    # set up to highlight marco classified crystal images
    plate_inspec_run.ui.checkBox_21.setChecked(False)
    plate_inspec_run.ui.checkBox_22.setChecked(True)
    plate_inspec_run.ui.checkBox_23.setChecked(True)
    plate_inspec_run.apply_plate_settings()

    for item in scene_pixmaps(plate_inspec_run):
        if item.data(0).machine_class == IMAGE_CLASSIFICATIONS[0]:  # crystals
            assert int(item.opacity()) == 1
        else:
            assert item.opacity() < 1

    # turn off image filtering
    plate_inspec_run.ui.checkBox_27.setChecked(False)
    plate_inspec_run.apply_plate_settings()

    for item in scene_pixmaps(plate_inspec_run):
        assert int(item.opacity()) == 1


def test_images_per_plate(plate_inspec_run):

    combo = plate_inspec_run.ui.comboBox_7
    for index in range(combo.count()):
        combo.setCurrentIndex(index)  # go through all indices
        plate_inspec_run.show_current_plate()  # render the plate
        items = scene_pixmaps(plate_inspec_run)
        assert len(items) == int(combo.currentText())


def test_save_view(plate_inspec_run, image_save_path):
    plate_inspec_run.show_current_plate()
    plate_inspec_run.ui.plateViewer.export_current_view(
        save_path=image_save_path
    )
    assert hasattr(plate_inspec_run.ui.plateViewer, 'export_thread')
    while plate_inspec_run.ui.plateViewer.export_thread.isRunning():
        continue
    # wait until thread is finished
    assert os.path.isfile(image_save_path)
    if os.path.exists(image_save_path):
        os.remove(image_save_path)


def test_image_labeling(plate_inspec_run):
    plate_inspec_run.show_current_plate()
    check_status = plate_inspec_run.parse_label_checkboxes()
    for item in plate_inspec_run.ui.plateViewer.items():
        if isinstance(item, QtWidgets.QGraphicsTextItem):
            for key, value in check_status.items():
                if value:
                    assert key in item.toPlainText()
