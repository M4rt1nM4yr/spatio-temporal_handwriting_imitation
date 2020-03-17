import numpy as np


def penpositions_to_text(penPositions):

    lowerBorders = penPositions[0].pos
    upperBorders = penPositions[0].pos

    for penPosition in penPositions:
        lowerBorders = np.minimum(lowerBorders, penPosition.pos)
        upperBorders = np.maximum(upperBorders, penPosition.pos)

    lowerBorders = lowerBorders.astype(int)
    upperBorders = upperBorders.astype(int)

    imgOffset = 5 - lowerBorders
    imgSize = 10 + upperBorders - lowerBorders

    result = str(imgSize[0]) + " " + str(imgSize[1]) + "\n\n"

    for penPosition in penPositions:

        pos = penPosition.pos + imgOffset
        result += str(pos[0]) + " " + str(pos[1]) + "\n"

        if penPosition.penUp > 0.5:
            result += "\n"

    return result
