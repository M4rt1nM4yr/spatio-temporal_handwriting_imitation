import numpy as np
from PIL import Image, ImageDraw


def penpositions_to_skeletonimages_without_metadata(penPositions, imgOffset=None, imgSize=None):

    lowerBorders = penPositions[0].pos
    upperBorders = penPositions[0].pos

    for penPosition in penPositions:
        lowerBorders = np.minimum(lowerBorders, penPosition.pos)
        upperBorders = np.maximum(upperBorders, penPosition.pos)

    lowerBorders = lowerBorders.astype(int)
    upperBorders = upperBorders.astype(int)

    if not imgOffset:
        imgOffset = 5 - lowerBorders
    if not imgSize:
        imgSize = 10 + upperBorders - lowerBorders

    strokeBitmap = Image.new('1', tuple(imgSize))

    strokeCanvas = ImageDraw.Draw(strokeBitmap)

    previousStrokePos = None
    for penPosition in penPositions:

        # print(penPosition)

        # print(stroke[:2] + imgOffset, stroke[2], char_labels[strokeId], eoc_labels[strokeId], bow_labels[strokeId], eocCounter, bowCounter)

        if previousStrokePos is not None:
            strokeCanvas.line([tuple((previousStrokePos + imgOffset).round()), tuple((penPosition.pos + imgOffset).round())], fill=1)

        if penPosition.penUp < 0.5:
            previousStrokePos = penPosition.pos
        else:
            previousStrokePos = None

    del strokeCanvas

    return strokeBitmap, (imgOffset, imgSize)


def penpositions_to_skeletonimages(penPositions, imgOffset=None, imgSize=None):

    lowerBorders = penPositions[0].pos
    upperBorders = penPositions[0].pos

    for penPosition in penPositions:
        lowerBorders = np.minimum(lowerBorders, penPosition.pos)
        upperBorders = np.maximum(upperBorders, penPosition.pos)

    lowerBorders = lowerBorders.astype(int)
    upperBorders = upperBorders.astype(int)

    if not imgOffset:
        imgOffset = 5 - lowerBorders
    if not imgSize:
        imgSize = 10 + upperBorders - lowerBorders

    strokeBitmap = Image.new('1', tuple(imgSize))
    charBitmap = Image.new('L', tuple(imgSize))
    eocBitmap = Image.new('I', tuple(imgSize))
    bowBitmap = Image.new('I', tuple(imgSize))

    strokeCanvas = ImageDraw.Draw(strokeBitmap)
    charCanvas = ImageDraw.Draw(charBitmap)
    eocCanvas = ImageDraw.Draw(eocBitmap)
    bowCanvas = ImageDraw.Draw(bowBitmap)

    eocCounter = 1
    bowCounter = 0
    currentCharLabel = 0
    currentEocLabel = 0

    previousStrokePos = None
    for penPosition in penPositions:

        # print(penPosition)

        # print(stroke[:2] + imgOffset, stroke[2], char_labels[strokeId], eoc_labels[strokeId], bow_labels[strokeId], eocCounter, bowCounter)

        if previousStrokePos is not None:
            strokeCanvas.line([tuple((previousStrokePos + imgOffset).round()), tuple((penPosition.pos + imgOffset).round())], fill=1)
            charCanvas.line([tuple((previousStrokePos + imgOffset).round()), tuple((penPosition.pos + imgOffset).round())], fill=int(currentCharLabel))
            eocCanvas.line([tuple((previousStrokePos + imgOffset).round()), tuple((penPosition.pos + imgOffset).round())], fill=int(eocCounter))
            bowCanvas.line([tuple((previousStrokePos + imgOffset).round()), tuple((penPosition.pos + imgOffset).round())], fill=int(bowCounter))

        if currentEocLabel > 0.5:
            eocCounter += 1

        currentCharLabel = penPosition.charLabel
        currentEocLabel = penPosition.eocLabel
        currentBowLabel = penPosition.bowLabel

        if currentBowLabel > 0.5:
            bowCounter += 1

        if penPosition.penUp < 0.5:
            previousStrokePos = penPosition.pos
        else:
            previousStrokePos = None

    del strokeCanvas
    del charCanvas
    del eocCanvas
    del bowCanvas

    return np.asarray(strokeBitmap), np.asarray(charBitmap), np.asarray(eocBitmap), np.asarray(bowBitmap), (
        imgOffset, imgSize)
