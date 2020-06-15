import pytest
from polo.ui.widgets.plate_inspector_widget import PlateInspectorWidget
from polo.utils.io_utils import RunDeserializer
from polo.crystallography.run import *
from polo import COLORS
from PyQt5.QtGui import QBitmap, QBrush, QColor, QIcon, QPainter, QPixmap
from random import randint

test_xtal_path = 'tests/data/test_xtals/jun_15_save.xtal'

#TODO Figure out how to make windows and widgets without have pytester
# crash Last file traceback from crash at the bottom of this file

# @pytest.fixture
# def run():
#     return RunDeserializer(test_xtal_path).xtal_to_run()


# @pytest.fixture
# def plate_inspector(run):
#     return PlateInspectorWidget(parent=None, run=run)


# def test_plate_inspec_init(plate_inspector):
#     assert isinstance(plate_inspector, PlateInspectorWidget)
#     assert isinstance(plate_inspector.run, (Run, HWIRun))


# def test_image_class_checkboxes_titles(plate_inspector):
#     for class_, checkbox in plate_inspector.image_type_checkboxes:
#         assert checkbox.text() == class_


# def test_color_options(plate_inspector):
#     for combo_box in plate_inspector.color_combos:
#         assert combo_box.currentText() in COLORS


# def test_plateview_init(plate_inspector):
#     assert plate_inspector.ui.plateViewer.run.run_name == plate_inspector.run.run_name


# def test_human_checkbox(plate_inspector):
#     plate_inspector.ui.checkBox_21.setChecked(True)
#     assert plate_inspector.human is True


# def test_marco_checkbox(plate_inspector):
#     plate_inspector.ui.checkBox_22.setChecked(True)
#     assert plate_inspector.maro is True


# def test_color_mapping(plate_inspector):
#     assert isinstance(plate_inspector.color_mapping, dict)
#     for image_class, color_combobox in plate_inspector.color_combos.items():
#         assert isinstance(
#             plate_inspector.color_mapping[color_combobox.currentText()],
#             QColor)


# def test_selected_classifications(plate_inspector):
#     for class_, combobox in plate_inspector.image_type_checkboxes:
#         checked = randint(0, 1)
#         combobox.setChecked(checked)
#         if checked:
#             assert class_ in plate_inspector.selected_classifications
#         else:
#             assert class_ not in plate_inspector.selected_classifications


# def test_navigate_plateview(plate_inspector):

#     # test next page
#     current_page = plate_inspector.ui.plateViewer.current_page
#     plate_inspector.navigate_plateview(next_page=True)
#     assert current_page + 1 == plate_inspector.ui.plateViewer.current_page

#     # expand to other test cases with other navigation directions



# Current thread 0x00007f8ca153d740 (most recent call first):
#   File "/home/ethan/Documents/github/Polo_Builder/src/polo/ui/widgets/plate_inspector_widget.py", line 17 in __init__
#   File "/home/ethan/Documents/github/Polo_Builder/src/tests/test_plate_inspector.py", line 19 in plate_inspector
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/_pytest/fixtures.py", line 792 in call_fixture_func
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/_pytest/fixtures.py", line 964 in pytest_fixture_setup
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/pluggy/callers.py", line 187 in _multicall
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/pluggy/manager.py", line 87 in <lambda>
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/pluggy/manager.py", line 93 in _hookexec
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/pluggy/hooks.py", line 286 in __call__
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/_pytest/fixtures.py", line 914 in execute
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/_pytest/fixtures.py", line 584 in _compute_fixture_value
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/_pytest/fixtures.py", line 503 in _get_active_fixturedef
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/_pytest/fixtures.py", line 487 in getfixturevalue
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/_pytest/fixtures.py", line 477 in _fillfixtures
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/_pytest/fixtures.py", line 297 in fillfixtures
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/_pytest/python.py", line 1483 in setup
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/_pytest/runner.py", line 373 in prepare
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/_pytest/runner.py", line 123 in pytest_runtest_setup
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/pluggy/callers.py", line 187 in _multicall
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/pluggy/manager.py", line 87 in <lambda>
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/pluggy/manager.py", line 93 in _hookexec
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/pluggy/hooks.py", line 286 in __call__
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/_pytest/runner.py", line 217 in <lambda>
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/_pytest/runner.py", line 244 in from_call
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/_pytest/runner.py", line 217 in call_runtest_hook
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/_pytest/runner.py", line 186 in call_and_report
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/_pytest/runner.py", line 94 in runtestprotocol
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/_pytest/runner.py", line 85 in pytest_runtest_protocol
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/pluggy/callers.py", line 187 in _multicall
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/pluggy/manager.py", line 87 in <lambda>
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/pluggy/manager.py", line 93 in _hookexec
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/pluggy/hooks.py", line 286 in __call__
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/_pytest/main.py", line 272 in pytest_runtestloop
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/pluggy/callers.py", line 187 in _multicall
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/pluggy/manager.py", line 87 in <lambda>
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/pluggy/manager.py", line 93 in _hookexec
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/pluggy/hooks.py", line 286 in __call__
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/_pytest/main.py", line 247 in _main
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/_pytest/main.py", line 191 in wrap_session
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/_pytest/main.py", line 240 in pytest_cmdline_main
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/pluggy/callers.py", line 187 in _multicall
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/pluggy/manager.py", line 87 in <lambda>
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/pluggy/manager.py", line 93 in _hookexec
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/pluggy/hooks.py", line 286 in __call__
#   File "/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/_pytest/config/__init__.py", line 125 in main
#   File "/home/ethan/anaconda3/envs/polo_3.5/bin/pytest", line 8 in <module>
# Aborted (core dumped)

