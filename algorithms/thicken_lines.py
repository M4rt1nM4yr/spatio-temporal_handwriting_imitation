
import numpy as np

from scipy.ndimage import morphology


def thicken_lines(img, lineWidth):
    lineWidth = int(lineWidth // 2)
    stencil = np.zeros((2*lineWidth+1, 2*lineWidth+1), dtype=np.uint8)
    for y in range(stencil.shape[0]):
        pY = y - lineWidth
        for x in range(stencil.shape[1]):
            pX = x - lineWidth
            if pX*pX+pY*pY <= lineWidth*lineWidth:
                stencil[y, x] = 1

    while len(stencil.shape) < len(img.shape):
        stencil = np.expand_dims(stencil, axis=2)

    morphedArray = morphology.binary_dilation(img, structure=stencil)
    return morphedArray
