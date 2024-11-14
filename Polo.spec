# -*- mode: python ; coding: utf-8 -*-

# Spec script to build exe files via pyinstaller
# Pass arg "F" at end of pyinstaller call to run in one file mode
import os
from pathlib import Path
import platform
import sys
import tensorflow

from PyInstaller.utils.hooks import collect_all, collect_submodules
from PyInstaller.building.api import PYZ, EXE, COLLECT
from PyInstaller.building.build_main import Analysis
from PyInstaller.building.datastruct import Tree
# import tensorflow, tensorflow_core, tensorflow_estimator, tensorboard, google
import pptx

cur_dir = Path().resolve()
print(cur_dir)

block_cipher = None

# Set the path for Polo logo and icon
polo_logo = str(cur_dir.joinpath('src/data/images/logos/polo.png'))
polo_icon = str(Path(cur_dir).joinpath('src/data/images/icons/polo.ico'))

pptx_location = str(Path(pptx.__file__).parent)
pptx_depends = (pptx_location, 'pptx/')

# path to tensorflow in anaconda env
OS = platform.system()

a = Analysis(['src/Polo.py'],
             pathex=[cur_dir],
             binaries=[],
             datas=[('src/data', 'data/'), ('src/astor', 'astor/'),
                    ('src/unrar', 'unrar/'), ('src/templates', 'templates/'),
                    pptx_depends],
             hiddenimports=['tensorflow', 'tensorflow_core'],
            hookspath=['hooks'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=None,
             noarchive=False)

import site
site_packages = site.getsitepackages()[0]
tf_path = os.path.join(site_packages, 'tensorflow')
a.datas += Tree(tf_path, prefix='tensorflow', excludes=['*.pyc'])


pyz = PYZ(a.pure, a.zipped_data,
          cipher=None)

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