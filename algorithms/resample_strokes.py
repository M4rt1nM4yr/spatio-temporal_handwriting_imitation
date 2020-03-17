import numpy as np
import math

import matplotlib.pyplot as plt

from datastructures.StrokesGraph import StrokesGraph, StrokePoint
from . import ccode

def __pointDistance(p1, p2):
    delta = p1.pos - p2.pos
    return math.sqrt(delta[0] * delta[0] + delta[1] * delta[1])


def generateSubdivisionPoint(stroke, subDivisionPosition):
    pos1Weight, pos0 = math.modf(subDivisionPosition)
    pos0 = int(pos0)
    pos1 = pos0 + 1
    pos0Weight = 1 - pos1Weight
    np.testing.assert_almost_equal(pos0 * pos0Weight + pos1 * pos1Weight, subDivisionPosition)

    if pos0 < 0:
        pos0 = 0
    if pos1 >= len(stroke.points):
        pos1 = len(stroke.points) - 1

    # print(pos0, len(stroke.points))
    assert (pos1 >= 0)
    assert (pos0 < len(stroke.points))

    point0 = stroke.points[pos0]
    point1 = stroke.points[pos1]

    newPos = point0.pos * pos0Weight + point1.pos * pos1Weight

    additionalDataPos = pos0
    if pos0Weight < 0.5:
        additionalDataPos = pos1

    return StrokePoint(newPos,
                       stroke.points[additionalDataPos].eocLabel,
                       stroke.points[additionalDataPos].bowLabel,
                       stroke.points[additionalDataPos].charLabel)


def resample_strokes_constant(strokes, penSpeed):

    resultStrokesGraph = StrokesGraph()

    for strokeId in strokes.strokeOrder:
        stroke = strokes.getStroke(strokeId)
        strokeLength = stroke.computeLength()
        if len(stroke.points) < 2 or strokeLength == 0:
            continue
        numSubdivisions = int(round(strokeLength / penSpeed))
        if numSubdivisions < 1:
            numSubdivisions = 1

        subdivisionPointPositions = np.array(range(numSubdivisions + 1)) * strokeLength / numSubdivisions
        subdivisionPoints = list()

        previousPoint = None
        distanceSum = 0.0
        previousDistanceSum = -1.0  # important to prevent division through zero
        nextSubdivisionId = 0
        nextSubdivision = subdivisionPointPositions[nextSubdivisionId]
        for pointId, point in enumerate(stroke.points):
            if previousPoint is not None:
                previousDistanceSum = distanceSum
                distanceSum += __pointDistance(previousPoint, point)

            while distanceSum > nextSubdivision:
                # print('---\n', previousDistanceSum, nextSubdivision, distanceSum)

                # Compute sub-integer array position of the point we are searching for
                distanceStep = distanceSum - previousDistanceSum
                distanceSubstep = nextSubdivision - previousDistanceSum

                distancePct = distanceSubstep / distanceStep
                targetArrayPosition = pointId - 1 + distancePct

                # Compute the interpolated value
                subdivisionPoint = generateSubdivisionPoint(stroke, targetArrayPosition)
                subdivisionPoints.append(subdivisionPoint)

                nextSubdivisionId += 1
                if nextSubdivisionId >= len(subdivisionPointPositions):
                    break
                nextSubdivision = subdivisionPointPositions[nextSubdivisionId]

            if nextSubdivisionId >= len(subdivisionPointPositions):
                break

            previousPoint = point

        if len(subdivisionPoints) < len(subdivisionPointPositions):
            subdivisionPoints.append(generateSubdivisionPoint(stroke, len(stroke.points) - 1))

        if len(subdivisionPoints) != len(subdivisionPointPositions):
            print(len(subdivisionPoints), len(subdivisionPointPositions))
        assert (len(subdivisionPoints) == len(subdivisionPointPositions))

        resultStrokesGraph.addStroke(subdivisionPoints)

    return resultStrokesGraph


def __distanceToLine(pos, line0, line1):

    x = pos[0]
    y = pos[1]
    x1 = line0[0]
    y1 = line0[1]
    x2 = line1[0]
    y2 = line1[1]

    A = x - x1
    B = y - y1
    C = x2 - x1
    D = y2 - y1

    dot = A * C + B * D
    len_sq = C * C + D * D
    param = -1
    if len_sq != 0: # in case of 0 length line
        param = dot / len_sq

    xx = 0
    yy = 0

    if param < 0:
        xx = x1
        yy = y1
    elif param > 1:
        xx = x2
        yy = y2
    else:
        xx = x1 + param * C
        yy = y1 + param * D

    dx = x - xx
    dy = y - yy

    return math.sqrt(dx * dx + dy * dy)


