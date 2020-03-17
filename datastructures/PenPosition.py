import numpy as np
import matplotlib.pyplot as plt


class PenPosition:

    def __init__(self, pX, pY, penUp, charLabel, eocLabel, bowLabel):
        self.pos = np.array([pX, pY])
        self.penUp = penUp
        self.charLabel = charLabel
        self.eocLabel = eocLabel
        self.bowLabel = bowLabel

    def __str__(self):
        result = "(%.2f, %.2f)" % (self.pos[0], self.pos[1])
        result += ' - ' + ('1' if self.penUp else '0')
        result += '\t' + str(self.charLabel)
        result += '\t' + str(self.eocLabel)
        result += '\t' + str(self.bowLabel)
        return result


def plotPenPositions(penPositions):

    xCoords = list()
    yCoords = list()
    for i, pos in enumerate(penPositions):
        xCoords.append(pos.pos[0])
        yCoords.append(pos.pos[1])

        if pos.penUp:
            col = float(i) / len(penPositions)
            colR = min(col, 1.0)
            colG = min(col, 1.0)
            colB = max(1.0 - col, 0.0)
            plt.plot(xCoords, yCoords, 'k.-', color=(colR, colG, colB))
            xCoords = list()
            yCoords = list()

    if xCoords:
        plt.plot(xCoords, yCoords, 'k.-', color=(1.0, 1.0, 0.0))
