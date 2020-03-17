import math
import numpy as np

from datastructures.StrokesGraph import StrokesGraph, StrokePoint

import utils


def point_difference(p0, p1):
    dx = p0[0] - p1[0]
    dy = p0[1] - p1[1]
    return math.sqrt(dx*dx+dy*dy)


def findHighestNodeInCircle(graph, startNodeId):

    allNodesInCircle = set()

    currentNodeId = startNodeId
    currentNode = graph.getNode(currentNodeId)
    assert(len(currentNode.connectedNodes) == 2)

    maxPosY = currentNode.y
    maxPosId = currentNodeId
    allNodesInCircle.add(currentNodeId)

    nextNodeId = list(currentNode.connectedNodes)[0]

    while nextNodeId != startNodeId:
        previousNodeId = currentNodeId
        currentNodeId = nextNodeId
        currentNode = graph.getNode(currentNodeId)

        allNodesInCircle.add(currentNodeId)

        if currentNode.y > maxPosY:
            maxPosY = currentNode.y
            maxPosId = currentNodeId

        nextNodeId = nextNode(previousNodeId, currentNode)

    return maxPosId, allNodesInCircle


def nextNode(prevNodePos, currentNode):

    assert (prevNodePos in currentNode.connectedNodes)

    if len(currentNode.connectedNodes) == 1:
        return None

    assert(len(currentNode.connectedNodes) == 2)

    for node in currentNode.connectedNodes:
        if node != prevNodePos:
            return node

    raise RuntimeError("Should never happen.")


def add_all_lines_to_strokesgraph(inputGraph, outputGraph, endNodes, visitedNodes, minimumLength):

    # Iterate over all 2-ended lines
    for nodePos in endNodes:
        if nodePos in visitedNodes:
            continue

        strokeLen = 0
        strokePoints = list()

        visitedNodes.add(nodePos)
        strokePoints.append(StrokePoint(nodePos))

        currentNode = inputGraph.getNode(nodePos)
        nextPos = list(currentNode.connectedNodes)[0]

        while nextPos is not None:
            prevPos = nodePos
            nodePos = nextPos
            currentNode = inputGraph.getNode(nodePos)

            visitedNodes.add(nodePos)
            strokeLen += point_difference(strokePoints[-1].pos, nodePos)
            strokePoints.append(StrokePoint(nodePos))

            nextPos = nextNode(prevPos, currentNode)

        if strokeLen > minimumLength:
            outputGraph.addStroke(strokePoints)


def graph_to_strokes(graph, minimumLength=2):

    minConnections = float('inf');
    maxConnections = -float('inf');
    for nodePos, node in graph.nodes.items():
        minConnections = min(len(node.connectedNodes), minConnections)
        maxConnections = max(len(node.connectedNodes), maxConnections)

    # Make sure that we already did a splitting before this step.
    #print('connections: ', minConnections, maxConnections)
    #if minConnections < 1:
#        error_and_draw("Input graph should not have rogue nodes!", graph)
    assert(maxConnections <= 2), "Input graph should have a maximum node connectivity of 2!"
#    assert(minConnections >= 1), "Input graph should not have rogue nodes!"

    # Now we only have two possibilities:
    # Strokes with exactly one start and one, without any crossections, and circular strokes.
    # First, we need to process all normal strokes.
    # Then, we need to detect circular dependencies.

    # Prepare dict that stores whether we already visited a node
    endNodes = list()
    for nodePos, node in graph.nodes.items():
        if len(node.connectedNodes) == 1:
            endNodes.append(nodePos)

    # Create result graph
    strokesGraph = StrokesGraph()

    # Keep track of which nodes we already visited
    visitedNodes = set()

    # Do the actual conversion
    add_all_lines_to_strokesgraph(graph, strokesGraph, endNodes, visitedNodes, minimumLength)

    # Find circular dependencies
    nodesToBeSplit = list()
    visitedCircleNodes = set()
    for nodeId, node in graph.nodes.items():
        if nodeId in visitedCircleNodes:
            continue
        if len(node.connectedNodes) != 0 and nodeId not in visitedNodes:
            topNodeId, otherNodesInCircle = findHighestNodeInCircle(graph, nodeId)
            visitedCircleNodes.update(otherNodesInCircle)
            nodesToBeSplit.append(topNodeId)

    # Remove single items from input graph to fix circular dependencies
    for nodeId in nodesToBeSplit:
        #print(nodeId)
        graph.removeConnection(nodeId, list(graph.getNode(nodeId).connectedNodes)[0])

    # Now run algorithm again on missing lines
    add_all_lines_to_strokesgraph(graph, strokesGraph, nodesToBeSplit, visitedNodes, minimumLength)

    for nodeId, node in graph.nodes.items():
        if len(node.connectedNodes) != 0:
            utils.errors.assert_or_draw(nodeId in visitedNodes, nodeId, [graph, strokesGraph])
            #assert(nodePos in visitedNodes)


    return strokesGraph
