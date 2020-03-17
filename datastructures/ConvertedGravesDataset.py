import numpy as np

from ext.deepwriting import preprocessing
import os

class ConvertedGravesDataset:

    def __init__(self):
        self.outputDataset = dict()
        self.outputDataset['samples'] = list()
        self.outputDataset['texts'] = list()

    def addSample(self, penPositions, textContent):
        stroke = list()
        for penPosition in penPositions:
            stroke.append([penPosition.pos[0], penPosition.pos[1], penPosition.penUp])

        stroke = np.array(stroke, dtype='f4')

        self.outputDataset.get('samples').append(stroke)
        self.outputDataset.get('texts').append(textContent)

    def save(self, filename):
        dirname = os.path.dirname(filename)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        np.savez_compressed(filename, **self.outputDataset)
