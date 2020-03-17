from .cppcode import deblur_skeleton as deblur_skeleton_impl

import numpy as np

from scipy import ndimage


def deblur_skeleton(img):
    gaussian = np.zeros((5, 5))
    gaussian[2, 2] = 1.0
    gaussian = ndimage.gaussian_filter(gaussian, 0.3, mode='nearest') * 0.3
    return deblur_skeleton_impl((255-np.asarray(img))/255, gaussian)
