import matplotlib.pyplot as plt
import numpy as np


total_images = 1536 * 8 * 2

rand_vals = np.random.rand(156, 156)
ax = plt.imshow(rand_vals)
ax.set_cmap('Spectral')

ax.axes.xaxis.set_visible(False)
ax.axes.yaxis.set_visible(False)

plt.show()