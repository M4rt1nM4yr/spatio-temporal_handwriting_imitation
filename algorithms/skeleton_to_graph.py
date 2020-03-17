import matplotlib.pyplot as plt

import numpy as np

from algorithms.resolve_strokes import resolve_strokes

from enum import Enum

from datastructures.EuclideanGraph import EuclideanGraph


def find_connected_triangle_groups(skeleton):
    # The triangle direction
    class TriangleDirection(Enum):
        BR = [False, True, True, True]
        BL = [True, False, True, True]
        TR = [True, True, False, True]
        TL = [True, True, True, False]

    allTriangleSquares = {}

    # Find all squares that contain 1 or 4 triangles
    for y, line in enumerate(skeleton):
        for x, hasSkeleton in enumerate(line):
            if not hasSkeleton:
                continue

            # [ Left, Right, Top, Bottom ]
            connection = [False, False, False, False]

            # check for horizontal connection
            foundHorizontalConnection = False
            for cid, dx in enumerate([-1, 1]):
                other_line = line
                other_x = x + dx
                if other_x < 0 or other_x >= len(other_line):
                    continue
                other_hasSkeleton = other_line[other_x]
                if other_hasSkeleton:
                    foundHorizontalConnection = True
                    connection[cid] = True

            if not foundHorizontalConnection:
                continue

            # check for vertical connection
            foundVerticalConnection = False
            for cid, dy in enumerate([-1, 1]):
                other_y = y + dy
                if other_y < 0 or other_y >= len(skeleton):
                    continue
                other_line = skeleton[other_y]
                other_x = x
                other_hasSkeleton = other_line[other_x]
                if other_hasSkeleton:
                    foundVerticalConnection = True
                    connection[cid+2] = True

            if not foundVerticalConnection:
                continue

            # Found a triangle corner!
            # Checking which triangle(s) it belongs to ...
            for c0, c1, dx, dy, triangleDirection in [
                (0, 2, -1, -1, TriangleDirection.BR),
                (1, 2, 0, -1, TriangleDirection.BL),
                (0, 3, -1, 0, TriangleDirection.TR),
                (1, 3, 0, 0, TriangleDirection.TL),
            ]:
                if connection[c0] and connection[c1]:
                    quadPos = (x + dx, y + dy)
                    if quadPos not in allTriangleSquares:
                        allTriangleSquares[quadPos] = {triangleDirection}
                    else:
                        allTriangleSquares.get(quadPos).add(triangleDirection)

    # Connect squares to groups
    squareGroups = []
    processedSquarePositions = set()

    # print('[%.2f] Processing triangle squares ...' % (time.time() - t0))

    # recursive helper functions
    def processTriangleSquare(currentSquarePosition, groupId=None):
        if currentSquarePosition in processedSquarePositions:
            return

        if groupId is None:
            squareGroups.append([currentSquarePosition])
            groupId = len(squareGroups) - 1
        else:
            squareGroups[groupId].append(currentSquarePosition)

        processedSquarePositions.add(currentSquarePosition)

        currentSquareTriangleDirections = allTriangleSquares.get(currentSquarePosition)

        checkDirections = [
            ({TriangleDirection.TR, TriangleDirection.BR}, (+1, 0), {TriangleDirection.TL, TriangleDirection.BL}),
            ({TriangleDirection.TL, TriangleDirection.BL}, (-1, 0), {TriangleDirection.TR, TriangleDirection.BR}),
            ({TriangleDirection.BR, TriangleDirection.BL}, (0, +1), {TriangleDirection.TR, TriangleDirection.TL}),
            ({TriangleDirection.TR, TriangleDirection.TL}, (0, -1), {TriangleDirection.BR, TriangleDirection.BL}),
        ]

        # Check all directions for touching triangles
        for checkDirection in checkDirections:
            if not currentSquareTriangleDirections.intersection(checkDirection[0]):
                continue

            neighborPosition = (
                currentSquarePosition[0] + checkDirection[1][0],
                currentSquarePosition[1] + checkDirection[1][1],
            )

            if neighborPosition in processedSquarePositions:
                continue
            if neighborPosition not in allTriangleSquares:
                continue

            # If we are here, we found a neighbor square that contains a touching triangle
            # that has not been processed yet. Now, recursively process it.
            processTriangleSquare(neighborPosition, groupId)

    for nextSquarePosition in allTriangleSquares:
        processTriangleSquare(nextSquarePosition)

    # Compute all points in triangle squares
    triangleGroups = []
    for squareGroup in squareGroups:
        triangleGroup = set()
        # Iterate through all squares in square group
        for squarePos in squareGroup:

            # Compute which of the four points in the square are important
            triangleDirections = allTriangleSquares.get(squarePos)
            importantPointsInSquare = [False, False, False, False]
            for triangleDirection in triangleDirections:
                importantPointsInSquare = np.logical_or(importantPointsInSquare, triangleDirection.value)

            for pointId, offset in enumerate([(0, 0), (1, 0), (0, 1), (1, 1)]):
                if not importantPointsInSquare[pointId]:
                    continue
                pointPosition = (squarePos[0] + offset[0], squarePos[1] + offset[1])
                triangleGroup.add(pointPosition)

        triangleGroups.append(triangleGroup)

    return triangleGroups


