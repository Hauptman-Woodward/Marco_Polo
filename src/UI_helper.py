import os

Ui_dir = '/home/ethan/Documents/github/Marco_Polo/pyqt_designer'
target_dir = '/home/ethan/Documents/github/Marco_Polo/src/polo/designer'
ui_files = [os.path.join(Ui_dir, f) for f in os.listdir(Ui_dir)]

for each_ui_file in ui_files:
    ui_name = 'UI_' + os.path.basename(each_ui_file).split('.')[0] + '.py'
    
    target_path = os.path.join(target_dir, ui_name)
    print(target_path)
    cmd = 'pyuic5 {} -o {}'.format(each_ui_file, target_path)
    os.system(cmd)
    print(cmd)