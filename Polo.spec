# -*- mode: python ; coding: utf-8 -*-

# Spec script to build exe files via pyinstaller
# Pass arg "F" at end of pyinstaller call to run in one file mode
import os
from pathlib import Path
import platform
import sys

cur_dir = Path().resolve()

block_cipher = None

# update the repo to latest version

print('Pulling latest changes from git')
os.system('git pull')

# path to tensorflow in anaconda env
OS = platform.system()

# tensorflow_binaries = []  # collect tensorflow files that pyinstaller misses here

# Paths to tensorflow package on your machine, you can either change these paths directly here
# when running this file or update your environmental variables to reflect the variable names
# in tensorflow_location dictionary

# polo_dir = os.environ['POLO_DIR']
# pptx_location = os.environ['PPTX_DIR']
# pptx_location = '/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/pptx/'
# if OS != 'Windows':
  # tensorflow_location = os.environ['TENSORFLOW_DIR']
#  tensorflow_location = '/home/ethan/anaconda3/envs/polo_3.5/lib/python3.5/site-packages/tensorflow'

#if not os.path.isdir(str(polo_dir)):
#    raise Exception(
#        'Polo directory {} does not exist! Please check the paths specified in the "polo_locations" vairable.')


# Set the path for Polo logo and icon
polo_logo = str(cur_dir.joinpath('src/data/images/logos/polo.png'))
polo_icon = str(Path(cur_dir).joinpath('src/data/images/icons/polo.ico'))

# Ask the user if they want to continue if either the logo or the icon cannot
# be found

if not os.path.isfile(polo_icon):
    print('WAIT WAIT WAIT POLO ICON NOT FOUND')
    if input('Q to quit, any other key to continue: ').lower() == 'q':
        sys.exit()

if not os.path.isfile(polo_logo):
    print('WAIT WAIT WAIT WHAT ABOUT THE BRANDING!')
    print('POLO LOGO NOT FOUND AT {}'.format(polo_logo))
    if input('Q to quit, any other key to continue: ').lower() == 'q':
        sys.exit()

#print('tensorflow location set to {}'.format(tensorflow_location))

#if tensorflow_location:  # do only for mac and linux working without
#    # tensorflow binary gathering on windows for some reason
#    for dir_name, sub_dir_list, fileList in os.walk(tensorflow_location):
#        for f in fileList:
#            if f.endswith(".so"):  # collect all binaries
#                full_file = dir_name + '/' + f
#                parent = Path(full_file).parent
#                parent = str(parent) + '/*'
#                target = parent.replace(tensorflow_location, 'tensorflow')[:-1]
#                tensorflow_binaries.append((full_file, target))

#print('Collected {} tensorflow_binaries'.format(len(tensorflow_binaries)))
#pptx_depends = [(pptx_location, 'pptx/')]

a = Analysis(['src/Polo.py'],
             pathex=[cur_dir],
             binaries=[],
             datas=[('src/data', 'data/'), ('src/astor', 'astor/'),
                    ('src/unrar', 'unrar/'), ('src/templates', 'templates/')], #+ tensorflow_binaries + pptx_depends,
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
