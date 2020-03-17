import unittest

from tests.test_data import TestData

from algorithms.sample_to_penpositions import sample_to_penpositions
from algorithms.penpositions_to_strokes import penpositions_to_strokes
from algorithms.resample_strokes import resample_strokes_smooth

import numpy as np


class TestConversions(unittest.TestCase):
    def test_resample_smooth(self):

        inputDataset = TestData.getDataset()

        for sampleId, rawSample in enumerate(inputDataset.samples[0:3]):
            sample = inputDataset.undo_preprocess(rawSample)
            penPositions = sample_to_penpositions(sample,
                                                  inputDataset.char_labels[sampleId],
                                                  inputDataset.eoc_labels[sampleId],
                                                  inputDataset.bow_labels[sampleId])
            strokes = penpositions_to_strokes(penPositions)
            strokesPython = resample_strokes_smooth(strokes, useCCode=False)
            strokesCcode = resample_strokes_smooth(strokes, useCCode=True)

            for strokePosId in range(len(strokesPython.strokeOrder)):
                strokePython = strokesPython.getStroke(strokesPython.strokeOrder[strokePosId])
                strokeCcode = strokesCcode.getStroke(strokesCcode.strokeOrder[strokePosId])
                unrolledPython = [[point.pos[0], point.pos[1]] for point in strokePython.points]
                unrolledCcode = [[point.pos[0], point.pos[1]] for point in strokeCcode.points]

                np.testing.assert_array_equal(unrolledPython, unrolledCcode);


if __name__ == '__main__':
    unittest.main()
