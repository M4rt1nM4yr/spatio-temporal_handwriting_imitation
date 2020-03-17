

import random

from PIL import Image


def randomPos(outputSize, inputSize):

    if outputSize > inputSize:
        return random.randrange(outputSize - inputSize)
    else:
        return random.randint(outputSize - inputSize, 0)


def generateCutOffset(outputSize, inputSize):

    result = []
    for s1, s2 in zip(outputSize, inputSize):
        result.append(randomPos(s1, s2))

    return tuple(result)


def cutImageWithOffset(outputSize, image, cutOffset):
    newImage = Image.new('RGB', outputSize, (255, 255, 255))
    newImage.paste(image, cutOffset)
    return newImage


def cutSingleImage(outputSize, image):
    cutOffset = generateCutOffset(outputSize, image.size)
    return cutImageWithOffset(outputSize, image, cutOffset)


def cutAndJoinDualImages(outputSize, imageA, imageB, unaligned=False):
    if not unaligned:
        assert(imageA.size == imageB.size)

    cutOffsetA = generateCutOffset(outputSize, imageA.size)
    if unaligned:
        cutOffsetB = generateCutOffset(outputSize, imageB.size)
    else:
        cutOffsetB = cutOffsetA

    cutA = cutImageWithOffset(outputSize, imageA, cutOffsetA)
    cutB = cutImageWithOffset(outputSize, imageB, cutOffsetB)

    newImage = Image.new('RGB', (outputSize[0]*2, outputSize[1]), (255, 255, 255))
    newImage.paste(cutA, (0, 0))
    newImage.paste(cutB, (outputSize[0], 0))

    return newImage

