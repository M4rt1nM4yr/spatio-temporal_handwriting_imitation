import numpy as np

from ext.deepwriting import preprocessing


class ConvertedDeepritingDataset:

    def __init__(self, inputDataset):
        self.outputDataset = dict()
        self.outputDataset['alphabet'] = inputDataset.alphabet
        self.outputDataset['eoc_labels'] = list()
        self.outputDataset['sow_labels'] = list()
        self.outputDataset['char_labels'] = list()
        self.outputDataset['samples'] = list()
        self.outputDataset['texts'] = list()
        self.outputDataset['preprocessing'] = list()

        # Add necessary but unused data
        self.outputDataset['subject_labels'] = None
        self.outputDataset['soc_labels'] = None
        self.outputDataset['eow_labels'] = None

    def addSample(self, penPositions, textContent):
        eocLabels = list()
        bowLabels = list()
        charLabels = list()
        stroke = list()
        for penPosition in penPositions:
            eocLabels.append(penPosition.eocLabel)
            bowLabels.append(penPosition.bowLabel)
            charLabels.append(penPosition.charLabel)
            stroke.append([penPosition.pos[0], penPosition.pos[1], penPosition.penUp])

        eocLabels = np.array(eocLabels, dtype='i4')
        bowLabels = np.array(bowLabels, dtype='i4')
        charLabels = np.array(charLabels, dtype='i4')
        stroke = np.array(stroke, dtype='f4')
        # print(stroke)

        self.outputDataset.get('eoc_labels').append(eocLabels)
        self.outputDataset.get('sow_labels').append(bowLabels)
        self.outputDataset.get('char_labels').append(charLabels)
        self.outputDataset.get('samples').append(stroke)
        self.outputDataset.get('texts').append(textContent)

    def applyPreProcessing(self, validationSet=None):
        validationDataset = None
        if validationSet:
            validationDataset = validationSet.outputDataset

        preprocessing.scale_dataset(self.outputDataset, validation_data=validationDataset)

        preprocessing.translate_to_origin(self.outputDataset)
        preprocessing.convert_to_diff_representation(self.outputDataset)

        if validationDataset:
            preprocessing.translate_to_origin(validationDataset)
            preprocessing.convert_to_diff_representation(validationDataset)

        preprocessing.standardize_dataset(self.outputDataset, validation_data=validationDataset)

    def save(self, filename):
        np.savez_compressed(filename, **self.outputDataset)