def __createReachabilityMatrix(stroke, deviationThreshold):

    reachabilityMatrix = np.zeros((len(stroke.points), len(stroke.points)), dtype=bool)

    for pId0, p0 in enumerate(stroke.points):
        for pId1 in range(pId0+1, len(stroke.points)):
            p1 = stroke.points[pId1]

            # check reachability of p0 to p1

            maxDeviation = 0
            deviationSum = 0
            length = 0
            previousPos = p0
            for pId in range(pId0+1, pId1):
                pos = stroke.points[pId]
                length += __pointDistance(previousPos, pos)
                previousPos = pos

                deviation = __distanceToLine(pos.pos, p0.pos, p1.pos)
                maxDeviation = max(deviation, maxDeviation)

                deviationSum += deviation

            # We didn't look at last segment yet, so add it
            length += __pointDistance(previousPos, p1)

            dist = __pointDistance(p0, p1)

            #print(pId0, pId1, dist, length, maxDeviation, deviationSum, length/dist)

            # lots of possible heuristics, this one seems to work best
            if maxDeviation > deviationThreshold:
                break

            reachabilityMatrix[pId0, pId1] = True

    if False:
        fig = plt.figure('ReachabilityMatrix', figsize=(16, 9))
        ax = fig.add_subplot(111)
        for fromId, row in enumerate(reachabilityMatrix):
            for toId, isConnected in enumerate(row):
                if isConnected:
                    #print(fromId, toId)
                    p0 = stroke.points[fromId]
                    p1 = stroke.points[toId]
                    ax.plot([p0.pos[0],p1.pos[0]],[p0.pos[1],p1.pos[1]],'.-')
        ax.set_aspect('equal')
        plt.show()
        exit(1)

    return reachabilityMatrix


def __computeAcceleration(p0, p1, p2):
    v0 = p1-p0
    v1 = p2-p1
    acc = v1-v0
    return np.linalg.norm(acc)


def __run4DDijkstra(stroke, reachabilityMatrix, maxAcceleration):

    reachabilityMatrix[0, 0] = True

    path = np.zeros(reachabilityMatrix.shape, dtype=int) - 1
    pathLength = np.zeros(reachabilityMatrix.shape, dtype=int) - 1

    pathLength[0,0] = 0

    #print(path)
    #print(pathLength)

    # Iterate through all points
    for currentId in range(0, len(stroke.points)):
        currentPoint = stroke.points[currentId]

        # For every point, compute the optimal path for all possible outgoing speeds
        for nextId in range(currentId+1, len(stroke.points)):
            if not reachabilityMatrix[currentId, nextId]:
                continue
            #print(currentId, nextId)

            nextPoint = stroke.points[nextId]

            bestPreviousId = -1
            bestPreviousLength = -1
            for previousId, canBeReached in enumerate(reachabilityMatrix[:, currentId]):
                if not canBeReached:
                    continue
                previousPoint = stroke.points[previousId]
                acceleration = __computeAcceleration(previousPoint.pos, currentPoint.pos, nextPoint.pos)
                if acceleration > maxAcceleration:
                    continue

                # We have the current point and velocity and a previous point.
                # We now need to find the optimal solution that leads to the current point and velocity
                pathLengthToPrevious = pathLength[previousId, currentId]
                if bestPreviousLength < 0 or bestPreviousLength > pathLengthToPrevious:
                    bestPreviousLength = pathLengthToPrevious
                    bestPreviousId = previousId
                #print('\t', previousId, pathLengthToPrevious)

            #print('Best solution: ', bestPreviousId, bestPreviousLength)

            if bestPreviousId < 0:
                reachabilityMatrix[currentId, nextId] = False
            else:
                pathLength[currentId, nextId] = bestPreviousLength + 1
                path[currentId, nextId] = bestPreviousId

    bestPenultimatePointId = -1
    bestPenultimatePointLength = -1
    lastPoint = stroke.points[-1]
    lastPointId = len(stroke.points) - 1
    for pointId, pointLength in enumerate(pathLength[:,-1]):
        if not reachabilityMatrix[pointId, -1]:
            continue
        point = stroke.points[pointId]
        acceleration = __computeAcceleration(point.pos, lastPoint.pos, lastPoint.pos)
        if acceleration > maxAcceleration:
            continue

        if bestPenultimatePointLength < 0 or bestPenultimatePointLength >= pointLength:
            bestPenultimatePointLength = pointLength
            bestPenultimatePointId = pointId

    pointsReverse = [lastPointId, bestPenultimatePointId]
    while not pointsReverse[-1] == 0:
        #print(pointsReverse)
        #print(path)
        #print(np.shape(path))
        pointsReverse.append(path[pointsReverse[-1], pointsReverse[-2]])

    #print(pointsReverse)

    if False:
        fig = plt.figure('bestPath', figsize=(16, 9))

        ax = fig.add_subplot(111)

        pointsX = []
        pointsY = []
        for pointId in reversed(pointsReverse):
            # print(fromId, toId)
            p0 = stroke.points[pointId]
            pointsX.append(p0.pos[0])
            pointsY.append(p0.pos[1])
        ax.plot(pointsX, pointsY, '.-')
        ax.set_aspect('equal')
        plt.show()
        #exit(1)

    return list(reversed(pointsReverse))


