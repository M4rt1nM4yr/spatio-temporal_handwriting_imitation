import matplotlib.pyplot as plt
import numpy as np


class Stroke:
    def __init__(self, node1, node2, points, length):
        reverse = False

        # Always make stroke start left and end right. Consistency might help the RNN to figure out patterns.
        if node1[0] > node2[0]:
            reverse = True
        elif node1[0] == node2[0]:
            if node1[1] > node2[1]:
                reverse = True
            elif node1[1] == node2[1]:
                if points[1][0] > points[-2][0]:
                    reverse = True
                elif points[1][1] > points[-2][1]:
                    reverse = True

        if reverse:
            self.startNode = node2
            self.endNode = node1
            self.points = points[::-1]
            self.length = length
        else:
            self.startNode = node1
            self.endNode = node2
            self.points = points
            self.length = length

        self.extraData = dict()


class Node:
    def __init__(self, pos):
        self.x = pos[0]
        self.y = pos[1]
        self.strokes = list()

    def addStroke(self, stroke):
        self.strokes.append(stroke)

    def __str__(self):
        return str((self.x, self.y))


class StrokesGraph:
    def __init__(self):
        self.nodes = dict()
        self.strokes = dict()
        self.nextStrokeId = 1
        pass

    def createNode(self, pos):
        if pos in self.nodes:
            raise RuntimeError('Node ' + str(pos) + ' already exists.')
        self.nodes[pos] = Node(pos)
        return self.nodes.get(pos)

    def getNode(self, pos):
        return self.nodes.get(pos)

    def getStroke(self, strokeId):
        return self.strokes.get(strokeId)

    def addStroke(self, stroke):
        newStrokeId = self.nextStrokeId
        self.nextStrokeId += 2
        self.strokes[newStrokeId] = stroke
        return newStrokeId

    def plot(self, fmt_lines='k-', fmt_dots='k.'):
        self.checkForConsistency()
        for nodeId, node in self.nodes.items():
            plt.plot([node.x], [node.y], fmt_dots)

        col = 0.0
        for strokeId in self.sortStrokes():
            stroke = self.getStroke(strokeId)
            col += 1.0 / len(self.strokes)
            xCoords = list()
            yCoords = list()
            for x,y in stroke.points:
                xCoords.append(x)
                yCoords.append(y)

            colR = min(col, 1.0)
            colG = min(col, 1.0)
            colB = max(1.0-col, 0.0)
            plt.plot(xCoords, yCoords, fmt_lines, color=(colR, colG, colB))
            #print(stroke.points)

    def checkForConsistency(self):
        for nodeKey, node in self.nodes.items():
            if node.x != nodeKey[0] or node.y != nodeKey[1]:
                raise RuntimeError('Key ' + str(nodeKey) + ' does not match node ' + str(node) + '!')
            for strokeId in node.strokes:
                if strokeId not in self.strokes:
                    raise RuntimeError('Stroke ' + str(strokeId) + ' not in strokes list!')
                stroke = self.getStroke(strokeId)

                if nodeKey == stroke.startNode:
                    connectedNodeId = stroke.endNode
                elif nodeKey == stroke.endNode:
                    connectedNodeId = stroke.startNode
                else:
                    raise RuntimeError('Connected stroke does not reference back to us!')

                connectedNode = self.nodes.get(connectedNodeId)
                if strokeId not in connectedNode.strokes:
                    raise RuntimeError('Unidirectional connection detected between ' + str(node)
                                       + ' and ' + str(connectedNode))

    def sortStrokes(self, sortingKey=lambda stroke: stroke.endNode[0]):

        strokeIds = list(self.strokes.keys())
        sortingKeys = [sortingKey(self.getStroke(strokeId)) for strokeId in strokeIds]

        sortedIndices = np.argsort(sortingKeys)
        sortedStrokeIds = np.array(strokeIds)[sortedIndices]

        return sortedStrokeIds
