
from algorithms.skeleton_to_graph import skeleton_to_graph
from algorithms.resolve_strokes import resolve_strokes
from algorithms.graph_to_strokes import graph_to_strokes
from algorithms.resample_strokes import resample_strokes_smooth, resample_strokes_constant
from algorithms.strokes_to_penpositions import strokes_to_penpositions

import numpy as np

import matplotlib.pyplot as plt

from PIL import Image


def sample_to_penpositions(img, sortBy='mean'):

    img = np.asarray(img) > 0.5

    # Create a graph out of the skeleton image
    graph = skeleton_to_graph(img)

    DRAW_STEPS = False
    if DRAW_STEPS:
        print("Drawing ...")
        figure = plt.figure("Graphs")
        plt.subplot(4, 1, 1)
        plt.imshow(img, cmap='binary', vmax=10)
        graph.plot()
        print("Computing ...")
        #plt.show()

    # Resolves crossections
    resolve_strokes(graph)

    # Creates strokes from the graph
    strokes = graph_to_strokes(graph)

    # Sort the strokes
    if sortBy == 'first':
        sortingKey = lambda stroke: stroke.points[0].pos[0]
    elif sortBy == 'last':
        sortingKey = lambda stroke: stroke.points[-1].pos[0]
    elif sortBy == 'leftmost':
        sortingKey = lambda stroke: min([point.pos[0] for point in stroke.points])
    elif sortBy == 'rightmost':
        sortingKey = lambda stroke: max([point.pos[0] for point in stroke.points])
    elif sortBy == 'mean':
        sortingKey = lambda stroke: np.mean([point.pos[0] for point in stroke.points])
    else:
        raise ValueError(sortBy + " is not a valid sorting key")

    strokes.sort(sortingKey=sortingKey)

    # Resample the strokes smoothly, emulating pen acceleration and deceleration
    smoothStrokes = resample_strokes_smooth(strokes)

    if DRAW_STEPS:
        print("Drawing 2 ...")
        plt.subplot(4, 1, 2)
        plt.imshow(img, cmap='binary', vmax=10)
        graph.plot()
        plt.subplot(4, 1, 3)
        plt.imshow(img, cmap='binary', vmax=10)
        strokes.plot()
        plt.subplot(4, 1, 4)
        plt.imshow(img, cmap='binary', vmax=10)
        smoothStrokes.plot()
        plt.show()
        exit(1)

    # Create penpositions from strokes
    fakePenPositions = strokes_to_penpositions(smoothStrokes)

    return fakePenPositions


def main():
    skeleton = np.asarray(Image.open('../../latex/thesis/assets/sampling/sampling/a03-218z-05-crop2.png')) < 0.5
    print(skeleton)

    figure0 = plt.figure('Skeleton Graph')
    graph = skeleton_to_graph(skeleton, figure0)

    graph = resolve_strokes(graph)

    # Creates strokes from the graph
    strokes = graph_to_strokes(graph)

    # Sort the strokes
    strokes.sort()

    # Resample the strokes smoothly, emulating pen acceleration and deceleration
    smoothStrokes = resample_strokes_smooth(strokes)
    constantStrokes = resample_strokes_constant(strokes, 2.5)


    imShape = np.shape(skeleton)
    if imShape[0] > imShape[1]:
        plt.subplot(1, 3, 3)
    else:
        plt.subplot(3, 1, 3)
    plt.imshow(skeleton, cmap='binary', vmax=10)
    graph.plot()
    plt.gca().axes.get_xaxis().set_visible(False)
    plt.gca().axes.get_yaxis().set_visible(False)

    print("Drawing 2 ...")

    plt.subplot(2, 2, 1)
    plt.imshow(skeleton, cmap='binary', vmax=100)
    graph.plot()
    plt.gca().axes.get_xaxis().set_visible(False)
    plt.gca().axes.get_yaxis().set_visible(False)

    plt.subplot(2, 2, 2)
    plt.imshow(skeleton, cmap='binary', vmax=100)
    strokes.plot(colored=False)
    plt.gca().axes.get_xaxis().set_visible(False)
    plt.gca().axes.get_yaxis().set_visible(False)

    plt.subplot(2, 2, 3)
    plt.imshow(skeleton, cmap='binary', vmax=100)
    constantStrokes.plot(colored=False)
    plt.gca().axes.get_xaxis().set_visible(False)
    plt.gca().axes.get_yaxis().set_visible(False)

    plt.subplot(2, 2, 4)
    plt.imshow(skeleton, cmap='binary', vmax=100)
    smoothStrokes.plot(colored=False)
    plt.gca().axes.get_xaxis().set_visible(False)
    plt.gca().axes.get_yaxis().set_visible(False)

    plt.show()

if __name__ == "__main__":
    main()
