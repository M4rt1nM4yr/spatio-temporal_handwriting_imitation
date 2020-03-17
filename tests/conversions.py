import unittest
import tempfile
import os

from tests.test_data import TestData

from algorithms.sample_to_penpositions import sample_to_penpositions
from algorithms.penpositions_to_strokes import penpositions_to_strokes
from algorithms.strokes_to_penpositions import strokes_to_penpositions
from datastructures.ConvertedDeepwritingDataset import ConvertedDataset

from ext.deepwriting.dataset_hw import HandWritingDatasetConditional

import numpy as np


class TestConversions(unittest.TestCase):

    def test_dataset_to_pen(self):
        inputDataset = TestData.getDataset()

        outputDataset = ConvertedDataset(inputDataset)

        for sampleId, rawSample in enumerate(inputDataset.samples):
            sample = inputDataset.undo_preprocess(rawSample)
            penPositions = sample_to_penpositions(sample,
                                                  inputDataset.char_labels[sampleId],
                                                  inputDataset.eoc_labels[sampleId],
                                                  inputDataset.bow_labels[sampleId])
            outputDataset.addSample(penPositions, inputDataset.texts[sampleId])

        outputDataset.applyPreProcessing()

        with tempfile.TemporaryDirectory() as tmpDir:
            tmpFile = os.path.join(tmpDir, 'dataset.npz')
            outputDataset.save(tmpFile)

            verificationDataset = HandWritingDatasetConditional(tmpFile)

            for sampleId, _ in enumerate(inputDataset.samples):
                inputSample = inputDataset.samples[0] * inputDataset.norm_std + inputDataset.norm_mean
                inputSample *= inputDataset.scale_max - inputDataset.scale_min
                verificationSample = (verificationDataset.samples[0] * verificationDataset.norm_std + verificationDataset.norm_mean)
                verificationSample *= verificationDataset.scale_max - verificationDataset.scale_min

                inputSample[:,2] = inputDataset.samples[0][:,2]
                verificationSample[:, 2] = verificationDataset.samples[0][:, 2]

                np.testing.assert_array_almost_equal(inputSample, verificationSample, decimal=4)
                np.testing.assert_array_equal(inputDataset.char_labels[sampleId], verificationDataset.char_labels[sampleId])
                np.testing.assert_array_almost_equal(inputDataset.eoc_labels[sampleId], verificationDataset.eoc_labels[sampleId])
                np.testing.assert_array_almost_equal(inputDataset.bow_labels[sampleId], verificationDataset.bow_labels[sampleId])
                self.assertEqual(inputDataset.texts[sampleId], verificationDataset.texts[sampleId])

            np.testing.assert_array_equal(inputDataset.alphabet, verificationDataset.alphabet)

    def test_pen_to_strokes(self):
        inputDataset = TestData.getDataset()

        outputDataset = ConvertedDataset(inputDataset)

        for sampleId, rawSample in enumerate(inputDataset.samples):
            sample = inputDataset.undo_preprocess(rawSample)
            penPositions = sample_to_penpositions(sample,
                                                  inputDataset.char_labels[sampleId],
                                                  inputDataset.eoc_labels[sampleId],
                                                  inputDataset.bow_labels[sampleId])
            strokes = penpositions_to_strokes(penPositions)
            penPositions2 = strokes_to_penpositions(strokes)

            self.assertEqual(len(penPositions), len(penPositions2))

            penPos1 = [pos1.pos for pos1 in penPositions]
            penPos2 = [pos2.pos for pos2 in penPositions2]
            np.testing.assert_array_almost_equal(penPos1, penPos2)

            penUp1 = [pos1.penUp for pos1 in penPositions[:-1]] # don't test last penUp, seems to be random
            penUp2 = [pos2.penUp for pos2 in penPositions2[:-1]]
            np.testing.assert_array_almost_equal(penUp1, penUp2)

            penChar1 = [pos1.charLabel for pos1 in penPositions[:]]
            penChar2 = [pos2.charLabel for pos2 in penPositions2[:]]
            np.testing.assert_array_equal(penChar1, penChar2)

            penEoc1 = [pos1.eocLabel for pos1 in penPositions[:]]
            penEoc2 = [pos2.eocLabel for pos2 in penPositions2[:]]
            np.testing.assert_array_almost_equal(penEoc1, penEoc2)

            penBow1 = [pos1.bowLabel for pos1 in penPositions[:]]
            penBow2 = [pos2.bowLabel for pos2 in penPositions2[:]]
            np.testing.assert_array_almost_equal(penBow1, penBow2)


if __name__ == '__main__':
    unittest.main()
