import matplotlib.pyplot as plt
import numpy as np
import math


class StrokePoint:
    def __init__(self, pos, eocLabel=0, bowLabel=0, charLabel=0):
        self.pos = np.array(pos)
        self.eocLabel = eocLabel
        self.bowLabel = bowLabel
        self.charLabel = charLabel


class Stroke:

    def __init__(self, strokePoints):
        self.points = strokePoints

    def computeLength(self):
        length = 0
        lastPoint = None
        for point in self.points:
            if lastPoint is not None:
                delta = point.pos - lastPoint.pos
                segmentLength = math.sqrt(delta[0]*delta[0]+delta[1]*delta[1])
                length += segmentLength

            lastPoint = point

        return length


class StrokesGraph:
    def __init__(self):
        self.strokes = dict()
        self.strokeOrder = list()
        self.nextStrokeId = 1
        pass

    def getStroke(self, strokeId):
        return self.strokes.get(strokeId)

    def addStroke(self, strokePoints):
        newStrokeId = self.nextStrokeId
        self.nextStrokeId += 1
        self.strokes[newStrokeId] = Stroke(strokePoints)
        self.strokeOrder.append(newStrokeId)
        return newStrokeId

    def plot(self, fmt_lines='-', fmt_dots='.', colored=True):
        #for nodeId, node in self.nodes.items():
        #    plt.plot([node.x], [node.y], fmt_dots)
        #print("plotting")
        col = 0.0
        for strokeId in self.strokeOrder:
            #print(strokeId)
            stroke = self.getStroke(strokeId)
            col += 1.0 / len(self.strokeOrder)
            xCoords = list()
            yCoords = list()
            for strokePoint in stroke.points:
                xCoords.append(strokePoint.pos[0])
                yCoords.append(strokePoint.pos[1])
                #print(strokePoint.pos)

            colR = min(col, 1.0)
            colG = min(col, 1.0)
            colB = max(1.0-col, 0.0)
            if not colored:
                colR = colG = colB = 0.0
            plt.plot(xCoords, yCoords, fmt_lines, color=(0.9, 0.9, 0.9))
            plt.plot(xCoords, yCoords, fmt_dots, color=(colR, colG, colB))
            #print(stroke.points)

    def sort(self, sortingKey=lambda stroke: stroke.points[-1].pos[0]):
        # Make sure the individual strokes start left and end right
        for strokeId, stroke in self.strokes.items():
            if len(stroke.points) < 2:
                continue
            startNode = stroke.points[0]
            endNode = stroke.points[-1]

            reverse = False
            if startNode.pos[0] > endNode.pos[0]:
                reverse = True
            elif startNode.pos[0] == endNode.pos[0]:
                if startNode.pos[1] > endNode.pos[1]:
                    reverse = True
                elif startNode.pos[1] == startNode.pos[1]:
                    if stroke.points[1].pos[0] > stroke.points[-2].pos[0]:
                        reverse = True
                    elif stroke.points[1].pos[0] == stroke.points[-2].pos[0]:
                        if stroke.points[1].pos[1] > stroke.points[-2].pos[1]:
                            reverse = True

            if reverse:
                stroke.points = list(reversed(stroke.points))

        strokeIds = list(self.strokeOrder)
        sortingKeys = [sortingKey(self.getStroke(strokeId)) for strokeId in strokeIds]

        sortedIndices = np.argsort(sortingKeys)
        sortedStrokeIds = np.array(strokeIds)[sortedIndices]
        
        self.strokeOrder = sortedStrokeIds


    def checkForConsistency(self):
        pass