## super slow
#def __run4DDijkstra(stroke, reachabilityMatrix, maxAcceleration):
#
#    targetPoint = len(stroke.points)-1
#
#    pastIds = list()
#    pastPrevs = list()
#
#    oldIds = [0]
#    oldPrevs = [-1]
#
#    pIds = [0]
#    prevs = [0]
#
#    newIds = list()
#    newPrevs = list()
#
#    while len(pIds) > 0:
#
#        for currentPosInArray, pId in enumerate(pIds):
#            prev = prevs[currentPosInArray]
#            prevPos = stroke.points[oldIds[prev]]
#            currentPos = stroke.points[pId]
#
#            for nextId, canReach in enumerate(reachabilityMatrix[pId]):
#                if not canReach:
#                    continue
#                nextPos = stroke.points[nextId]
#                acceleration = __computeAcceleration(prevPos.pos, currentPos.pos, nextPos.pos)
#                if acceleration > maxAcceleration:
#                    continue
#
#                newIds.append(nextId)
#                newPrevs.append(currentPosInArray)
#
#        pastIds.append(oldIds)
#        pastPrevs.append(oldPrevs)
#        oldIds = pIds
#        oldPrevs = prevs
#        pIds = newIds
#        prevs = newPrevs
#        newIds = list()
#        newPrevs = list()
#        print(len(pIds), np.max(pIds))
#
#        if True:
#            fig = plt.figure('currentBestPath', figsize=(16, 9))
#            argMax = np.argmax(pIds)
#            print('argMax', argMax)
#            pointIds = [pIds[argMax]]
#
#            prev = prevs[argMax]
#            pointIds.append(oldIds[prev])
#            prev = oldPrevs[prev]
#
#            print('pointIds', pointIds)
#
#            for pastId, pastPrev in zip(reversed(pastIds), reversed(pastPrevs)):
#                pointIds.append(pastId[prev])
#                prev = pastPrev[prev]
#
#            print('pointIds', pointIds)
#
#            ax = fig.add_subplot(111)
#
#            pointsX = []
#            pointsY = []
#            for pointId in pointIds:
#                # print(fromId, toId)
#                p0 = stroke.points[pointId]
#                pointsX.append(p0.pos[0])
#                pointsY.append(p0.pos[1])
#            ax.plot(pointsX, pointsY, '.-')
#            ax.set_aspect('equal')
#            plt.show()
#            #exit(1)


