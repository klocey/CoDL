from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import axes3d
import numpy as np
import sys

def sample_spherical(npoints, ndim=3):
    vec = np.random.randn(ndim, npoints)
    vec /= np.linalg.norm(vec, axis=0)
    return vec


phi = np.linspace(0, np.pi, 20)
theta = np.linspace(0, 2 * np.pi, 40)
x = np.outer(np.sin(theta), np.cos(phi)) * 180
y = np.outer(np.sin(theta), np.sin(phi)) * 180
z = np.outer(np.cos(theta), np.ones_like(phi)) * 90

xi, yi, zi = sample_spherical(10)

xi = xi * 180
yi = yi * 180
zi = zi * 90

print xi

fig, ax = plt.subplots(1, 1, subplot_kw={'projection':'3d', 'aspect':'equal'})
ax.plot_wireframe(x, y, z, color='0.7')
ax.scatter(xi, yi, zi, s=100, c='r', zorder=10)

plt.show()