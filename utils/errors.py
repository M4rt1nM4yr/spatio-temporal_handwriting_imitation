import matplotlib.pyplot as plt
import traceback


def error_and_draw(message, plotableObjects):

    print("Message: ", message)

    figure = plt.figure("ERROR!")

    if isinstance(plotableObjects, list):

        for plotId, plotableObject in enumerate(plotableObjects):
            plt.subplot(len(plotableObjects), 1, plotId+1)
            plotableObject.plot()
            plt.gca().set_aspect('equal')
            plt.gca().invert_yaxis()
    else:

        plotableObjects.plot()
        plt.gca().set_aspect('equal')
        plt.gca().invert_yaxis()

    plt.show()
    exit(1)


def assert_or_draw(checkValue, message, plotableObjects):

    if not checkValue:
        traceback.print_stack()
        error_and_draw(message, plotableObjects)
