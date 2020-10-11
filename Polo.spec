# -*- mode: python ; coding: utf-8 -*-

# Spec script to build exe files via pyinstaller
# Pass arg "F" at end of pyinstaller call to run in one file mode

block_cipher = None

import os
from pathlib import Path
import platform
import sys
block_cipher = None


# update the repo to latest version

print('Pulling latest changes from git')
os.system('git pull')

# path to tensorflow in anaconda env
OS = platform.system()

tensorflow_binaries = []
tensorflow_location = {
  'Linux': '/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/tensorflow',
  'Darwin': '/Users/michelleholleman/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/tensorflow',
  'Windows': None
  # thanks for letting me borrow the mac Mom
}

pptx_location = {
  'Linux': '/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/pptx/',
  'Darwin': '/Users/michelleholleman/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/pptx/',
  'Windows': '\\Users\\User\\.conda\\envs\\polo_3.5\\lib\\site-packages\\pptx\\'
  # thanks for letting me borrow the mac Mom
}


polo_locations = {  # paths to polo directory on each system 
  'Linux': '/home/ethan/Documents/github/Marco_Polo',
  'Darwin': '/Users/michelleholleman/Documents/Marco_Polo/',
  'Windows': r'C:\Users\User\Desktop\marco_3\Marco_Polo'
}

polo_dir = polo_locations[OS]
polo_logo = Path(polo_dir).joinpath('src/data/images/logos/polo.png')
polo_logo = str(polo_logo)  # use path to avoid issues on windows

polo_icon = str(Path(polo_dir).joinpath('src/data/images/icons/polo.ico'))

print('Added logo at {}'.format(polo_logo))
print(sys.argv)

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
pptx_depends = [(pptx_location[OS], 'pptx/')]

a = Analysis(['src/Polo.py'],
             pathex=[polo_dir],
             binaries=[],
             datas=[('src/data', 'data/'), ('src/astor', 'astor/'),
                    ('src/unrar', 'unrar/'), ('src/templates', 'templates/')] + tensorflow_binaries + pptx_depends,
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
  

if len(sys.argv) > 0 and sys.argv[-1] == 'F':  # make ony file mode
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
            console=True,
            icon=polo_icon)
else:  # make as dir
  exe = EXE(pyz,
            a.scripts,
            [],
            exclude_binaries=True,
            name='Polo',
            debug=False,
            bootloader_ignore_signals=False,
            strip=False,
            upx=True,
            console=True,
            icon=polo_icon)

  coll = COLLECT(exe,
                a.binaries,
                a.zipfiles,
                a.datas,
                strip=False,
                upx=True,
                upx_exclude=[],
                name='Polo')