def skeleton_to_graph(skeleton, figure=None):

    # t0 = time.time()

    graph = EuclideanGraph()

    # print('[%.2f] Building graph ...' % (time.time() - t0))
    # Create full graph of all connected pixels
    for y, line in enumerate(skeleton):
        for x, hasSkeleton in enumerate(line):
            if not hasSkeleton:
                continue

            node = graph.createNode(x, y)

            for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                other_y = y + dy
                if other_y < 0 or other_y >= len(skeleton):
                    continue
                other_line = skeleton[other_y]
                other_x = x + dx
                if other_x < 0 or other_x >= len(other_line):
                    continue
                other_hasSkeleton = other_line[other_x]
                if other_hasSkeleton:
                    node.connectedNodes.add((other_x, other_y))

    if figure:
        plt.figure(figure.number)
        imShape = np.shape(skeleton)
        if imShape[0] > imShape[1]:
            plt.subplot(1, 2, 1)
        else:
            plt.subplot(2, 1, 1)

        plt.imshow(skeleton, cmap='binary', vmax=10)
        plt.gca().axes.get_xaxis().set_visible(False)
        plt.gca().axes.get_yaxis().set_visible(False)
        # plt.xticks([0, 2, 4, 6, 8])
        graph.plot()

    # print('[%.2f] Finding connected groups ...' % (time.time() - t0))
    # Check for triangles
    triangleGroups = find_connected_triangle_groups(skeleton)

    # print('[%.2f] Replacing groups ...' % (time.time() - t0))
    for triangleGroup in triangleGroups:

        # connect all group nodes that are connected to nodes outside the group
        connectedToOutsiders = set()
        for nodePos in triangleGroup:
            node = graph.getNode(nodePos)

            for connectedNodePos in node.connectedNodes:
                if connectedNodePos not in triangleGroup:
                    connectedToOutsiders.add(nodePos)
                    break

        # compute new node, by averaging all other nodes
        newNodeX = 0
        newNodeY = 0
        for nodePos in triangleGroup:
            newNodeX += nodePos[0]
            newNodeY += nodePos[1]
        newNodeX /= len(triangleGroup)
        newNodeY /= len(triangleGroup)
        newNodePos = (newNodeX, newNodeY)

        # remove all nodes that are not connected to the outside
        for nodePos in triangleGroup:
            if nodePos not in connectedToOutsiders:
                graph.removeNode(nodePos)

        # create new center node
        if not graph.nodeExists(newNodePos):
            graph.createNode(newNodeX, newNodeY)
        newNode = graph.getNode(newNodePos)

        # remove all connections between the outsider nodes
        for nodePos in connectedToOutsiders:
            if nodePos == newNodePos:
                continue
            node = graph.getNode(nodePos)
            node.connectedNodes -= connectedToOutsiders
            node.connectedNodes.add(newNodePos)
            newNode.connectedNodes.add(nodePos)

    if figure:
        plt.figure(figure.number)
        imShape = np.shape(skeleton)
        if imShape[0] > imShape[1]:
            plt.subplot(1, 2, 2)
        else:
            plt.subplot(2, 1, 2)
        plt.imshow(skeleton, cmap='binary', vmax=10)
        # plt.xticks([0, 2, 4, 6, 8])
        graph.plot()
        plt.gca().axes.get_xaxis().set_visible(False)
        plt.gca().axes.get_yaxis().set_visible(False)

    # print('[%.2f] Checking for consistency ...' % (time.time() - t0))
    graph.checkForConsistency()
    # print('[%.2f] Done.' % (time.time() - t0))
    return graph


def main():
    skeleton = np.array([
        [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
        [0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0],
        [0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0],
        [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0],
        [0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0],
        [0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0],
        [1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1],
        [0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0],
        [0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0],
        [0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1],
        [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
        [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
    ]).astype(bool)

    figure0 = plt.figure('Skeleton Graph')
    graph = skeleton_to_graph(skeleton, figure0)

    figure1 = plt.figure('Resolved')

    graph = resolve_strokes(graph)
    plt.imshow(skeleton, cmap='binary', vmax=10)
    graph.plot()



    plt.show()


if __name__ == "__main__":
    main()
