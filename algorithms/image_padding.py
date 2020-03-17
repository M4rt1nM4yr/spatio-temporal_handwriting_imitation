from PIL import Image
from skimage.util import pad
import numpy as np

from utils.math import findSmallestMultipleOf


def pad_image(img, paddingBase=(256, 256)):

    if isinstance(paddingBase, int):
        paddingBase = (paddingBase, paddingBase)

    imgWidth, imgHeight = img.size

    wantedWidth = findSmallestMultipleOf(imgWidth, paddingBase[0])
    wantedHeight = findSmallestMultipleOf(imgHeight, paddingBase[1])

    missingWidth = wantedWidth - imgWidth
    missingHeight = wantedHeight - imgHeight

    padLeft = missingWidth // 2
    padTop = missingHeight // 2
    padRight = missingWidth - padLeft
    padBottom = missingHeight - padTop
    unpadArgs = (padLeft, padTop, padLeft+imgWidth, padTop+imgHeight)

    imgArray = np.asarray(img)
    #print(img.size)
    #print(imgArray)
    #print(padLeft, padTop, padRight, padBottom)
    if wantedWidth != imgWidth or wantedHeight != imgHeight:
        padding = ((padTop, padBottom), (padLeft, padRight))
        if imgArray.ndim == 3:
            padding = padding + ((0, 0),)
        paddedImgArray = pad(imgArray, pad_width=padding, mode='reflect')
    else:
        paddedImgArray = imgArray

    paddedImg = Image.fromarray(paddedImgArray)

    #reconstructedImg = unpad_image(paddedImg, unpadArgs)
    #assert(np.array_equal(imgArray, np.asarray(reconstructedImg)))

    return paddedImg, unpadArgs


def unpad_image(img, paddingParams):
    if isinstance(img, np.ndarray):
        return img[paddingParams[1]:paddingParams[3], paddingParams[0]:paddingParams[2]]
    return img.crop(paddingParams)
