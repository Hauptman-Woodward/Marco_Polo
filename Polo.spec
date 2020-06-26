# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path
import platform
block_cipher = None


# update the repo to latest version

print('Pulling latest changes from git')
os.system('git pull')

# path to tensorflow in anaconda env
OS = platform.system()

tensorflow_binaries = []
tensorflow_location = {
  'Linux': '/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/tensorflow',
  'Darwin': '',
  'Windows': None
}
polo_locations = {  # paths to polo directory on each system 
  'Linux': '/home/ethan/Documents/github/Polo_Builder',
  'Darwin': '~/Documents/Marco_Polo/',
  'Windows': r'C:\Users\User\Desktop\marco_2\Marco_Polo'
}


tensorflow_location = tensorflow_location[OS]
print('tensorflow location set to {}'.format(tensorflow_location))

if tensorflow_location:  # do only for mac and linux working without
  # tensorflow binary gathering on windows for some reason
  for dir_name, sub_dir_list, fileList in os.walk(tensorflow_location):
      for f in fileList:
          if f.endswith(".so"):  # collect all binaries
              full_file = dir_name + '/' + f
              parent = Path(full_file).parent
              parent = str(parent) + '/*'
              target = parent.replace(tensorflow_location, 'tensorflow')[:-1]
              tensorflow_binaries.append((full_file, target))

print('Collected {} tensorflow_binaries'.format(len(tensorflow_binaries)))

a = Analysis(['src/Polo.py'],
             pathex=[polo_locations[OS]],
             binaries=[],
             datas=[('data', 'data/'), ('src/astor', 'astor/'),
                    ('unrar', 'unrar/')] + tensorflow_binaries,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='Polo',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True)
