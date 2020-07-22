import pylab as plt

# Load the image
img = plt.imread("lena512color.tiff")

# Grid lines at these intervals (in pixels)
# dx and dy can be different
dx, dy = 100,100

# Custom (rgb) grid color
grid_color = [0,0,0]

# Modify the image to include the grid
img[:,::dy,:] = grid_color
img[::dx,:,:] = grid_color

# Show the result
plt.imshow(img)
plt.show()