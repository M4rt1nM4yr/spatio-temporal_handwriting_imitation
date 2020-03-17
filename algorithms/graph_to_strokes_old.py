import math
from datastructures.StrokesGraphOld import StrokesGraph, Stroke


def point_difference(p0, p1):
    dx = p0[0] - p1[0]
    dy = p0[1] - p1[1]
    return math.sqrt(dx*dx+dy*dy)


def graph_to_strokes(graph, minimumLength=2):

    strokesGraph = StrokesGraph()

    # Collect all connector nodes, meaning nodes with != 2 neighbors. This includes nodes with 1 or 0 neighbors.
    for nodePos, node in graph.nodes.items():
        if len(node.connectedNodes) != 2:
            strokesGraph.createNode(nodePos)

    # Prepare dict that stores whether we already visited a node
    visitedNodes = dict()
    for nodePos in graph.nodes:
        visitedNodes[nodePos] = set()

    # Add strokes
    for nodePos, node in graph.nodes.items():
        if len(node.connectedNodes) == 2:
            continue
        strokesGraphNode = strokesGraph.getNode(nodePos)

        # Create strokes from all neighbors that we havent visited yet
        ourVisitedNodesCounter = visitedNodes.get(nodePos)
        for neighborPos in node.connectedNodes:
            if neighborPos in ourVisitedNodesCounter:
                continue
            ourVisitedNodesCounter.add(neighborPos)

            # Initialize stroke data
            strokePoints = [nodePos, neighborPos]
            strokeLength = point_difference(nodePos, neighborPos)

            previousPoint = nodePos
            currentPoint = neighborPos
            currentPointNode = graph.getNode(currentPoint)
            while len(currentPointNode.connectedNodes) == 2:
                possibleNextPoints = list(currentPointNode.connectedNodes)
                nextPoint = possibleNextPoints[0]
                if nextPoint == previousPoint:
                    nextPoint = possibleNextPoints[1]

                # move to the next point
                previousPoint = currentPoint
                currentPoint = nextPoint
                currentPointNode = graph.getNode(currentPoint)

                # append point to stroke
                strokePoints.append(currentPoint)
                strokeLength += point_difference(currentPoint, previousPoint)

            # Prevent stroke from getting traversed twice
            visitedNodes.get(currentPoint).add(previousPoint)

            # Ignore strokes that are just too short
            if strokeLength < minimumLength:
                continue

            stroke = Stroke(nodePos, currentPoint, strokePoints, strokeLength)
            strokeId = strokesGraph.addStroke(stroke)
            strokesGraphNode.addStroke(strokeId)
            strokesGraph.getNode(currentPoint).addStroke(strokeId)

    strokesGraph.checkForConsistency()

    return strokesGraph
