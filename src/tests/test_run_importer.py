import pytest
from polo.ui.windows.run_importer_dialog import RunImporterDialog

@pytest.fixture
def run_importer():
    return RunImporterDialog(current_run_names=None)