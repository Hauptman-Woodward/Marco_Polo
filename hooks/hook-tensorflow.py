from PyInstaller.utils.hooks import collect_all, collect_submodules

# Collect all TensorFlow modules
hiddenimports = collect_submodules('tensorflow')

# Collect all TensorFlow core modules
hiddenimports += collect_submodules('tensorflow_core')

# Collect Keras modules
hiddenimports += collect_submodules('keras')

# Add additional common dependencies
hiddenimports += [
    'astor',
    'termcolor',
    'wrapt',
    'gast',
    'h5py',
    'absl',
    'tensorboard',
    'tensorflow_estimator',
]

# Collect all TensorFlow data
datas, binaries, _ = collect_all('tensorflow')

# Collect all TensorFlow core data
datas_core, binaries_core, _ = collect_all('tensorflow_core')
datas += datas_core
binaries += binaries_core