def resample_strokes_smooth(strokes, useCCode=True, accelerationToHeight=0.025):

    maxPos = None
    minPos = None

    for strokeId in strokes.strokeOrder:
        stroke = strokes.getStroke(strokeId)
        for point in stroke.points:
            if maxPos is None:
                maxPos = point.pos
            if minPos is None:
                minPos = point.pos

            maxPos = np.maximum(maxPos, point.pos)
            minPos = np.minimum(minPos, point.pos)

    height = maxPos[1] - minPos[1]
    acceleration = accelerationToHeight * height
    #print('acc:', acceleration)
    presamplingStepsize=acceleration/3

    resultStrokes = StrokesGraph()

    strokes = resample_strokes_constant(strokes, penSpeed=presamplingStepsize)

    for strokeId in strokes.strokeOrder:
        stroke = strokes.getStroke(strokeId)

        deviationThreshold = 3.0 * presamplingStepsize

        if useCCode:
            pathfindingResult = ccode.compute_accelerated_stroke(stroke,
                                                                 deviationThreshold=deviationThreshold,
                                                                 maxAcceleration=acceleration)
        else:
            reachabalityMatrix = __createReachabilityMatrix(stroke, deviationThreshold=deviationThreshold)
            pathfindingResult = __run4DDijkstra(stroke, reachabalityMatrix, maxAcceleration=acceleration)

        subdivisionPoints = [stroke.points[pointId] for pointId in pathfindingResult]
        resultStrokes.addStroke(subdivisionPoints)

    return resultStrokes

# --- removed, introduced a lot of ringing ---
# def filter_strokes_lowpass(strokes):
#
#    resultStrokes = StrokesGraph()
#
#    for strokeId in strokes.strokeOrder:
#        stroke = strokes.getStroke(strokeId)
#
#        posX = list([stroke.points[0].pos[0]]) * 2
#        posY = list([stroke.points[0].pos[1]]) * 2
#        for point in stroke.points:
#            posX.append(point.pos[0])
#            posY.append(point.pos[1])
#        posX.append(stroke.points[-1].pos[0])
#        posX.append(stroke.points[-1].pos[0])
#        posY.append(stroke.points[-1].pos[1])
#        posY.append(stroke.points[-1].pos[1])
#
#        fftX = np.fft.fft(posX)
#        fftY = np.fft.fft(posY)
#
#        # the actual lowpass
#        numFrequencies = int(len(fftX)/2)
#        keepFrequencies = int(numFrequencies/2)
#        print('keepFrequencies', keepFrequencies)
#        print(fftX)
#        fftX[keepFrequencies + 1:-keepFrequencies] = 0
#        fftY[keepFrequencies + 1:-keepFrequencies] = 0
#
#        print('fftX filtered:', fftX)
#
#        transformedPosX = np.fft.ifft(fftX)[2:-2]
#        transformedPosY = np.fft.ifft(fftY)[2:-2]
#
#        resultStrokePoints = list()
#        for pointId, point in enumerate(stroke.points):
#            pos = np.array([transformedPosX[pointId], transformedPosY[pointId]])
#            resultStrokePoints.append(StrokePoint(pos, point.eocLabel, point.bowLabel, point.charLabel))
#        resultStrokes.addStroke(resultStrokePoints)
#
#        print(transformedPosX)
#        print(posX[2:-2])
#
#    return resultStrokes


def analyse_strokes_acceleration(strokes):
    accelerations = list()

    maxPos = None
    minPos = None

    for strokeId in strokes.strokeOrder:
        stroke = strokes.getStroke(strokeId)
        for pointId, point in enumerate(stroke.points):
            if maxPos is None:
                maxPos = point.pos
            if minPos is None:
                minPos = point.pos

            maxPos = np.maximum(maxPos, point.pos)
            minPos = np.minimum(minPos, point.pos)


            if pointId <= 0 or pointId >= len(stroke.points) - 1:
                continue
            prevPoint = stroke.points[pointId-1]
            nextPoint = stroke.points[pointId+1]

            # approximate acceleration of point by second order discretization:
            # a[p] = (v[p+0.5] - v[p-0.5]) / dt
            # we assume constant time steps and define dt = 1
            # => a[p] = v[p+0.5]-v[p-0.5]
            # v[p] = (x[p+0.5] - x[p-0.5] / dt
            # v[p] = x[p+0.5] - x[p-0.5]
            # a[p] = v[p+0.5] - v[p-0.5] = (x[p+1] - x[p]) - (x[p] - x[p-1])
            # a[p] = x[p+1] - 2*x[p] + x[p-1]

            vFuture = nextPoint.pos - point.pos
            vPast = point.pos - prevPoint.pos
            acceleration = vFuture - vPast

            accelerationAbs = math.sqrt(acceleration[0]*acceleration[0]+acceleration[1]*acceleration[1])
            accelerations.append(accelerationAbs)

    print(minPos, maxPos)
    height = maxPos[1] - minPos[1]
    print(height)
    for i in range(len(accelerations)):
        accelerations[i] /= height

    return accelerations

