# -*- mode: python ; coding: utf-8 -*-

# Spec script to build exe files via pyinstaller
# Pass arg "F" at end of pyinstaller call to run in one file mode
import os
from pathlib import Path
import platform
import sys
import PyQt5
# import tensorflow, tensorflow_core, tensorflow_estimator, tensorboard, google
import pptx

cur_dir = Path().resolve()
print(cur_dir)

block_cipher = None

# update the repo to latest version

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

# if not os.path.isdir(str(polo_dir)):
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

# print('tensorflow location set to {}'.format(tensorflow_location))

# tensorflow_location = str(Path(tensorflow.__file__).parent)
# tensorflow_depends = (tensorflow_location, 'tensorflow/')

# tensorcore_loc = str(Path(tensorflow_core.__file__).parent)
# tensorcore_depends = (tensorcore_loc, 'tensorflow_core/')

# tensorflow_estimator_loc = str(Path(tensorflow_estimator.__file__).parent)
# tensorflow_estimator_depends = (tensorflow_estimator_loc, 'tensorflow_estimator/')

# tensorboard_loc = str(Path(tensorboard.__file__).parent)
# tensorboard_depends = (tensorboard_loc, 'tensorboard/')

#google_loc = str(Path(tensorflow_location).parent.joinpath('google'))
#google_depends = (google_loc, 'google/')

#sol = str(Path(tensorflow_location).parent.joinpath('_solib_k8'))
#sol_depends = (sol, '_solib_k8/')

# for dir_name, sub_dir_list, fileList in os.walk(tensorflow_location):
#     for f in fileList:
#         if f.endswith(".so"):  # collect all binaries
#             full_file = dir_name + '/' + f
#             parent = Path(full_file).parent
#             parent = str(parent) + '/*'
#             target = parent.replace(tensorflow_location, 'tensorflow')[:-1]
#             tensorflow_binaries.append((full_file, target))


pptx_location = str(Path(pptx.__file__).parent)
pptx_depends = (pptx_location, 'pptx/')


# ------------------------------------------------------------------
# Copyright (c) 2020 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------

from PyInstaller.utils.hooks import is_module_satisfies, \
    collect_submodules, collect_data_files

tf_pre_1_15_0 = is_module_satisfies("tensorflow < 1.15.0")
tf_post_1_15_0 = is_module_satisfies("tensorflow >= 1.15.0")
tf_pre_2_0_0 = is_module_satisfies("tensorflow < 2.0.0")
tf_pre_2_2_0 = is_module_satisfies("tensorflow < 2.2.0")


# Exclude from data collection:
#  - development headers in include subdirectory
#  - XLA AOT runtime sources
#  - libtensorflow_framework shared library (to avoid duplication)
#  - import library (.lib) files (Windows-only)
data_excludes = [
    "include",
    "xla_aot_runtime_src",
    "libtensorflow_framework.*",
    "**/*.lib",
]

print('\n'*10)
print('HOOKING')

# Under tensorflow 2.3.0 (the most recent version at the time of writing),
# _pywrap_tensorflow_internal extension module ends up duplicated; once
# as an extension, and once as a shared library. In addition to increasing
# program size, this also causes problems on macOS, so we try to prevent
# the extension module "variant" from being picked up.
#
# See pyinstaller/pyinstaller-hooks-contrib#49 for details.
excluded_submodules = ['tensorflow.python._pywrap_tensorflow_internal']


def _submodules_filter(x):
    return x not in excluded_submodules


if tf_pre_1_15_0:
    # 1.14.x and earlier: collect everything from tensorflow
    hiddenimports = collect_submodules('tensorflow',
                                       filter=_submodules_filter)
    datas = collect_data_files('tensorflow', excludes=data_excludes)
elif tf_post_1_15_0 and tf_pre_2_2_0:
    # 1.15.x - 2.1.x: collect everything from tensorflow_core
    hiddenimports = collect_submodules('tensorflow_core',
                                       filter=_submodules_filter)
    datas = collect_data_files('tensorflow_core', excludes=data_excludes)

    # Under 1.15.x, we seem to fail collecting a specific submodule,
    # and need to add it manually...
    if tf_post_1_15_0 and tf_pre_2_0_0:
        hiddenimports += \
            ['tensorflow_core._api.v1.compat.v2.summary.experimental']
else:
    # 2.2.0 and newer: collect everything from tensorflow again
    hiddenimports = collect_submodules('tensorflow',
                                       filter=_submodules_filter)
    datas = collect_data_files('tensorflow', excludes=data_excludes)

    # From 2.6.0 on, we also need to explicitly collect keras (due to
    # lazy mapping of tensorflow.keras.xyz -> keras.xyz)
    if is_module_satisfies("tensorflow >= 2.6.0"):
        hiddenimports += collect_submodules('keras')

excludedimports = excluded_submodules

# Suppress warnings for missing hidden imports generated by this hook.
# Requires PyInstaller > 5.1 (with pyinstaller/pyinstaller#6914 merged); no-op otherwise.
warn_on_missing_hiddenimports = False


a = Analysis(['src/Polo.py'],
             pathex=[cur_dir],
             binaries=[],
             datas=[('src/data', 'data/'), ('src/astor', 'astor/'),
                    ('src/unrar', 'unrar/'), ('src/templates', 'templates/'),
                    pptx_depends] + datas,
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