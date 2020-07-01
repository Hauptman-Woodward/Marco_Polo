import os
from pathlib import Path
Ui_dir = '/home/ethan/Documents/github/Marco_Polo/pyqt_designer'
Ui_dir = os.path.join(os.path.abspath(__file__), '../pyqt_designer')

dirname = Path(os.path.dirname(__file__)).absolute()
print(dirname)

Ui_dir = dirname.parent.joinpath('pyqt_designer')
target_dir = dirname.joinpath('polo/designer')
ui_files = [Ui_dir.joinpath(f) for f in os.listdir(str(Ui_dir))]


for each_ui_file in ui_files:
    ui_name = 'UI_' + os.path.basename(str(each_ui_file)).split('.')[0] + '.py'
    full_target_path = os.path.join(str(target_dir), ui_name)

    # print(target_path)
    cmd = 'pyuic5 {} -o {}'.format(each_ui_file, full_target_path)
    os.system(cmd)
    print(cmd)