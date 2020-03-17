
import numpy as np


def align(newStrokes, oldStrokes, align='left'):

    newStrokes = newStrokes.copy()

    maxPos_old = oldStrokes[0].pos
    minPos_old = oldStrokes[0].pos

    maxPos_new = newStrokes[0].pos
    minPos_new = newStrokes[0].pos

    for stroke in oldStrokes:
        maxPos_old = np.maximum(stroke.pos, maxPos_old)
        minPos_old = np.minimum(stroke.pos, minPos_old)

    for stroke in newStrokes:
        maxPos_new = np.maximum(stroke.pos, maxPos_new)
        minPos_new = np.minimum(stroke.pos, minPos_new)

    median_old = (maxPos_old + minPos_old) / 2
    median_new = (maxPos_new + minPos_new) / 2

    # size_old = maxPos_old - minPos_old
    # size_new = maxPos_new - minPos_new
    # resize = size_old[1] / size_new[1]

    moveAmt = median_old - median_new;

    for penPos in newStrokes:
        penPos.pos += moveAmt

    return newStrokes
