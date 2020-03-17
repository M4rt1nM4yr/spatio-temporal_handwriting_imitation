import numpy as np

import math
from utils.errors import error_and_draw


def getAngles(skeletonGraph, nodeId, connectedNodeIds, walkDist=1):
    angles = list()

    for connectedNodeId in connectedNodeIds:
        angle = getAngleOfPath(skeletonGraph, nodeId, connectedNodeId, maxDist=walkDist)
        angles.append(angle)
    return angles


def getNextNodeId(skeletonGraph, previousNodeId, currentNodeId):
    currentNode = skeletonGraph.getNode(currentNodeId)
    neighborNodes = currentNode.connectedNodes

    assert(previousNodeId in neighborNodes)

    if len(neighborNodes) != 2:
        return None
    for neighborNodeId in neighborNodes:
        if neighborNodeId != previousNodeId:
            return neighborNodeId


def createsCircularDependency(skeletonGraph, startNodeId, targetNodeId):
    if targetNodeId == startNodeId:
        return True

    targetNode = skeletonGraph.getNode(targetNodeId)
    startNode = skeletonGraph.getNode(startNodeId)

    if len(startNode.connectedNodes) < 1:
        error_and_draw("startNode.connectedNodes < 1", skeletonGraph)

    assert (len(targetNode.connectedNodes) >= 1)
    assert (len(startNode.connectedNodes) >= 1)

    if len(targetNode.connectedNodes) > 1:
        return False

    if len(startNode.connectedNodes) > 1:
        return False

    currentNodeId = startNodeId
    nextNodeId = list(startNode.connectedNodes)[0]
    while nextNodeId is not None:
        if nextNodeId == targetNodeId:
            return True

        previousNodeId = currentNodeId
        currentNodeId = nextNodeId
        nextNodeId = getNextNodeId(skeletonGraph, previousNodeId, currentNodeId)

    return False


def getAngleOfPath(skeletonGraph, startNodeId, directionNodeId, maxDist):
    previousNodeId = startNodeId

    for i in range(maxDist-1):
        nextNode = getNextNodeId(skeletonGraph, previousNodeId, directionNodeId)

        if nextNode is None:
            break
        previousNodeId = directionNodeId
        directionNodeId = nextNode

    connectedNode = skeletonGraph.getNode(directionNodeId)
    startNode = skeletonGraph.getNode(startNodeId)
    firstPointDirX = connectedNode.x - startNode.x
    firstPointDirY = connectedNode.y - startNode.y
    angle = math.atan2(firstPointDirY, firstPointDirX)

    return angle


def computeAnglesMatrix(angles):
    anglesMatrix = np.zeros((len(angles), len(angles)))

    anglesOffset = (len(angles)+1)//2
    assert((anglesOffset * 2) - 1 == len(angles))

    for angleId, angle0 in enumerate(angles):
        nextAngleId = (angleId + anglesOffset) % len(angles)

        angle1 = angles[nextAngleId]
        diff = abs(angle1 - angle0)
        if diff > math.pi:
            diff = 2*math.pi - diff

        anglesMatrix[angleId, nextAngleId] = diff

    return anglesMatrix


def resolve_strokes(skeletonGraph):

    # necessary to provide a mechanism for restarting the algorithm in case strokesGraph changed
    needsContinue = True
    while needsContinue:
        needsContinue = False
        for nodeId, node in skeletonGraph.nodes.items():

            if len(node.connectedNodes) <= 2:
                continue

            # Remove all nodes that only have one neighbor
            nodesToRemove = []
            for connectedNodeId in node.connectedNodes:
                connectedNode = skeletonGraph.getNode(connectedNodeId)
                if len(connectedNode.connectedNodes) < 2:
                    nodesToRemove.append(connectedNodeId)
            if nodesToRemove:
                for nodeIdToRemove in nodesToRemove:
                    skeletonGraph.removeNode(nodeIdToRemove)
                needsContinue = True
                break

            if len(node.connectedNodes) % 2 == 0:

                connectedNodeIds = list(node.connectedNodes)
                angles = getAngles(skeletonGraph, nodeId, connectedNodeIds)
                anglesOrder = np.argsort(angles)

                sortedConnectedNodeIds = [connectedNodeIds[pos] for pos in anglesOrder]

                skeletonGraph.removeNode(nodeId)

                halfLen = len(connectedNodeIds)//2
                assert(halfLen * 2 == len(connectedNodeIds))
                for i in range(halfLen):
                    if not createsCircularDependency(skeletonGraph, sortedConnectedNodeIds[i], sortedConnectedNodeIds[i+halfLen]):
                        skeletonGraph.addConnection(sortedConnectedNodeIds[i], sortedConnectedNodeIds[i+halfLen])

                needsContinue = True
                break

            if len(node.connectedNodes) % 2 == 1:
                #print("================")
                #print(nodeId)

                connectedNodeIds = list(node.connectedNodes)
                angles = getAngles(skeletonGraph, nodeId, connectedNodeIds, walkDist=2)

                anglesOrder = np.argsort(angles)
                sortedConnectedNodeIds = [connectedNodeIds[pos] for pos in anglesOrder]
                sortedAngles = [angles[pos] for pos in anglesOrder]

                anglesMatrix = computeAnglesMatrix(sortedAngles)

                #print(sortedConnectedNodeIds)
                #print(sortedAngles)

                numLeft = (len(node.connectedNodes) - 1)//2
                assert(len(connectedNodeIds) == 2*numLeft + 1)

                for _ in range(numLeft):
                    i, j = np.unravel_index(anglesMatrix.argmax(), anglesMatrix.shape)
                    #print(i, j)
                    anglesMatrix[i, :] = 0
                    anglesMatrix[j, :] = 0
                    anglesMatrix[:, i] = 0
                    anglesMatrix[:, j] = 0

                    if skeletonGraph.nodesConnected(sortedConnectedNodeIds[i], nodeId):
                        skeletonGraph.removeConnection(sortedConnectedNodeIds[i], nodeId)
                    if skeletonGraph.nodesConnected(sortedConnectedNodeIds[j], nodeId):
                        skeletonGraph.removeConnection(sortedConnectedNodeIds[j], nodeId)
                    if not createsCircularDependency(skeletonGraph, sortedConnectedNodeIds[i], sortedConnectedNodeIds[j]):
                        skeletonGraph.addConnection(sortedConnectedNodeIds[i], sortedConnectedNodeIds[j])

                needsContinue = True
                break

    skeletonGraph.checkForConsistency()

    return skeletonGraph
